# Generated by Django 5.0.3 on 2024-03-26 07:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Items',
            fields=[
                ('item_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('item_name', models.CharField(max_length=50, unique=True)),
                ('item_group', models.CharField(choices=[('G-1', 'Item group 1'), ('G-2', 'Item group 2')], max_length=3)),
                ('unit_of_measurement', models.CharField(choices=[('U-1', 'Item unit 1'), ('U-2', 'Item unit 2')], max_length=3)),
                ('quantity', models.IntegerField(default=1)),
                ('price_without_VAT', models.DecimalField(decimal_places=2, max_digits=6)),
                ('status', models.CharField(max_length=50)),
                ('storage_location', models.CharField(blank=True, max_length=50)),
                ('contact_person', models.TextField(blank=True, max_length=250)),
                ('photo', models.ImageField(blank=True, upload_to='uploads/')),
            ],
            options={
                'verbose_name_plural': 'Items',
                'ordering': ['item_id'],
            },
        ),
        migrations.AlterModelOptions(
            name='requests',
            options={'ordering': ['item_id'], 'verbose_name_plural': 'Requests'},
        ),
        migrations.RenameField(
            model_name='requests',
            old_name='unit',
            new_name='unit_of_measurement',
        ),
        migrations.AlterField(
            model_name='requests',
            name='employee_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='requests',
            name='item_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.items'),
        ),
        migrations.DeleteModel(
            name='Goods',
        ),
    ]
