from django import forms
from django.contrib.auth.models import User, Permission, ContentType
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _

# ---------------------------
# Tailwind UI helpers
# ---------------------------
INPUT_CLS = (
    "w-full rounded-xl border border-slate-300 dark:border-slate-700 "
    "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 "
    "px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "focus:border-emerald-500"
)
CHECK_CLS = (
    "h-4 w-4 rounded border-slate-300 dark:border-slate-600 "
    "text-emerald-600 focus:ring-emerald-600"
)
RADIO_INPUT_CLS = (
    "h-4 w-4 border-slate-300 dark:border-slate-600 "
    "text-emerald-600 focus:ring-emerald-600"
)
RADIO_GROUP_CLS = "flex flex-col gap-2"  # applied on <ul> wrapper for RadioSelect


def style_text_inputs(field: forms.Field, placeholder: str | None = None):
    field.widget.attrs.setdefault("class", INPUT_CLS)
    if placeholder:
        field.widget.attrs.setdefault("placeholder", placeholder)


def style_checkbox(field: forms.Field):
    # Works for BooleanField / CheckboxInput
    field.widget.attrs.setdefault("class", CHECK_CLS)


def style_radios(field: forms.Field):
    # Works for RadioSelect; attrs are applied to each <input type="radio">
    widget = field.widget
    if isinstance(widget, forms.RadioSelect):
        widget.attrs.setdefault("class", RADIO_INPUT_CLS)  # input element
        # Small trick: add wrapper class via renderer/ul isn't needed usually,
        # but we can expose a "data-ul" class to target in CSS if desired.
        # For simplicity, rely on container layout in template.
    else:
        # If someone swaps widget accidentally, at least set base class.
        field.widget.attrs.setdefault("class", RADIO_INPUT_CLS)


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

    # remove existing perms for this model
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
        user.user_permissions.add(*to_add)


# ---------------------------
# Forms
# ---------------------------
class AdminUserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=False, label="First name")
    last_name = forms.CharField(required=False, label="Last name")
    is_superuser = forms.BooleanField(
        required=False, label="Superuser (full access)"
    )

    # Role radios
    programs_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="Programs"
    )
    news_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="News"
    )
    events_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="Events"
    )
    gallery_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="Gallery"
    )
    donations_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="Donations"
    )
    messages_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="Messages"
    )
    settings_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, initial="view", label="Site Settings"
    )

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

        # Style text inputs
        style_text_inputs(self.fields["username"], "Enter username")
        style_text_inputs(self.fields["email"], "name@example.com")
        style_text_inputs(self.fields["first_name"], "First name")
        style_text_inputs(self.fields["last_name"], "Last name")

        # Passwords
        style_text_inputs(self.fields["password1"], "New password")
        self.fields["password1"].widget.attrs.setdefault("autocomplete", "new-password")
        style_text_inputs(self.fields["password2"], "Confirm password")
        self.fields["password2"].widget.attrs.setdefault("autocomplete", "new-password")

        # Checkboxes
        style_checkbox(self.fields["is_superuser"])

        # Radios
        for key in MODULES.keys():
            style_radios(self.fields[f"{key}_perm"])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.is_staff = True  # admin access
        if commit:
            user.save()
            self.save_m2m()

            if user.is_superuser:
                # full access; no need to assign granular perms
                return user

            # granular perms
            for key in MODULES.keys():
                level = self.cleaned_data.get(f"{key}_perm", "none")
                set_module_level_perms(user, key, level)
        return user


class AdminUserUpdateForm(forms.ModelForm):
    is_active = forms.BooleanField(required=False, initial=True, label="Active")
    is_superuser = forms.BooleanField(
        required=False, label="Superuser (full access)"
    )

    programs_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="Programs"
    )
    news_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="News"
    )
    events_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="Events"
    )
    gallery_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="Gallery"
    )
    donations_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="Donations"
    )
    messages_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="Messages"
    )
    settings_perm = forms.ChoiceField(
        choices=LEVELS, widget=forms.RadioSelect, label="Site Settings"
    )

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

        # Style text inputs
        style_text_inputs(self.fields["username"], "Enter username")
        style_text_inputs(self.fields["email"], "name@example.com")
        style_text_inputs(self.fields["first_name"], "First name")
        style_text_inputs(self.fields["last_name"], "Last name")

        # Checkboxes
        style_checkbox(self.fields["is_active"])
        style_checkbox(self.fields["is_superuser"])

        # Radios
        for key in MODULES.keys():
            style_radios(self.fields[f"{key}_perm"])

        # Prefill radios based on current perms
        if self.instance and self.instance.pk:
            for key, (app_label, model) in MODULES.items():
                view_codename = f"{app_label}.view_{model}"
                add_codename = f"{app_label}.add_{model}"
                change_codename = f"{app_label}.change_{model}"
                delete_codename = f"{app_label}.delete_{model}"

                has_view = self.instance.has_perm(view_codename)
                has_add = self.instance.has_perm(add_codename)
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

            if user.is_superuser:
                # Superuser gets all, nothing else to do
                return user

            for key in MODULES.keys():
                level = self.cleaned_data.get(f"{key}_perm", "none")
                set_module_level_perms(user, key, level)
        return user


class AdminSetPasswordForm(SetPasswordForm):
    """Same behavior, but styled for Tailwind in templates."""
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        style_text_inputs(self.fields["new_password1"], "New password")
        self.fields["new_password1"].widget.attrs.setdefault("autocomplete", "new-password")
        style_text_inputs(self.fields["new_password2"], "Confirm new password")
        self.fields["new_password2"].widget.attrs.setdefault("autocomplete", "new-password")
