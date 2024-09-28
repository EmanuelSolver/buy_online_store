from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Store, CollectionCenter
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'mobile_number', 'address', 'password1', 'password2']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['storeName', 'location']

class CollectionCenterForm(forms.ModelForm):
    class Meta:
        model = CollectionCenter
        fields = ['centerName', 'county', 'town', 'building']
