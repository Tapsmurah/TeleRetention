from django import forms # type: ignore
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profileimg', 'firstname', 'lastname', 'address', 
            'gender', 'department', 'country', 'province', 
            'city', 'mobile_no'
        ]