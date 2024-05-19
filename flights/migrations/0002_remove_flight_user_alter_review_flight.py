# Generated by Django 5.0.3 on 2024-05-18 19:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='user',
        ),
        migrations.AlterField(
            model_name='review',
            name='flight',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flights.flight'),
        ),
    ]