# Generated by Django 3.2.6 on 2021-08-17 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0030_auto_20210415_1001"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shippingmethodtranslation",
            name="language_code",
            field=models.CharField(max_length=35),
        ),
    ]