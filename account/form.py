from .models import UserProfile,User
from django import forms
class UserEditForm(forms.ModelForm):
 class Meta:
   model = User
   fields = ['first_name', 'last_name', 'email']
class ProfileEditForm(forms.ModelForm):
  class Meta:
   model = UserProfile
   fields = ['age', 'photo']