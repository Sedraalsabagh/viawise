# Generated by Django 5.0.3 on 2024-05-19 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0003_alter_review_flight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='flight',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flights.flight'),
        ),
    ]
