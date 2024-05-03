# Generated by Django 5.0.3 on 2024-05-03 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_agencypolicy_points_offers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agencypolicy',
            name='policy_type',
            field=models.CharField(blank=True, choices=[('modify', 'Modify'), ('cancel', 'Cancel'), ('offers', 'Offers'), ('cancel_without_payment', 'Cancel Without Payment'), ('cancel_over_week', 'cancel_over_week')], max_length=100, null=True),
        ),
    ]
