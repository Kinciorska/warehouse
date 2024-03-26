from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Items(models.Model):
    class ItemGroup(models.TextChoices):
        ITEM_GROUP_1 = 'G-1', _("Item group 1")
        ITEM_GROUP_2 = 'G-2', _("Item group 2")

    class ItemUnit(models.TextChoices):
        ITEM_UNIT_1 = 'U-1', _("Item unit 1")
        ITEM_UNIT_2 = 'U-2', _("Item unit 2")

    item_id = models.BigAutoField(primary_key=True)
    item_name = models.CharField(unique=True, max_length=50)
    item_group = models.CharField(max_length=3, choices=ItemGroup)
    unit_of_measurement = models.CharField(max_length=3, choices=ItemUnit)
    quantity = models.IntegerField(default=1)
    price_without_VAT = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=50)
    storage_location = models.CharField(max_length=50, blank=True)
    contact_person = models.TextField(max_length=250, blank=True)
    photo = models.ImageField(upload_to='uploads/', blank=True)

    class Meta:
        verbose_name_plural = 'Items'
        ordering = ['item_id']

    def __str__(self):
        return self.item_name


class Requests(models.Model):

    class Status(models.TextChoices):
        NEW = 'new', _("New")
        APPROVED = 'apr', _("Approved")
        REJECTED = 'rej', _("Rejected")

    request_id = models.BigAutoField(primary_key=True)
    employee_name = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Items, on_delete=models.CASCADE)
    unit_of_measurement = models.CharField(max_length=3, choices=Items.ItemUnit)
    quantity = models.IntegerField(default=1)
    price_without_VAT = models.DecimalField(max_digits=6, decimal_places=2)
    comment = models.TextField(max_length=250, blank=True)
    status = models.CharField(max_length=3, choices=Status, default=Status.NEW)

    class Meta:
        verbose_name_plural = "Requests"
        ordering = ['item_id']

    def __str__(self):
        return f"Item: {self.item_id} in quantity: {self.quantity}. Status: {self.status}"


