# Generated by Django 4.1.7 on 2023-03-22 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salesmanbasket', '0005_rename_identifier_basket_hook_identifier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='hook_id',
        ),
    ]
