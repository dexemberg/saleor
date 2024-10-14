# Generated by Django 3.2.25 on 2024-09-26 09:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("channel", "0017_channel_include_draft_order_in_voucher_usage"),
    ]

    operations = [
        migrations.AddField(
            model_name="channel",
            name="automatically_complete_fully_paid_checkouts",
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL(
            """
            ALTER TABLE channel_channel
            ALTER COLUMN automatically_complete_fully_paid_checkouts
            SET DEFAULT false;
            """,
            migrations.RunSQL.noop,
        ),
    ]