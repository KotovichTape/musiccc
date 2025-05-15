from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('warehouse', 'Складской работник'),
        ('technician', 'Технический специалист'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('guitar', 'Гитары'),
        ('microphone', 'Микрофоны'),
        ('drums', 'Барабаны'),
        ('amplifier', 'Усилители'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='guitar')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    needs_repair = models.BooleanField(default=False)
    is_rented = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='equipment_photos/', blank=True, null=True)

    def is_available(self):
        return not self.is_rented and not self.needs_repair

    def __str__(self):
        return f"{self.name} ({'Доступно' if self.is_available() else 'Недоступно'})"

class RentalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('approved', 'Подтверждено'),
        ('issued', 'Выдано'),
        ('returned', 'Возвращено'),
        ('rejected', 'Отклонено'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='rental_requests')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=now)
    end_date = models.DateField(default=now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    issued_date = models.DateTimeField(null=True, blank=True)
    returned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.client} - {self.equipment} ({self.status})"

class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активный'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    rental_request = models.OneToOneField(RentalRequest, on_delete=models.CASCADE, related_name='contract')
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='contracts')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Договор {self.id} - {self.equipment.name}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Счет {self.id} - {self.contract.equipment.name}"

class EquipmentCheck(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('checked_ok', 'Проверено, исправно'),
        ('needs_repair', 'Требуется ремонт'),
        ('repaired', 'Ремонт завершён'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    technician = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    check_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата завершения/обновления")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Проверка {self.equipment.name} ({self.get_status_display()})"

class EquipmentRepair(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В ремонте'),
        ('completed', 'Ремонт завершен'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    technician = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    repair_date = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения ремонта")
    description = models.TextField()
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Ремонт {self.equipment.name} ({self.get_status_display()})"

class RepairInvoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
    ]

    repair = models.ForeignKey(EquipmentRepair, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Счет за ремонт {self.id} - {self.repair.equipment.name}"

class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Лог {self.user} ({self.timestamp})"
