from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Doctor, Nurse, Patient,
    OPDVisit, OPDVitalSign, OPDConsultation, OPDPrescriptionItem,
    LabCategory, LabTest, LabTestParameter, LabRequest, LabRequestItem, LabResult, LabResultItem,
    Invoice, InvoiceItem, PaymentTransaction,
    Staff, StaffAttendance, StaffLeave, StaffPayroll,
    HospitalSetting
)

# Isticmaal UserAdmin si aadan u helin qaladka 'AlreadyRegistered'
admin.site.register(User, UserAdmin)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Patient)

# Billing Admin
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'doctor', 'billing_date', 'total_amount', 'paid_amount', 'balance_due', 'status')
    list_filter = ('status', 'payment_method', 'billing_date')
    search_fields = ('invoice_number', 'patient__name', 'patient__phone')
    inlines = [InvoiceItemInline, PaymentTransactionInline]

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'invoice', 'amount', 'payment_method', 'reference_number', 'payment_date', 'received_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('transaction_id', 'reference_number', 'invoice__invoice_number')


# OPD Admin
class OPDVitalSignInline(admin.StackedInline):
    model = OPDVitalSign
    extra = 0

class OPDPrescriptionItemInline(admin.TabularInline):
    model = OPDPrescriptionItem
    extra = 1

@admin.register(OPDVisit)
class OPDVisitAdmin(admin.ModelAdmin):
    list_display = ('visit_number', 'token_number', 'patient', 'doctor', 'visit_type', 'status', 'payment_status', 'visit_date')
    list_filter = ('status', 'visit_type', 'payment_status', 'visit_date')
    search_fields = ('visit_number', 'patient__name', 'patient__phone')
    inlines = [OPDVitalSignInline]

@admin.register(OPDVitalSign)
class OPDVitalSignAdmin(admin.ModelAdmin):
    list_display = ('visit', 'blood_pressure', 'temperature', 'pulse_rate', 'respiratory_rate', 'oxygen_saturation', 'weight', 'bmi')

@admin.register(OPDConsultation)
class OPDConsultationAdmin(admin.ModelAdmin):
    list_display = ('visit', 'doctor', 'diagnosis', 'outcome', 'consultation_date')
    search_fields = ('visit__visit_number', 'visit__patient__name', 'diagnosis')
    inlines = [OPDPrescriptionItemInline]


class LabTestParameterInline(admin.TabularInline):
    model = LabTestParameter
    extra = 1

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'sample_type', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'code')
    inlines = [LabTestParameterInline]

@admin.register(LabCategory)
class LabCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

class LabRequestItemInline(admin.TabularInline):
    model = LabRequestItem
    extra = 1

@admin.register(LabRequest)
class LabRequestAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'patient', 'doctor', 'priority', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'priority', 'payment_status')
    search_fields = ('order_number', 'patient__name')
    inlines = [LabRequestItemInline]

class LabResultItemInline(admin.TabularInline):
    model = LabResultItem
    extra = 1

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('request', 'test', 'technician', 'performed_at', 'is_abnormal')
    list_filter = ('is_abnormal',)
    inlines = [LabResultItemInline]


# HR & Staff Admin
class StaffAttendanceInline(admin.TabularInline):
    model = StaffAttendance
    extra = 0

class StaffLeaveInline(admin.TabularInline):
    model = StaffLeave
    extra = 0

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'department', 'designation', 'shift', 'phone', 'salary', 'status')
    list_filter = ('department', 'status', 'shift', 'gender')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__username', 'phone', 'designation')
    inlines = [StaffAttendanceInline, StaffLeaveInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Shaqaalaha (Name)'

@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'status', 'check_in', 'check_out', 'recorded_by')
    list_filter = ('status', 'date')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'staff__employee_id')

@admin.register(StaffLeave)
class StaffLeaveAdmin(admin.ModelAdmin):
    list_display = ('staff', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on', 'approved_by')
    list_filter = ('leave_type', 'status')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'staff__employee_id', 'reason')

@admin.register(StaffPayroll)
class StaffPayrollAdmin(admin.ModelAdmin):
    list_display = ('payroll_number', 'staff', 'salary_month', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('payroll_number', 'staff__user__first_name', 'staff__user__last_name', 'staff__employee_id', 'reference_number')


@admin.register(HospitalSetting)
class HospitalSettingAdmin(admin.ModelAdmin):
    list_display = ('hospital_name', 'phone', 'email', 'currency_symbol', 'tax_percentage', 'updated_at')


