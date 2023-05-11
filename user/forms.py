from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CreateUserForm(UserCreationForm):
    username = forms.CharField(label='姓名', min_length=5, max_length=150)
    # email = forms.EmailField()
    email = forms.EmailField(label='Email')  
    password1 = forms.CharField(label='密碼', widget=forms.PasswordInput)  
    password2 = forms.CharField(label='確認密碼', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']