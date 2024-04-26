from django.contrib import admin

from .models import Item, Order, LinkedOrder


class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'item_group', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'item_id', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status']


class LinkedOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'position', 'item_id', 'unit_of_measurement', 'quantity', 'price_without_VAT',
                    'status']


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(LinkedOrder, LinkedOrderAdmin)
