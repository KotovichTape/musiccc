from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Client, Employee, RentalRequest, Contract, Invoice,
    EquipmentCheck, EquipmentRepair, RepairInvoice
)

class SimpleUserCreationForm(forms.ModelForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    phone = forms.CharField(label='Телефон', max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'phone')

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
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

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
