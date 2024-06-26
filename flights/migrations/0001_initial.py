# Generated by Django 5.0.3 on 2024-05-11 13:33

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Airline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airline_id', models.IntegerField(default=0)),
                ('airline_name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('airport_id', models.AutoField(primary_key=True, serialize=False)),
                ('airport_name', models.CharField(max_length=100)),
                ('IATA_code', models.CharField(max_length=3)),
                ('contact_info', models.TextField()),
                ('country', models.CharField(max_length=50)),
                ('comment', models.TextField(default='', max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refundable', models.BooleanField(default=False)),
                ('exchangeable', models.BooleanField(default=False)),
                ('exchangeable_condition', models.CharField(blank=True, max_length=255, null=True)),
                ('cancellation_period', models.DurationField(default=datetime.timedelta(0))),
            ],
        ),
        migrations.CreateModel(
            name='RefundedPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notes', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SeatType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('economy_capacity', models.IntegerField(null=True, unique=True)),
                ('business_class_capacity', models.IntegerField(null=True, unique=True)),
                ('first_class_capacity', models.IntegerField(null=True, unique=True)),
                ('economy_weight_limit', models.IntegerField(default=30, null=True)),
                ('business_class_weight_limit', models.IntegerField(default=40, null=True)),
                ('first_class_weight_limit', models.IntegerField(default=50, null=True)),
                ('carry_on_bag_weight_limit', models.IntegerField(default=8, null=True)),
                ('excess_weight_fee', models.DecimalField(decimal_places=2, default=22, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Airplane',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airplane_name', models.CharField(max_length=100)),
                ('manufacturer', models.CharField(max_length=100)),
                ('manufacturing_date', models.DateField()),
                ('airline', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flights.airline')),
                ('seats', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.seattype')),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure_date', models.DateField(default=datetime.datetime.now)),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('airportDeparture', models.CharField(max_length=40)),
                ('airportArrival', models.CharField(max_length=40)),
                ('notes', models.TextField(blank=True, max_length=200, null=True)),
                ('ratings', models.IntegerField(blank=True, null=True)),
                ('departure_city', models.CharField(default='', max_length=100, null=True)),
                ('destination_city', models.CharField(default='', max_length=100)),
                ('departure_country', models.CharField(default='', max_length=100)),
                ('destination_country', models.CharField(default='', max_length=100)),
                ('economy_remaining', models.IntegerField(default=20, null=True)),
                ('first_remaining', models.IntegerField(default=10, null=True)),
                ('business_remaining', models.IntegerField(default=10, null=True)),
                ('price_flight', models.DecimalField(decimal_places=2, default=10.1, max_digits=10)),
                ('destination_activity', models.CharField(blank=True, choices=[('Sightseeing', 'Sightseeing'), ('Skiing', 'Skiing'), ('Beach relaxation', 'Beach relaxation')], max_length=100, null=True)),
                ('destination_type', models.CharField(blank=True, choices=[('Business', 'Business'), ('Tourism', 'Tourism'), ('Education', 'Education'), ('Entertainment', 'Entertainment')], max_length=100, null=True)),
                ('destination_climate', models.CharField(blank=True, choices=[('Warm', 'Warm'), ('Cold', 'Cold'), ('Moderate', 'Moderate')], max_length=100, null=True)),
                ('flight_schedule', models.CharField(blank=True, choices=[('Direct', 'Direct'), ('Transit', 'Transit')], max_length=100, null=True)),
                ('Airplane', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='flights.airplane')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FlightSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('comment', models.TextField(default='', max_length=2000)),
                ('airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.airport')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.flight')),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField(blank=True, null=True)),
                ('conditions', models.TextField(blank=True, null=True)),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('flight', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flights.flight')),
            ],
        ),
        migrations.AddField(
            model_name='airline',
            name='policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.policy'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(default='', max_length=2000)),
                ('ratings', models.IntegerField(default=0)),
                ('createAt', models.DateTimeField(auto_now_add=True)),
                ('flight', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='flights.flight')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
