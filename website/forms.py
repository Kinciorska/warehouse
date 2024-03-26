from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Items


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class ItemForm(ModelForm):

    class Meta:
        model = Items
        fields = ('item_name', 'item_group', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status',
                  'storage_location', 'contact_person', 'photo')
