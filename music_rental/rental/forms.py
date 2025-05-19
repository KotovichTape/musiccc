from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Client, Employee, RentalRequest, Contract, Invoice,
    EquipmentCheck, EquipmentRepair, RepairInvoice
)
import re
from django.core.exceptions import ValidationError

class SimpleUserCreationForm(forms.ModelForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    phone = forms.CharField(label='Телефон', max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'phone')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Проверка минимальной длины
        if len(password) < 8:
            raise ValidationError('Пароль должен содержать не менее 8 символов.')
        
        # Проверка наличия хотя бы одной цифры
        if not re.search(r'\d', password):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру.')
        
        # Проверка наличия хотя бы одной буквы в верхнем регистре
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву.')
        
        # Проверка наличия хотя бы одной буквы в нижнем регистре
        if not re.search(r'[a-z]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну строчную букву.')
        
        # Проверка наличия хотя бы одного специального символа
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Пароль должен содержать хотя бы один специальный символ (!@#$%^&*(),.?":{}|<>).')
        
        return password

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        return user

class RegistrationForm(SimpleUserCreationForm):
    pass

class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(
        label='Пароль', 
        widget=forms.PasswordInput,
        help_text='Пароль должен содержать не менее 8 символов, включая цифры, заглавные и строчные буквы, и специальные символы.'
    )

class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['start_date', 'end_date', 'total_price', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['amount', 'due_date', 'payment_method', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class EquipmentCheckForm(forms.ModelForm):
    class Meta:
        model = EquipmentCheck
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class EquipmentRepairForm(forms.ModelForm):
    class Meta:
        model = EquipmentRepair
        fields = ['description', 'repair_cost']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RepairInvoiceForm(forms.ModelForm):
    class Meta:
        model = RepairInvoice
        fields = ['amount', 'due_date', 'payment_method', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client  
        fields = ['phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance, Employee):
            self.Meta.model = Employee  
            self.fields['role'] = forms.ChoiceField(choices=Employee.ROLE_CHOICES, required=False)

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['phone']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['role', 'phone']
