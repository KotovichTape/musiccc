from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('catalog/', views.catalog_view, name='catalog'),
    path('rental-history/', views.rental_history_view, name='rental_history'),
    path('create-rental-request/<int:equipment_id>/', views.create_rental_request, name='create_rental_request'),
    path('rental-request/<int:request_id>/', views.rental_request_detail, name='rental_request_detail'),
    
    path('manager/dashboard/', views.dashboard_manager, name='dashboard_manager'),
    path('manager/approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('manager/reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('manager/reports/', views.rental_reports, name='rental_reports'),
    
    path('warehouse/dashboard/', views.dashboard_warehouse, name='dashboard_warehouse'),
    path('warehouse/issue-equipment/<int:rental_id>/', views.issue_equipment, name='issue_equipment'),
    path('warehouse/return-equipment/<int:rental_id>/', views.return_equipment, name='return_equipment'),
    path('warehouse/send-to-technician/<int:equipment_id>/', views.send_to_technician, name='send_to_technician'),
    
    path('technician/dashboard/', views.dashboard_technician, name='dashboard_technician'),
    path('technician/check-equipment/<int:check_id>/', views.perform_equipment_check, name='perform_equipment_check'),
    path('technician/complete-repair/<int:repair_id>/', views.complete_equipment_repair, name='complete_equipment_repair'),
    path('technician/repair-history/', views.repair_history, name='repair_history'),
    
    path('admin/manage-users/', views.manage_users, name='manage_users'),
    path('admin/create-user/', views.create_user, name='create_user'),
    path('admin/system-settings/', views.system_settings, name='system_settings'),
    path('admin/system-logs/', views.system_logs, name='system_logs'),
    path('panel/backup-database/', views.backup_database_get, name='backup_database'),
    path('panel/backup-database/restore/', views.backup_database, name='restore_database'),
    path('panel/backup-database/download/', views.download_db_backup, name='download_db_backup'),
    
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('debug-all-equipment-checks/', views.debug_all_equipment_checks, name='debug_all_equipment_checks'),
    path('perform-equipment-repair/<int:check_id>/', views.perform_equipment_repair, name='perform_equipment_repair'),
    path('client/contracts/', views.client_contracts, name='client_contracts'),
    path('client/invoices/', views.client_invoices, name='client_invoices'),
    path('client/repair-invoices/', views.client_repair_invoices, name='client_repair_invoices'),
    path('client/pay-invoice/<int:invoice_id>/', views.pay_invoice, name='pay_invoice'),
    path('client/pay-repair-invoice/<int:invoice_id>/', views.pay_repair_invoice, name='pay_repair_invoice'),
    path('equipment/', views.equipment_list_view, name='equipment_list'),
    path('public-catalog/', views.public_catalog_view, name='public_catalog'),
    path('client/contract-download/<int:contract_id>/', views.download_contract, name='download_contract'),
    path('client/repair-invoice-download/<int:invoice_id>/', views.download_repair_invoice, name='download_repair_invoice'),
] 