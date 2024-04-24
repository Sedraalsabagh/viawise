# Generated by Django 5.0.3 on 2024-04-12 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0017_alter_flight_airplane'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='price',
            field=models.DecimalField(decimal_places=2, default=10.1, max_digits=10),
        ),
    ]
