from django.contrib import admin
from .models import (
    Client, Employee, Equipment, RentalRequest, Contract,
    Invoice, EquipmentCheck, EquipmentRepair, RepairInvoice,
    SystemLog
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_day', 'is_available', 'needs_repair')
    list_filter = ('category', 'needs_repair', 'is_rented')
    search_fields = ('name', 'description')

@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'equipment', 'status', 'request_date', 'start_date', 'end_date')
    list_filter = ('status', 'request_date')
    search_fields = ('client__user__username', 'equipment__name')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'equipment', 'status', 'start_date', 'end_date', 'total_price')
    list_filter = ('status', 'start_date')
    search_fields = ('client__user__username', 'equipment__name')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'amount', 'status', 'created_at', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('contract__client__user__username', 'contract__equipment__name')

@admin.register(EquipmentCheck)
class EquipmentCheckAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'technician', 'status', 'check_date')
    list_filter = ('status', 'check_date')
    search_fields = ('equipment__name', 'technician__user__username')

@admin.register(EquipmentRepair)
class EquipmentRepairAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'technician', 'status', 'repair_date', 'repair_cost')
    list_filter = ('status', 'repair_date')
    search_fields = ('equipment__name', 'technician__user__username')

@admin.register(RepairInvoice)
class RepairInvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'repair', 'amount', 'status', 'created_at', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('repair__equipment__name', 'repair__technician__user__username')

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'action')
