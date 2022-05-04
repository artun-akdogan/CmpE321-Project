from django import forms

# A form that accepts credentials and redirects user to login with that credentials.
class UserLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput)
    