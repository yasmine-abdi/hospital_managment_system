"""
URL configuration for hospital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from hospital.views import login_view, dashboard_view
from django.contrib.auth.views import LogoutView # Import-garee LogoutView
from hospital.views import add_patient_view, patient_list_view
from hospital import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/'), name='home'),
    path('login/', login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('add-patient/', add_patient_view, name='add_patient'),
    path('patient-list/', patient_list_view, name='patient_list'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/create/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/update/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/update/', views.appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),

    # Pharmacy URLs
    path('pharmacy/medicines/', views.medicine_list, name='medicine_list'),
    path('pharmacy/medicines/create/', views.medicine_create, name='medicine_create'),
    path('pharmacy/medicines/<int:pk>/update/', views.medicine_update, name='medicine_update'),
    path('pharmacy/medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    
    path('pharmacy/sales/', views.pharmacy_sale_list, name='pharmacy_sale_list'),
    path('pharmacy/sales/create/', views.pharmacy_sale_create, name='pharmacy_sale_create'),
    path('pharmacy/sales/<int:pk>/', views.pharmacy_sale_detail, name='pharmacy_sale_detail'),

    # Inpatient (IPD) URLs
    path('ipd/admissions/', views.admission_list, name='admission_list'),
    path('ipd/admissions/create/', views.admission_create, name='admission_create'),
    path('ipd/admissions/<int:pk>/update/', views.admission_update, name='admission_update'),
    path('ipd/admissions/<int:pk>/discharge/', views.discharge_patient, name='discharge_patient'),
    path('ipd/beds/', views.bed_list, name='bed_list'),
    path('ipd/beds/create/', views.bed_create, name='bed_create'),
    path('ipd/wards/create/', views.ward_create, name='ward_create'),

    # Laboratory (LIS) URLs
    path('laboratory/', views.lab_dashboard, name='lab_dashboard'),
    path('laboratory/requests/', views.lab_request_list, name='lab_request_list'),
    path('laboratory/requests/create/', views.lab_request_create, name='lab_request_create'),
    path('laboratory/requests/<int:pk>/', views.lab_request_detail, name='lab_request_detail'),
    path('laboratory/requests/<int:pk>/collect-sample/', views.lab_sample_collect, name='lab_sample_collect'),
    path('laboratory/requests/<int:pk>/enter-results/', views.lab_result_entry, name='lab_result_entry'),
    path('laboratory/requests/<int:pk>/report/', views.lab_report_view, name='lab_report_view'),
    path('laboratory/results/', views.lab_result_list, name='lab_result_list'),
    path('laboratory/catalog/', views.lab_test_catalog, name='lab_test_catalog'),
    path('laboratory/tests/create/', views.lab_test_create, name='lab_test_create'),
    path('laboratory/tests/<int:pk>/update/', views.lab_test_update, name='lab_test_update'),
    path('laboratory/categories/create/', views.lab_category_create, name='lab_category_create'),

    # Outpatient Department (OPD) URLs
    path('opd/', views.opd_dashboard, name='opd_dashboard'),
    path('opd/visits/', views.opd_visit_list, name='opd_visit_list'),
    path('opd/visits/create/', views.opd_visit_create, name='opd_visit_create'),
    path('opd/visits/<int:pk>/', views.opd_visit_detail, name='opd_visit_detail'),
    path('opd/visits/<int:pk>/vitals/', views.opd_vitals_record, name='opd_vitals_record'),
    path('opd/visits/<int:pk>/consult/', views.opd_consultation_view, name='opd_consultation_view'),
    path('opd/visits/<int:pk>/prescription/', views.opd_prescription_print, name='opd_prescription_print'),

    # Billing & Finance URLs
    path('billing/', views.billing_dashboard, name='billing_dashboard'),
    path('billing/invoices/', views.invoice_list, name='invoice_list'),
    path('billing/invoices/create/', views.invoice_create, name='invoice_create'),
    path('billing/invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('billing/invoices/<int:pk>/payment/', views.payment_record, name='payment_record'),
    path('billing/invoices/<int:pk>/print/', views.invoice_print, name='invoice_print'),
    path('billing/payments/', views.payment_list, name='payment_list'),

    # HR & Staff Management URLs
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/staff/', views.staff_list, name='staff_list'),
    path('hr/staff/create/', views.staff_create, name='staff_create'),
    path('hr/staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('hr/staff/<int:pk>/update/', views.staff_update, name='staff_update'),
    path('hr/staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    path('hr/attendance/', views.attendance_list, name='attendance_list'),
    path('hr/attendance/mark/', views.attendance_mark, name='attendance_mark'),
    path('hr/leaves/', views.leave_list, name='leave_list'),
    path('hr/leaves/create/', views.leave_create, name='leave_create'),
    path('hr/leaves/<int:pk>/<str:action>/', views.leave_action, name='leave_action'),
    path('hr/payroll/', views.payroll_list, name='payroll_list'),
    path('hr/payroll/create/', views.payroll_create, name='payroll_create'),
    path('hr/payroll/<int:pk>/print/', views.payroll_print, name='payroll_print'),

    # Reports & Analytics URLs
    path('reports/', views.reports_hub, name='reports_hub'),
    path('reports/financial/', views.report_financial, name='report_financial'),
    path('reports/patients/', views.report_patients, name='report_patients'),
    path('reports/laboratory/', views.report_laboratory, name='report_laboratory'),
    path('reports/pharmacy/', views.report_pharmacy, name='report_pharmacy'),
    path('reports/hr/', views.report_hr, name='report_hr'),

    # Settings & Backup URLs
    path('settings/', views.settings_general, name='settings_general'),
    path('settings/hospital/', views.settings_hospital, name='settings_hospital'),
    path('settings/password/', views.settings_password, name='settings_password'),
    path('settings/backup/', views.settings_backup, name='settings_backup'),
    path('settings/backup/create/', views.backup_create, name='backup_create'),
    path('settings/backup/download/<str:filename>/', views.backup_download, name='backup_download'),
    path('settings/backup/delete/<str:filename>/', views.backup_delete, name='backup_delete'),

    # Users & Roles Management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    path('users/<int:pk>/toggle/', views.user_toggle_status, name='user_toggle_status'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
]

if settings.DEBUG or True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

