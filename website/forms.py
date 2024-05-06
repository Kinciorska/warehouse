from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Item, Order, LinkedOrder


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class ItemForm(ModelForm):

    class Meta:
        model = Item
        fields = ('item_name', 'item_group', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status',
                  'storage_location', 'contact_person', 'photo')


class OrderStatusForm(ModelForm):

    class Meta:
        model = Order
        fields = ('status', 'comment')


class OrderForm(ModelForm):

    class Meta:
        model = Order
        fields = ('unit_of_measurement', 'quantity', 'comment')


class OrderForLinkedOrderForm(forms.Form):
    order = forms.ModelChoiceField(queryset=Order.objects.filter(status=Order.Status.NEW),
                                   required=False)
    linked_order = forms.ModelChoiceField(queryset=LinkedOrder.objects.filter(status=LinkedOrder.Status.NEW),
                                          required=False)


class LinkedOrderStatusForm(ModelForm):

    class Meta:
        model = LinkedOrder
        fields = ('status', 'comment')


class SearchOrderForm(forms.Form):
    order_id = forms.IntegerField(label="", widget=forms.NumberInput(attrs={'placeholder': 'Search...'}))


class SearchItemForm(forms.Form):
    searched_item_name = forms.CharField(max_length=250, label="", widget=forms.TextInput(attrs={'placeholder': 'Search...'}))


class FilterOrderForm(forms.Form):
    quantity_0_10 = forms.BooleanField(label="QUANTITY <10", required=False)
    quantity_10_50 = forms.BooleanField(label="QUANTITY 10-50", required=False)
    quantity_50_100 = forms.BooleanField(label="QUANTITY 50-100", required=False)
    quantity_100_9999999 = forms.BooleanField(label="QUANTITY >100", required=False)
    price_0_10 = forms.BooleanField(label="PRICE <10", required=False)
    price_10_50 = forms.BooleanField(label="PRICE 10-50", required=False)
    price_50_100 = forms.BooleanField(label="PRICE 50-100", required=False)
    price_100_9999999 = forms.BooleanField(label="PRICE >100", required=False)
    status_new = forms.BooleanField(label="NEW", required=False)
    status_approved = forms.BooleanField(label="APPROVED", required=False)
    status_rejected = forms.BooleanField(label="REJECTED", required=False)
