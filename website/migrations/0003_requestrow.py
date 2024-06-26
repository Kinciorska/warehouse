# Generated by Django 5.0.3 on 2024-03-27 14:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_items_alter_requests_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestRow',
            fields=[
                ('request_row_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('request_id', models.IntegerField()),
                ('request_row', models.IntegerField()),
                ('unit_of_measurement', models.CharField(choices=[('U-1', 'Item unit 1'), ('U-2', 'Item unit 2')], max_length=3)),
                ('quantity', models.IntegerField(default=1)),
                ('price_without_VAT', models.DecimalField(decimal_places=2, max_digits=6)),
                ('comment', models.TextField(blank=True, max_length=250)),
                ('status', models.CharField(choices=[('new', 'New'), ('apr', 'Approved'), ('rej', 'Rejected')], default='new', max_length=3)),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.items')),
            ],
            options={
                'verbose_name_plural': 'Request Rows',
                'ordering': ['request_id'],
            },
        ),
    ]
