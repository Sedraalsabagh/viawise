# Generated by Django 5.0.3 on 2024-05-03 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0023_flight_destination_activity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='destination_activity',
            field=models.CharField(blank=True, choices=[('Sightseeing', 'Sightseeing'), ('Skiing', 'Skiing'), ('Beach relaxation', 'Beach relaxation')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='destination_climate',
            field=models.CharField(blank=True, choices=[('Warm', 'Warm'), ('Cold', 'Cold'), ('Moderate', 'Moderate')], max_length=100, null=True),
        ),
    ]
