# Generated by Django 4.1.7 on 2023-03-11 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0005_alter_hall_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="seats", name="is_free", field=models.BooleanField(default=True),
        ),
    ]
