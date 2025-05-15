from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm, RentalRequestForm
from .models import Client, Employee, Equipment, RentalRequest, Contract, Invoice, EquipmentCheck, EquipmentRepair, RepairInvoice, SystemLog
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, CharField, TextField
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.forms import modelform_factory
from django.utils.timezone import now
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt 
from django.core.exceptions import PermissionDenied
import json
from datetime import timedelta
import sys
from django.utils import timezone
from django.urls import reverse
from collections import defaultdict
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import os
from django.conf import settings
from django.views.decorators.http import require_POST

font_path = os.path.join(settings.BASE_DIR, 'rental', 'static', 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

MODEL_MAP = {
    'clients': (Client, 'Клиенты'),
    'employees': (Employee, 'Сотрудники'),
    'equipment': (Equipment, 'Оборудование'),
    'rental_requests': (RentalRequest, 'Заявки на аренду'),
    'contracts': (Contract, 'Договоры'),
    'invoices': (Invoice, 'Счета'),
    'repair_invoices': (RepairInvoice, 'Счета за ремонт'),
}

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            role = form.cleaned_data['role']
            phone = form.cleaned_data.get('phone', '')
            
            if role == 'client':
                Client.objects.create(user=user, phone=phone)
            else:
                Employee.objects.create(user=user, role=role, phone=phone)

            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'rental/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('dashboard')  
    else:
        form = LoginForm()
    return render(request, 'rental/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def equipment_list_view(request):
    if hasattr(request.user, 'employee'):
        role = request.user.employee.role
        if role == 'admin':
            return redirect('dashboard')  
        elif role == 'technician':
            return redirect('dashboard_technician')
        elif role == 'warehouse':
            return redirect('dashboard_warehouse')
        elif role == 'manager':
            return redirect('dashboard_manager')
    elif hasattr(request.user, 'client'):
        return redirect('catalog')
    return redirect('catalog')

@login_required
def manage_rental_requests(request):
    requests = RentalRequest.objects.all()
    return render(request, 'rental/manage_requests.html', {'requests': requests})

@login_required
def rental_reports_view(request):
    total_requests = RentalRequest.objects.count()
    
    approved_requests = RentalRequest.objects.filter(status='approved').count()

    total_income = Invoice.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'total_income': total_income
    }
    return render(request, 'rental/reports.html', context)

@login_required
def equipment_check_list(request):
    checks = EquipmentCheck.objects.all()
    return render(request, 'rental/equipment_checks.html', {'checks': checks})

@login_required
def add_equipment_check(request, equipment_id):
    equipment = Equipment.objects.get(id=equipment_id)
    EquipmentCheck.objects.create(
        equipment=equipment, 
        technician=request.user.employee, 
        status="pending"
    )
    return redirect('equipment_check_list')

@login_required
def add_equipment_repair(request, equipment_id):
    equipment = Equipment.objects.get(id=equipment_id)
    repair = EquipmentRepair.objects.create(
        equipment=equipment, 
        technician=request.user.employee, 
        description="Требуется ремонт",
        status="in_progress"
    )
    
    RepairInvoice.objects.create(
        repair=repair,
        amount=0,  
        status='pending',
        due_date=now()
    )
    
    return redirect('equipment_check_list')

@login_required
def profile_view(request):
    try:
        if hasattr(request.user, 'client'):
            profile = request.user.client
        elif hasattr(request.user, 'employee'):
            profile = request.user.employee
        else:
            profile = None
    except Exception as e:
        profile = None

    return render(request, 'rental/profile.html', {'profile': profile})

@login_required
def edit_profile_view(request):
    if hasattr(request.user, 'client'):
        profile = request.user.client
    elif hasattr(request.user, 'employee'):
        profile = request.user.employee
    else:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            SystemLog.objects.create(user=request.user, action="Обновление профиля")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'rental/edit_profile.html', {'form': form})

@login_required
def rental_history_view(request):
    if hasattr(request.user, 'client'):
        rentals = RentalRequest.objects.filter(client=request.user.client).order_by('-request_date')
    else:
        rentals = []
    
    return render(request, 'rental/rental_history.html', {'rentals': rentals})

def home_view(request):
    return render(request, 'rental/home.html')

@login_required
def logs_view(request):
    logs = SystemLog.objects.all().order_by('-timestamp')[:100]
    return render(request, 'rental/logs.html', {'logs': logs})

