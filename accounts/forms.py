from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

from accounts.models import Role

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone')


class RoleForm(forms.Form):
    username=forms.ModelChoiceField(queryset=User.objects.all(),empty_label='--Userni tanhlan--')
    role=forms.ChoiceField(choices=Role)