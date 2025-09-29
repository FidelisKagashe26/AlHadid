from django import forms
from django.contrib.auth.models import User, Permission, ContentType
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm

# ---------------------------
# Tailwind UI helpers
# ---------------------------

INPUT_CLS = (
    "block w-full rounded-xl border border-slate-300 dark:border-slate-700 "
    "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 "
    "px-3 py-2 shadow-sm placeholder-slate-400 dark:placeholder-slate-500 "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
)
TEXTAREA_CLS = INPUT_CLS + " min-h-[120px]"
SELECT_CLS = (
    "block w-full rounded-xl border border-slate-300 dark:border-slate-700 "
    "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 px-3 py-2 "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
)
FILE_CLS = (
    "block w-full text-sm text-slate-700 dark:text-slate-200 "
    "file:mr-4 file:rounded-lg file:border-0 file:bg-emerald-600 file:px-3 file:py-2 "
    "file:text-white hover:file:bg-emerald-700"
)
CHECK_CLS = (
    "h-4 w-4 rounded border-slate-300 dark:border-slate-600 "
    "text-emerald-600 focus:ring-emerald-600"
)
RADIO_INPUT_CLS = (
    "h-4 w-4 border-slate-300 dark:border-slate-600 "
    "text-emerald-600 focus:ring-emerald-600"
)
RADIO_GROUP_CLS = "flex flex-col gap-2"  # tumia kwenye wrapper div/ul kwenye template

ERROR_RING_CLS = "ring-2 ring-red-500 !border-red-500 focus:ring-red-500 focus:border-red-500"

# -- tools
class AdminPasswordResetForm(PasswordResetForm):
    """
    Only allow password reset for active staff (admin) users.
    If the email doesn't match an account, raise a form error
    so no email is sent.
    """
    _matched_users = None

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("Please enter your email address.")

        qs = User._default_manager.filter(
            email__iexact=email,
            is_active=True,
            is_staff=True,     # limit to admin accounts
        )

        if not qs.exists():
            # Stop here: form invalid = no email will be sent
            raise forms.ValidationError(
                "We couldn't find an active admin account with that email."
            )

        # (Optional) handle duplicates explicitly
        if qs.count() > 1:
            raise forms.ValidationError(
                "Multiple admin accounts use this email. Please contact support."
            )

        self._matched_users = list(qs)
        return email

    def get_users(self, email):
        # Use the set we validated in clean_email so we don’t re-query.
        users = self._matched_users if self._matched_users is not None else []
        for u in users:
            if u.has_usable_password():
                yield u

def _append_class(widget: forms.Widget, extra: str):
    if not extra:
        return
    existing = widget.attrs.get("class", "")
    widget.attrs["class"] = (existing + " " + extra).strip()

def _set_placeholder(field: forms.Field, placeholder: str | None):
    if placeholder:
        field.widget.attrs.setdefault("placeholder", placeholder)

def style_field(field: forms.Field, placeholder: str | None = None):
    """
    Weka Tailwind kwa kila aina ya widget ya kawaida.
    """
    w = field.widget

    # Text-like
    if isinstance(w, (forms.TextInput, forms.EmailInput, forms.URLInput,
                      forms.NumberInput, forms.PasswordInput,
                      forms.DateInput, forms.TimeInput, forms.DateTimeInput)):
        _append_class(w, INPUT_CLS)
        _set_placeholder(field, placeholder)

    # Textarea
    elif isinstance(w, forms.Textarea):
        _append_class(w, TEXTAREA_CLS)
        _set_placeholder(field, placeholder)

    # Selects
    elif isinstance(w, (forms.Select, forms.SelectMultiple)):
        _append_class(w, SELECT_CLS)

    # File
    elif isinstance(w, (forms.FileInput, forms.ClearableFileInput)):
        _append_class(w, FILE_CLS)

    # Checkbox
    elif isinstance(w, forms.CheckboxInput):
        _append_class(w, CHECK_CLS)

    # Radios
    elif isinstance(w, forms.RadioSelect):
        # Hii class ita-apply kwenye kila <input type="radio">
        _append_class(w, RADIO_INPUT_CLS)

    else:
        # Fallback: weka angalau base input
        _append_class(w, INPUT_CLS)

def style_error_state(field: forms.Field, has_error: bool):
    if not has_error:
        return
    w = field.widget
    # Usipoteze class zilizopo—ongeza tu error classes
    _append_class(w, ERROR_RING_CLS)
    # Accessibility: aria-invalid
    w.attrs["aria-invalid"] = "true"

# ---------------------------
# Permission model mapping
# ---------------------------
# Modules => (app_label, model)
MODULES = {
    "programs": ("website", "program"),
    "news": ("website", "news"),
    "events": ("website", "event"),
    "gallery": ("website", "gallery"),
    "donations": ("website", "donationmethod"),
    "messages": ("website", "contactmessage"),
    "settings": ("website", "sitesettings"),
}

LEVELS = (
    ("none", "No Access"),
    ("view", "View Only"),
    ("edit", "Edit (add/change/delete)"),
)

def set_module_level_perms(user: User, module_key: str, level: str):
    app_label, model = MODULES[module_key]
    ct = ContentType.objects.get(app_label=app_label, model=model)
    perms = Permission.objects.filter(content_type=ct)

    # Ondoa zote za model husika kwanza
    if perms.exists():
        user.user_permissions.remove(*perms)

    if level == "view":
        p = Permission.objects.get(content_type=ct, codename=f"view_{model}")
        user.user_permissions.add(p)
    elif level == "edit":
        codenames = [
            f"view_{model}",
            f"add_{model}",
            f"change_{model}",
            f"delete_{model}",
        ]
        to_add = Permission.objects.filter(content_type=ct, codename__in=codenames)
        if to_add.exists():
            user.user_permissions.add(*to_add)

