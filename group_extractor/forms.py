from django import forms

class GroupLinkForm(forms.Form):
    group_link = forms.URLField(label="WhatsApp Group Link", required=True)
