from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Items, Requests, RequestRow


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


class RequestStatusForm(ModelForm):

    class Meta:
        model = Requests
        fields = ('status', 'comment')


class RequestForm(ModelForm):

    class Meta:
        model = Requests
        fields = ('unit_of_measurement', 'quantity', 'comment')


class RequestForRequestRowForm(forms.Form):
    request = forms.ModelChoiceField(queryset=Requests.objects.filter(status=Requests.Status.NEW), required=False)
    requests = forms.ModelChoiceField(queryset=RequestRow.objects.filter(status=RequestRow.Status.NEW),
                                      required=False)


class RequestRowStatusForm(ModelForm):

    class Meta:
        model = RequestRow
        fields = ('status', 'comment')
