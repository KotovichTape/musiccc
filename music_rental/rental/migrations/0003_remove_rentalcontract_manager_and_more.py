# Generated by Django 5.1.7 on 2025-05-10 23:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0002_remove_rentalrequest_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentalcontract',
            name='manager',
        ),
        migrations.RemoveField(
            model_name='rentalcontract',
            name='rental_request',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='rentalrequest',
            name='quantity',
        ),
        migrations.AddField(
            model_name='equipment',
            name='is_rented',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='equipment',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='equipment_photos/'),
        ),
        migrations.AddField(
            model_name='equipmentcheck',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='equipmentrepair',
            name='repair_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='equipmentrepair',
            name='status',
            field=models.CharField(choices=[('in_progress', 'В ремонте'), ('completed', 'Ремонт завершен')], default='in_progress', max_length=20),
        ),
        migrations.AddField(
            model_name='rentalrequest',
            name='issued_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rentalrequest',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_requests', to='rental.employee'),
        ),
        migrations.AddField(
            model_name='rentalrequest',
            name='returned_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rentalrequest',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='equipmentcheck',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает проверки'), ('checked_ok', 'Проверено, исправно'), ('needs_repair', 'Требуется ремонт')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='equipmentcheck',
            name='technician',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rental.employee'),
        ),
        migrations.AlterField(
            model_name='equipmentrepair',
            name='technician',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rental.employee'),
        ),
        migrations.AlterField(
            model_name='rentalrequest',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rental_requests', to='rental.client'),
        ),
        migrations.AlterField(
            model_name='rentalrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидание'), ('approved', 'Подтверждено'), ('issued', 'Выдано'), ('returned', 'Возвращено'), ('rejected', 'Отклонено')], default='pending', max_length=10),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('active', 'Активный'), ('completed', 'Завершен'), ('cancelled', 'Отменен')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='rental.client')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rental.equipment')),
                ('manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts', to='rental.employee')),
                ('rental_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contract', to='rental.rentalrequest')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('paid', 'Оплачен'), ('cancelled', 'Отменен')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('due_date', models.DateField()),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='rental.contract')),
            ],
        ),
        migrations.CreateModel(
            name='RepairInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('paid', 'Оплачен'), ('cancelled', 'Отменен')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('due_date', models.DateField()),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('repair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='rental.equipmentrepair')),
            ],
        ),
        migrations.DeleteModel(
            name='EquipmentUsage',
        ),
        migrations.DeleteModel(
            name='RentalContract',
        ),
    ]