@login_required
def catalog_view(request):
    equipment = Equipment.objects.filter(is_rented=False, needs_repair=False)  
    return render(request, 'rental/catalog.html', {'equipment': equipment})

@login_required
def dashboard_view(request):
    try:
        employee = Employee.objects.get(user=request.user)
        
        if employee.role == 'admin':
            clients = Client.objects.all()
            employees = Employee.objects.all()
            system_logs = SystemLog.objects.all().order_by('-timestamp')[:50]
            return render(request, 'rental/dashboard_admin.html', {
                'clients': clients,
                'employees': employees,
                'system_logs': system_logs
            })

        elif employee.role == 'manager':
            pending_requests = RentalRequest.objects.filter(status="pending")
            active_contracts = Contract.objects.filter(status="active")
            total_income = Invoice.objects.filter(status="paid").aggregate(Sum('amount'))['amount__sum'] or 0
            return render(request, 'rental/dashboard_manager.html', {
                'pending_requests': pending_requests,
                'active_contracts': active_contracts,
                'total_income': total_income
            })

        elif employee.role == 'warehouse':
            return redirect('dashboard_warehouse')

        elif employee.role == 'technician':
            return redirect('dashboard_technician')

    except Employee.DoesNotExist:
        client = Client.objects.get(user=request.user)
        active_rentals = RentalRequest.objects.filter(client=client, status__in=["approved", "issued"])
        rental_history = RentalRequest.objects.filter(client=client, status="returned")
        contracts = Contract.objects.filter(client=client)
        return render(request, 'rental/dashboard_client.html', {
            'active_rentals': active_rentals,
            'rental_history': rental_history,
            'contracts': contracts
        })

@login_required
def dashboard_warehouse(request):
    """Кабинет складского работника"""
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'warehouse':
        raise PermissionDenied("Только складские работники могут просматривать эту страницу")
    
    active_rentals = RentalRequest.objects.filter(
        status__in=["approved", "issued"]
    ).select_related('client__user', 'equipment').order_by('-request_date')
    
    rental_history = RentalRequest.objects.filter(
        status="returned"
    ).select_related('client__user', 'equipment').order_by('-returned_date')
    
    equipment_in_repair = Equipment.objects.filter(
        needs_repair=True
    ).order_by('name')

    recent_issues = RentalRequest.objects.filter(
        status="issued",
        issued_date__gte=now() - timedelta(days=1)
    ).select_related('client__user', 'equipment').order_by('-issued_date')

    all_rentals = RentalRequest.objects.all().select_related('client__user', 'equipment').order_by('-request_date')

    return render(request, "rental/dashboard_warehouse.html", {
        "active_rentals": active_rentals,
        "rental_history": rental_history,
        "equipment_in_repair": equipment_in_repair,
        "recent_issues": recent_issues,
        "all_rentals": all_rentals,
    })

