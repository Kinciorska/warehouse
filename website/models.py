from django.db import models
from django.utils.translation import gettext_lazy as _


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

