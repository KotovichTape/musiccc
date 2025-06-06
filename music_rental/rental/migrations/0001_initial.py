# Generated by Django 5.1.7 on 2025-03-17 16:02

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(choices=[('guitar', 'Гитары'), ('microphone', 'Микрофоны'), ('drums', 'Барабаны'), ('amplifier', 'Усилители')], default='guitar', max_length=20)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price_per_day', models.DecimalField(decimal_places=2, max_digits=10)),
                ('needs_repair', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('manager', 'Менеджер'), ('warehouse', 'Складской работник'), ('technician', 'Технический специалист'), ('admin', 'Администратор')], max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.TextField()),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rental.equipment')),
                ('technician', models.ForeignKey(limit_choices_to={'role': 'technician'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rental.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentRepair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repair_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rental.equipment')),
                ('technician', models.ForeignKey(limit_choices_to={'role': 'technician'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rental.employee')),
            ],
        ),
        migrations.CreateModel(
            name='RentalContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('manager', models.ForeignKey(limit_choices_to={'role': 'manager'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rental.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usage_date', models.DateTimeField(auto_now_add=True)),
                ('returned', models.BooleanField(default=False)),
                ('damage_reported', models.TextField(blank=True, null=True)),
                ('rental_contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rental.rentalcontract')),
            ],
        ),
        migrations.CreateModel(
            name='RentalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('duration', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('pending', 'Ожидание'), ('approved', 'Подтверждено'), ('issued', 'Выдано'), ('returned', 'Возвращено'), ('rejected', 'Отклонено')], default='pending', max_length=10)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(default=django.utils.timezone.now)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rental.client')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rental.equipment')),
            ],
        ),
        migrations.AddField(
            model_name='rentalcontract',
            name='rental_request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rental.rentalrequest'),
        ),
        migrations.CreateModel(
            name='SystemLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
