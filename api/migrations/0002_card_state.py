# Generated by Django 5.0.6 on 2024-06-01 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="state",
            field=models.CharField(default="pending", max_length=50),
        ),
    ]