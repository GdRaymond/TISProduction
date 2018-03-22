from django.contrib.auth.models import User
from django import forms

class ProfileForm(forms.ModelForm):
    first_name=forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=30,
        required=False
    )
    last_name=forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=30,
        required=False
    )
    job_title=forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=30,
        required=False,
        help_text='The title in your curretn company',
    )
    email=forms.CharField(
        widget=forms.EmailInput(attrs={'class':'form-control'}),
        max_length=70,
        required=False
    )
    url=forms.CharField(
        widget=forms.URLInput(attrs={'class':'form-control'}),
        max_length=50,
        required=False
    )
    location=forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=100,
        required=False
    )

    class Meta:
        model=User
        fields=['first_name','last_name','job_title','email','url','location',]
