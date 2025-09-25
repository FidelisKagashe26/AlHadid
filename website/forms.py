from django import forms
from website.models import ContactMessage

class ContactForm(forms.ModelForm):
    # Simple anti-bot honeypot
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "block w-full rounded-xl border-slate-300 bg-white px-4 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100",
                "placeholder": "Your full name",
                "autocomplete": "name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "block w-full rounded-xl border-slate-300 bg-white px-4 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }),
            "subject": forms.TextInput(attrs={
                "class": "block w-full rounded-xl border-slate-300 bg-white px-4 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100",
                "placeholder": "How can we help?",
            }),
            "message": forms.Textarea(attrs={
                "rows": 6,
                "class": "block w-full rounded-xl border-slate-300 bg-white px-4 py-3 text-slate-900 placeholder-slate-400 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100",
                "placeholder": "Write your message here…",
            }),
        }

    def clean_website(self):
        # If bots fill this, we silently drop
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Bot detected.")
        return ""

    def clean_message(self):
        msg = self.cleaned_data["message"].strip()
        if len(msg) < 12:
            raise forms.ValidationError("Please provide a bit more detail (12+ characters).")
        return msg
