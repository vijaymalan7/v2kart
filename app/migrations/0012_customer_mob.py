# Generated by Django 5.0.6 on 2024-06-29 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='mob',
            field=models.IntegerField(blank=True, default='0000000000'),
        ),
    ]