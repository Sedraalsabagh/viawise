# Generated by Django 5.0.3 on 2024-05-01 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_pointbalance'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pointBalance',
            field=models.PositiveIntegerField(default=0),
        ),
    ]