@login_required
def dashboard_technician(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'technician':
        raise PermissionDenied("Только технические специалисты могут просматривать эту страницу")

    waiting_equipment = EquipmentCheck.objects.filter(
        status="pending"
    ).select_related('equipment')

    history_checks = EquipmentCheck.objects.filter(
        technician=request.user.employee
    ).exclude(status="pending").select_related('equipment')

    active_repairs = EquipmentRepair.objects.filter(
        status="in_progress",
        technician=request.user.employee
    ).select_related('equipment')

    completed_repairs = EquipmentRepair.objects.filter(
        status="completed",
        technician=request.user.employee
    ).select_related('equipment')

    all_checks = EquipmentCheck.objects.all().select_related('equipment', 'technician')
    all_equipment_in_repair = Equipment.objects.filter(needs_repair=True)

    return render(request, "rental/dashboard_technician.html", {
        "waiting_equipment": waiting_equipment,
        "history_checks": history_checks,
        "active_repairs": active_repairs,
        "completed_repairs": completed_repairs,
        "all_checks": all_checks,
        "all_equipment_in_repair": all_equipment_in_repair
    })

@login_required
def dashboard_manager(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'manager':
        raise PermissionDenied("Только менеджеры могут просматривать эту страницу")
        
    pending_requests = RentalRequest.objects.filter(status="pending")
    active_contracts = Contract.objects.filter(status="active")
    pending_invoices = Invoice.objects.filter(status="pending")
    
    context = {
        "pending_requests": pending_requests,
        "active_contracts": active_contracts,
        "pending_invoices": pending_invoices
    }
    
    return render(request, "rental/dashboard_manager.html", context)

@login_required
def create_rental_request(request, equipment_id):
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Только клиенты могут создавать заявки на аренду")
    
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    if equipment.is_rented or equipment.needs_repair:
        messages.error(request, 'Это оборудование сейчас недоступно для аренды')
        return redirect('catalog')
    
    if request.method == 'POST':
        form = RentalRequestForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            days = (end_date - start_date).days
            total_price = equipment.price_per_day * days
            
            rental_request = form.save(commit=False)
            rental_request.client = request.user.client
            rental_request.equipment = equipment
            rental_request.status = 'pending'
            rental_request.total_price = total_price
            rental_request.save()
            
            SystemLog.objects.create(
                user=request.user,
                action=f"Создана заявка на аренду оборудования: {equipment.name}"
            )
            
            messages.success(request, 'Заявка на аренду успешно создана')
            return redirect('rental_history')
    else:
        form = RentalRequestForm()
    
    return render(request, 'rental/create_rental_request.html', {
        'form': form,
        'equipment': equipment
    })

@login_required
def rental_request_detail(request, request_id):
    rental_request = get_object_or_404(RentalRequest, id=request_id)
    
    # Проверяем права доступа
    if hasattr(request.user, 'client'):
        if rental_request.client != request.user.client:
            raise PermissionDenied("У вас нет доступа к этой заявке")
    elif hasattr(request.user, 'employee'):
        if request.user.employee.role not in ['manager', 'admin']:
            raise PermissionDenied("У вас нет доступа к этой заявке")
    
    return render(request, 'rental/rental_request_detail.html', {
        'rental_request': rental_request
    })

@login_required
def approve_request(request, request_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'manager':
        raise PermissionDenied("Только менеджеры могут подтверждать заявки")
    
    rental_request = get_object_or_404(RentalRequest, id=request_id, status='pending')
    
    if request.method == 'POST':
        contract = Contract.objects.create(
            rental_request=rental_request,
            manager=request.user.employee,
            client=rental_request.client,
            equipment=rental_request.equipment,
            start_date=rental_request.start_date,
            end_date=rental_request.end_date,
            total_price=rental_request.total_price or rental_request.equipment.price_per_day * (rental_request.end_date - rental_request.start_date).days,
            status='active'
        )
        
        Invoice.objects.create(
            contract=contract,
            amount=contract.total_price,
            status='pending',
            due_date=now()
        )
        
        rental_request.status = 'approved'
        rental_request.manager = request.user.employee
        rental_request.save()
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Подтверждена заявка на аренду: {rental_request.equipment.name} для клиента {rental_request.client}"
        )
        
        messages.success(request, 'Заявка успешно подтверждена')
    
    return redirect('dashboard_manager')

@login_required
def reject_request(request, request_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'manager':
        raise PermissionDenied("Только менеджеры могут отклонять заявки")
    
    rental_request = get_object_or_404(RentalRequest, id=request_id, status='pending')
    
    if request.method == 'POST':
        rental_request.status = 'rejected'
        rental_request.manager = request.user.employee
        rental_request.save()
        
        try:
            contract = Contract.objects.get(rental_request=rental_request)
            contract.status = 'cancelled'
            contract.save()
            
            for invoice in contract.invoices.all():
                invoice.status = 'cancelled'
                invoice.save()
        except Contract.DoesNotExist:
            pass
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Отклонена заявка на аренду: {rental_request.equipment.name} для клиента {rental_request.client}"
        )
        
        messages.success(request, 'Заявка отклонена')
    
    return redirect('dashboard_manager')

@login_required
@csrf_exempt
def issue_equipment(request, rental_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'warehouse':
        raise PermissionDenied("Только складские работники могут выдавать оборудование")
    
    rental_request = get_object_or_404(RentalRequest, id=rental_id, status='approved')
    
    if request.method == 'POST':
        if not rental_request.equipment.is_rented:
            rental_request.equipment.is_rented = True
            rental_request.equipment.save()
            
            rental_request.status = 'issued'
            rental_request.issued_date = now()
            rental_request.save()
            
            try:
                contract = Contract.objects.get(rental_request=rental_request)
                contract.status = 'active'
                contract.save()
            except Contract.DoesNotExist:
                pass
            
            SystemLog.objects.create(
                user=request.user,
                action=f"Выдано оборудование: {rental_request.equipment.name} клиенту {rental_request.client}"
            )
            
            messages.success(request, 'Оборудование успешно выдано')
        else:
            messages.error(request, 'Оборудование уже выдано')
    
    return redirect('dashboard_warehouse')

@login_required
def return_equipment(request, rental_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'warehouse':
        raise PermissionDenied("Только складские работники могут принимать оборудование")
    
    rental_request = get_object_or_404(RentalRequest, id=rental_id, status='issued')
    
    if request.method == 'POST':
        print(f"DEBUG: return_equipment called for rental_id={rental_id}", file=sys.stderr)
        
        rental_request.equipment.is_rented = False
        rental_request.equipment.save()
        
        rental_request.status = 'returned'
        rental_request.returned_date = now()
        rental_request.save()
        
        # Обновляем статус договора если есть
        try:
            contract = Contract.objects.get(rental_request=rental_request)
            contract.status = 'completed'
            contract.save()
        except Contract.DoesNotExist:
            pass
            
        # Создаем запись для проверки оборудования (без техника)
        check = EquipmentCheck.objects.create(
            equipment=rental_request.equipment,
            status='pending',
            notes='Проверка после возврата от клиента',
            technician=None
        )
        print(f"DEBUG: Created EquipmentCheck: id={check.id}, equipment={check.equipment.name}, status={check.status}", file=sys.stderr)
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Возвращено оборудование: {rental_request.equipment.name} от клиента {rental_request.client}"
        )
        
        messages.success(request, 'Оборудование успешно возвращено')
    
    return redirect('dashboard_warehouse')

@login_required
@csrf_exempt
def perform_equipment_check(request, check_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'technician':
        raise PermissionDenied("Только технические специалисты могут проверять оборудование")
    
    equipment_check = get_object_or_404(EquipmentCheck, id=check_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        equipment_check.status = status
        equipment_check.notes = notes
        equipment_check.technician = request.user.employee
        equipment_check.save()
        
        if status == 'needs_repair':
            equipment_check.equipment.needs_repair = False
            equipment_check.equipment.is_rented = False
            equipment_check.equipment.save()
            repair = EquipmentRepair.objects.create(
                equipment=equipment_check.equipment,
                technician=request.user.employee,
                description=notes,
                status='completed'  
            )
            last_rental = RentalRequest.objects.filter(equipment=equipment_check.equipment).order_by('-returned_date').first()
            client = last_rental.client if last_rental else None
            invoice = RepairInvoice.objects.create(
                repair=repair,
                amount=0,  
                status='pending',
                due_date=now(),
                notes=f'Счёт за ремонт для клиента {client.user.username}' if client else ''
            )
        elif status == 'checked_ok':
            equipment_check.equipment.needs_repair = False
            equipment_check.equipment.is_rented = False
            equipment_check.equipment.save()
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Проверено оборудование: {equipment_check.equipment.name}, статус: {status}"
        )
        
        messages.success(request, 'Проверка оборудования завершена')
    
    return redirect('dashboard_technician')

@login_required
def complete_equipment_repair(request, repair_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'technician':
        raise PermissionDenied("Только технические специалисты могут ремонтировать оборудование")
    
    repair = get_object_or_404(EquipmentRepair, id=repair_id)
    
    if request.method == 'POST':
        repair_description = request.POST.get('repair_description', '')
        repair_cost = request.POST.get('repair_cost', 0)
        
        repair.description = repair_description
        repair.repair_cost = repair_cost
        repair.status = 'completed'
        repair.completed_at = timezone.now()
        repair.save()
        
        repair.equipment.needs_repair = False
        repair.equipment.is_rented = False
        repair.equipment.save()
        
        # Обновляем счет за ремонт
        repair_invoice = repair.invoices.first()
        if repair_invoice:
            repair_invoice.amount = repair_cost
            repair_invoice.save()
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Завершен ремонт оборудования: {repair.equipment.name}"
        )
        
        messages.success(request, 'Ремонт оборудования завершен')
    
    return redirect('dashboard_technician')

@login_required
def send_to_technician(request, equipment_id):
    print(f"DEBUG: send_to_technician called for equipment_id={equipment_id}, method={request.method}", file=sys.stderr)
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'warehouse':
        raise PermissionDenied("Только складские работники могут отправлять оборудование на осмотр")
    
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    if request.method == 'POST':
        print(f"DEBUG: send_to_technician POST for equipment {equipment.name}", file=sys.stderr)
        check = EquipmentCheck.objects.create(
            equipment=equipment,
            status="pending",
            notes="Отправлено на проверку со склада"
        )
        print(f"DEBUG: Created EquipmentCheck: id={check.id}, equipment={check.equipment.name}, status={check.status}", file=sys.stderr)
        
        equipment.needs_repair = True
        equipment.save()
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Оборудование {equipment.name} отправлено на технический осмотр"
        )
        
        messages.success(request, 'Оборудование отправлено на технический осмотр')
    
    return redirect('dashboard_warehouse')

@login_required
def rental_reports(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role not in ['manager', 'admin']:
        raise PermissionDenied("Только менеджеры и администраторы могут просматривать отчеты")
    
    finished_rentals = RentalRequest.objects.filter(status='returned')
    finished_contracts = Contract.objects.filter(rental_request__status='returned')

    equipment_counter = Counter()
    equipment_income = defaultdict(float)
    category_income = defaultdict(float)
    category_count = defaultdict(int)

    for contract in finished_contracts:
        eq = contract.equipment
        equipment_income[eq.name] += float(contract.total_price)
        category_income[eq.category] += float(contract.total_price)
        equipment_counter[eq.name] += 1
        category_count[eq.category] += 1

    equipment_stats = []
    for eq in Equipment.objects.all():
        equipment_stats.append(type('EqStat', (), {
            'name': eq.name,
            'category': eq.category,
            'rental_count': equipment_counter.get(eq.name, 0),
            'total_income': equipment_income.get(eq.name, 0.0)
        }))
    equipment_stats = sorted(equipment_stats, key=lambda x: x.rental_count, reverse=True)

    monthly = defaultdict(lambda: {'total_income': 0, 'contract_count': 0})
    for contract in finished_contracts:
        month = contract.created_at.strftime('%Y-%m')
        monthly[month]['total_income'] += float(contract.total_price)
        monthly[month]['contract_count'] += 1
    monthly_stats = [
        {'month': month, 'total_income': data['total_income'], 'invoice_count': data['contract_count']}
        for month, data in sorted(monthly.items())
    ]

    total_rentals = finished_rentals.count()
    approved_requests = finished_rentals.count()
    total_income = sum(float(c.total_price) for c in finished_contracts)

    context = {
        'total_rentals': total_rentals,
        'approved_requests': approved_requests,
        'total_income': total_income,
        'equipment_stats': equipment_stats,
        'monthly_stats': monthly_stats,
        'category_income': category_income,
        'category_count': category_count,
        'pending_invoices': Invoice.objects.filter(status='pending').count(),
        'active_contracts': Contract.objects.filter(status='active').count()
    }

    return render(request, 'rental/rental_reports.html', context)

@login_required
def manage_users(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут управлять пользователями")
    
    users = User.objects.all()
    return render(request, 'rental/manage_users.html', {'users': users})

@login_required
def create_user(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут создавать пользователей")
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            role = form.cleaned_data['role']
            phone = form.cleaned_data.get('phone', '')
            
            if role == 'client':
                Client.objects.create(user=user, phone=phone)
            else:
                Employee.objects.create(user=user, role=role, phone=phone)
            
            SystemLog.objects.create(
                user=request.user,
                action=f"Создан новый пользователь: {user.username} с ролью {role}"
            )
            
            messages.success(request, 'Пользователь успешно создан')
            return redirect('manage_users')
    else:
        form = RegistrationForm()
    
    return render(request, 'rental/create_user.html', {'form': form})

@login_required
def system_settings(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут настраивать систему")
    
    if request.method == 'POST':
        # Здесь можно добавить обработку настроек системы
        messages.success(request, 'Настройки системы обновлены')
        return redirect('system_settings')
    
    return render(request, 'rental/system_settings.html')

@login_required
def system_logs(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут просматривать системные логи")
    
    logs = SystemLog.objects.all().order_by('-timestamp')
    return render(request, 'rental/system_logs.html', {'logs': logs})

@login_required
def download_db_backup(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут скачивать резервные копии")
    db_path = settings.DATABASES['default']['NAME']
    if not os.path.exists(db_path):
        return HttpResponse('Файл базы данных не найден', status=404)
    with open(db_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="db.sqlite3"'
        return response

@login_required
@require_POST
def backup_database(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут восстанавливать базу данных")
    backup_file = request.FILES.get('backup_file')
    if not backup_file:
        messages.error(request, 'Файл не выбран')
        return redirect('backup_database')
    db_path = settings.DATABASES['default']['NAME']
    with open(db_path, 'wb') as f:
        for chunk in backup_file.chunks():
            f.write(chunk)
    messages.success(request, 'База данных успешно восстановлена!')
    return redirect('backup_database')

@login_required
def backup_database_get(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'admin':
        raise PermissionDenied("Только администраторы могут создавать резервные копии")
    return render(request, 'rental/backup_database.html')

@login_required
def manage_table(request, table_name):
    model_tuple = MODEL_MAP.get(table_name)
    if not model_tuple:
        return HttpResponse("Недопустимое имя таблицы.", status=404)

    model, localized_name = model_tuple
    search_query = request.GET.get('search', '').strip()
    objects = model.objects.all()

    if search_query:
        filters = Q()
        for field in model._meta.fields:
            if isinstance(field, (CharField, TextField)):
                filters |= Q(**{f"{field.name}__icontains": search_query})
        objects = objects.filter(filters)

    return render(request, 'rental/manage_table.html', {
        'table_name': table_name,
        'localized_name': localized_name,
        'objects': objects,
        'fields': [field.verbose_name for field in model._meta.fields],
        'field_names': [field.name for field in model._meta.fields],
        'search_query': search_query,
    })

@login_required
def add_object(request, table_name):
    model_tuple = MODEL_MAP.get(table_name)
    if not model_tuple:
        return JsonResponse({'error': 'Invalid table name'}, status=400)

    model, localized_name = model_tuple
    form_class = modelform_factory(model, fields="__all__")
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save()
            return redirect('manage_table', table_name=table_name)
    
    return render(request, 'rental/add_object.html', {
        'form': form_class(),
        'table_name': localized_name,
    })

@login_required
def edit_object(request, table_name, object_id):
    model_tuple = MODEL_MAP.get(table_name)
    if not model_tuple:
        return HttpResponse("Недопустимое имя таблицы.", status=404)

    model, localized_name = model_tuple
    obj = get_object_or_404(model, pk=object_id)
    form_class = modelform_factory(model, fields="__all__")
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('manage_table', table_name=table_name)
    
    return render(request, 'rental/edit_object.html', {
        'form': form_class(instance=obj),
        'table_name': localized_name,
    })

@login_required
def delete_object(request, table_name, object_id):
    model_tuple = MODEL_MAP.get(table_name)
    if not model_tuple:
        return JsonResponse({'error': 'Invalid table name'}, status=400)

    model, localized_name = model_tuple
    obj = get_object_or_404(model, pk=object_id)
    obj.delete()
    return redirect('manage_table', table_name=table_name)

@login_required
def repair_history(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'technician':
        raise PermissionDenied("Только технические специалисты могут просматривать историю ремонтов")
    
    repairs = EquipmentRepair.objects.filter(technician=request.user.employee).order_by('-created_at')
    return render(request, 'rental/repair_history.html', {'repairs': repairs})

@login_required
def debug_all_equipment_checks(request):
    checks = EquipmentCheck.objects.all().select_related('equipment', 'technician')
    lines = [
        f"id={c.id} | equipment={c.equipment.name} | status={c.status} | technician={c.technician.user.username if c.technician else 'None'}"
        for c in checks
    ]
    return HttpResponse('<br>'.join(lines) or 'No EquipmentCheck in DB')

@csrf_exempt
@login_required
def perform_equipment_repair(request, check_id):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'technician':
        return JsonResponse({'success': False, 'error': 'Доступ запрещён'}, status=403)
    try:
        equipment_check = EquipmentCheck.objects.get(id=check_id)
    except EquipmentCheck.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Проверка не найдена'}, status=404)
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            description = data.get('description', '').strip()
            cost = float(data.get('cost', 0))
        except Exception:
            return JsonResponse({'success': False, 'error': 'Некорректные данные'}, status=400)
        repair = EquipmentRepair.objects.create(
            equipment=equipment_check.equipment,
            technician=request.user.employee,
            description=description,
            repair_cost=cost,
            status='completed'
        )
        repair.completed_at = timezone.now()
        repair.save()
        equipment_check.status = 'repaired'
        equipment_check.technician = request.user.employee
        equipment_check.notes = description
        equipment_check.save()
        equipment_check.equipment.needs_repair = False
        equipment_check.equipment.is_rented = False
        equipment_check.equipment.save()
        return JsonResponse({'success': True, 'message': 'Ремонт завершён и сохранён!'})
    return JsonResponse({'success': False, 'error': 'Только POST-запрос'}, status=405)

@login_required
def client_contracts(request):
    if not hasattr(request.user, 'client'):
        return redirect('dashboard')
    contracts = Contract.objects.filter(client=request.user.client).select_related('equipment')
    return render(request, 'rental/client_contracts.html', {'contracts': contracts})

@login_required
def client_invoices(request):
    if not hasattr(request.user, 'client'):
        return redirect('dashboard')
    invoices = Invoice.objects.filter(contract__client=request.user.client).select_related('contract', 'contract__equipment')
    return render(request, 'rental/client_invoices.html', {'invoices': invoices})

@login_required
def client_repair_invoices(request):
    if not hasattr(request.user, 'client'):
        return redirect('dashboard')
    repair_invoices = RepairInvoice.objects.filter(repair__equipment__rentalrequest__client=request.user.client).select_related('repair', 'repair__equipment')
    return render(request, 'rental/client_repair_invoices.html', {'repair_invoices': repair_invoices})

@login_required
def pay_invoice(request, invoice_id):
    if not hasattr(request.user, 'client'):
        return redirect('dashboard')
    invoice = get_object_or_404(Invoice, id=invoice_id, contract__client=request.user.client)
    if request.method == 'POST' and invoice.status == 'pending':
        invoice.status = 'paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        return JsonResponse({'success': True, 'message': 'Счет оплачен!'})
    return JsonResponse({'success': False, 'error': 'Некорректный запрос'})

@login_required
def pay_repair_invoice(request, invoice_id):
    if not hasattr(request.user, 'client'):
        return redirect('dashboard')
    invoice = get_object_or_404(RepairInvoice, id=invoice_id, repair__equipment__rentalrequest__client=request.user.client)
    if request.method == 'POST' and invoice.status == 'pending':
        invoice.status = 'paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        return JsonResponse({'success': True, 'message': 'Счет за ремонт оплачен!'})
    return JsonResponse({'success': False, 'error': 'Некорректный запрос'})

def public_catalog_view(request):
    if not request.user.is_authenticated:
        return render(request, 'rental/public_catalog.html')
    else:
        return redirect('equipment_list')

@login_required
def download_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if hasattr(request.user, 'client') and contract.client != request.user.client:
        return HttpResponse('Нет доступа', status=403)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=contract_{contract.id}.pdf'
    p = canvas.Canvas(response, pagesize=A4)
    p.setFont('DejaVuSans', 16)
    p.drawString(100, 800, f"Договор аренды №{contract.id}")
    p.setFont('DejaVuSans', 12)
    p.drawString(100, 780, f"Оборудование: {contract.equipment.name}")
    p.drawString(100, 760, f"Период: {contract.start_date} — {contract.end_date}")
    p.drawString(100, 740, f"Клиент: {contract.client.user.get_full_name()} ({contract.client.user.username})")
    p.drawString(100, 720, f"Сумма: {contract.total_price} руб.")
    p.drawString(100, 700, f"Статус: {contract.get_status_display()}")
    p.showPage()
    p.save()
    return response

@login_required
def download_repair_invoice(request, invoice_id):
    invoice = get_object_or_404(RepairInvoice, id=invoice_id)
    if hasattr(request.user, 'client') and invoice.repair.equipment.rentalrequest_set.first().client != request.user.client:
        return HttpResponse('Нет доступа', status=403)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=repair_invoice_{invoice.id}.pdf'
    p = canvas.Canvas(response, pagesize=A4)
    p.setFont('DejaVuSans', 16)
    p.drawString(100, 800, f"Счет за ремонт №{invoice.id}")
    p.setFont('DejaVuSans', 12)
    p.drawString(100, 780, f"Оборудование: {invoice.repair.equipment.name}")
    p.drawString(100, 760, f"Описание ремонта: {invoice.repair.description}")
    p.drawString(100, 740, f"Сумма: {invoice.amount} руб.")
    p.drawString(100, 720, f"Статус: {invoice.get_status_display()}")
    p.showPage()
    p.save()
    return response