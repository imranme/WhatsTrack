# from django import forms

# class GroupLinkForm(forms.Form):
#     group_link = forms.URLField(label="WhatsApp Group Link", required=True)


from django import forms

class GroupLinkForm(forms.Form):
    link = forms.URLField(label="WhatsApp Group Link", widget=forms.URLInput(attrs={'placeholder': 'Enter WhatsApp group link'}))
