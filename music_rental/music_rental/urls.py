from django.contrib import admin
from django.urls import path, include
from rental.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rental.urls')),  # Include rental app URLs
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    path('', home_view, name='home'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('logs/', logs_view, name='logs'),
    path('catalog/', catalog_view, name='catalog'),
    
    path('equipment/', equipment_list_view, name='equipment_list'),
    path('equipment-checks/', equipment_check_list, name='equipment_check_list'),
    path('add-equipment-check/<int:equipment_id>/', add_equipment_check, name='add_equipment_check'),
    path('add-equipment-repair/<int:equipment_id>/', add_equipment_repair, name='add_equipment_repair'),
    
    path('rental-history/', rental_history_view, name='rental_history'),
    path('create-rental/<int:equipment_id>/', create_rental_request, name='create_rental_request'),
    
    path('manage-requests/', manage_rental_requests, name='manage_rental_requests'),
    path('reports/', rental_reports, name='rental_reports'),
    path('approve-request/<int:request_id>/', approve_request, name='approve_request'),
    path('reject-request/<int:request_id>/', reject_request, name='reject_request'),
    
    path('issue-equipment/<int:rental_id>/', issue_equipment, name='issue_equipment'),
    path('return-equipment/<int:rental_id>/', return_equipment, name='return_equipment'),
    path('send-to-technician/<int:equipment_id>/', send_to_technician, name='send_to_technician'),
    
    path('dashboard/technician/', dashboard_technician, name='dashboard_technician'),
    path('perform-equipment-check/<int:check_id>/', perform_equipment_check, name='perform_equipment_check'),
    path('complete-repair/<int:repair_id>/', complete_equipment_repair, name='complete_equipment_repair'),
    
    path('manage/<str:table_name>/', manage_table, name='manage_table'),
    path('manage/<str:table_name>/add/', add_object, name='add_object'),
    path('manage/<str:table_name>/edit/<int:object_id>/', edit_object, name='edit_object'),
    path('manage/<str:table_name>/delete/<int:object_id>/', delete_object, name='delete_object'),
    path('manage-users/', manage_users, name='manage_users'),
    path('create-user/', create_user, name='create_user'),
    path('system-settings/', system_settings, name='system_settings'),
    path('system-logs/', system_logs, name='system_logs'),
    path('backup-database/', backup_database_get, name='backup_database'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)