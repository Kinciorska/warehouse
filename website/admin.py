from django.contrib import admin

from .models import Items, Requests


class ItemsAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'item_group', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status']


class RequestsAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'item_id', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status']


admin.site.register(Items, ItemsAdmin)
admin.site.register(Requests, RequestsAdmin)