# ---------------------------
# Tailwind mixin
# ---------------------------

class TailwindFormMixin:
    """
    Ongeza Tailwind classes kwa fields zote, pamoja na error classes.
    - Inafanya kazi kwenye __init__ (initial render)
    - Pia baada ya validation (full_clean) ili error ziwe zionekane vizuri.
    """

    # placeholders unaweza override kwenye form kupitia dict hii:
    placeholders: dict[str, str] = {}

    def _tw_style_widgets(self):
        for name, field in self.fields.items():
            ph = self.placeholders.get(name)
            style_field(field, placeholder=ph)

    def _tw_apply_error_classes(self):
        if not getattr(self, "is_bound", False):
            return
        # Ikiwa form imebindika (POST) na ina errors, weka error ring
        for name, field in self.fields.items():
            style_error_state(field, has_error=name in self.errors)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # type: ignore
        self._tw_style_widgets()
        # Ikiwa tayari ime-bound (POST), weka error state endapo errors zisha-compute
        if getattr(self, "is_bound", False) and hasattr(self, "errors"):
            self._tw_apply_error_classes()

    def full_clean(self):
        # Run Django cleaning kwanza
        super().full_clean()  # type: ignore
        # Kisha tumia error classes
        self._tw_apply_error_classes()

# ---------------------------
# Forms
# ---------------------------

class AdminUserCreateForm(TailwindFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))
    first_name = forms.CharField(required=False, label=_("First name"))
    last_name = forms.CharField(required=False, label=_("Last name"))
    is_superuser = forms.BooleanField(required=False, label=_("Superuser (full access)"))

    # Role radios
    programs_perm = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("Programs"))
    news_perm     = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("News"))
    events_perm   = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("Events"))
    gallery_perm  = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("Gallery"))
    donations_perm= forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("Donations"))
    messages_perm = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("Messages"))
    settings_perm = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, initial="view", label=_("Site Settings"))

    placeholders = {
        "username": _("Enter username"),
        "email": _("name@example.com"),
        "first_name": _("First name"),
        "last_name": _("Last name"),
        "password1": _("New password"),
        "password2": _("Confirm password"),
    }

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Password autocomplete
        self.fields["password1"].widget.attrs.setdefault("autocomplete", "new-password")
        self.fields["password2"].widget.attrs.setdefault("autocomplete", "new-password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.is_staff = True  # apewe access ya admin area

        if commit:
            user.save()
            self.save_m2m()

            # Kama ni superuser, hana haja ya granular perms
            if user.is_superuser:
                return user

            # Vinginevyo, weka granular perms kwa kila module
            for key in MODULES.keys():
                level = self.cleaned_data.get(f"{key}_perm", "none")
                set_module_level_perms(user, key, level)

        return user


class AdminUserUpdateForm(TailwindFormMixin, forms.ModelForm):
    is_active = forms.BooleanField(required=False, initial=True, label=_("Active"))
    is_superuser = forms.BooleanField(required=False, label=_("Superuser (full access)"))

    programs_perm  = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("Programs"))
    news_perm      = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("News"))
    events_perm    = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("Events"))
    gallery_perm   = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("Gallery"))
    donations_perm = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("Donations"))
    messages_perm  = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("Messages"))
    settings_perm  = forms.ChoiceField(choices=LEVELS, widget=forms.RadioSelect, label=_("Site Settings"))

    placeholders = {
        "username": _("Enter username"),
        "email": _("name@example.com"),
        "first_name": _("First name"),
        "last_name": _("Last name"),
    }

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prefill radio levels kulingana na current perms
        if self.instance and self.instance.pk:
            for key, (app_label, model) in MODULES.items():
                view_codename   = f"{app_label}.view_{model}"
                add_codename    = f"{app_label}.add_{model}"
                change_codename = f"{app_label}.change_{model}"
                delete_codename = f"{app_label}.delete_{model}"

                has_view   = self.instance.has_perm(view_codename)
                has_add    = self.instance.has_perm(add_codename)
                has_change = self.instance.has_perm(change_codename)
                has_delete = self.instance.has_perm(delete_codename)

                if has_add or has_change or has_delete:
                    self.fields[f"{key}_perm"].initial = "edit"
                elif has_view:
                    self.fields[f"{key}_perm"].initial = "view"
                else:
                    self.fields[f"{key}_perm"].initial = "none"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True

        if commit:
            user.save()

            # Kama superuser, hapati granular, tayari ana full access
            if user.is_superuser:
                return user

            # Weka granular perms kwa kila module
            for key in MODULES.keys():
                level = self.cleaned_data.get(f"{key}_perm", "none")
                set_module_level_perms(user, key, level)

        return user


class AdminSetPasswordForm(TailwindFormMixin, SetPasswordForm):
    """SetPasswordForm yenye Tailwind."""
    placeholders = {
        "new_password1": _("New password"),
        "new_password2": _("Confirm new password"),
    }

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].widget.attrs.setdefault("autocomplete", "new-password")
        self.fields["new_password2"].widget.attrs.setdefault("autocomplete", "new-password")
