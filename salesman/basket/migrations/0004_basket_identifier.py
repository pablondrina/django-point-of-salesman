# Generated by Django 4.1.7 on 2023-03-20 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesmanbasket', '0003_rename_owner_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='identifier',
            field=models.CharField(blank=True, max_length=36, null=True, unique=True, verbose_name='Identifier'),
        ),
    ]
