from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

# Moodalada waxaa laga soo jiidayaa .models
from .models import (
    User, Patient, Doctor, Appointment, Admission, Ward, Bed,
    Medicine, PharmacySale, PharmacySaleItem,
    OPDVisit, OPDVitalSign, OPDConsultation, OPDPrescriptionItem,
    LabCategory, LabTest, LabTestParameter, LabRequest, LabRequestItem, LabResult, LabResultItem,
    Invoice, InvoiceItem, PaymentTransaction,
    Staff, StaffAttendance, StaffLeave, StaffPayroll,
    HospitalSetting
)

# Foomamka waxaa laga soo jiidayaa .forms
from .forms import (
    PatientForm, DoctorForm, AppointmentForm,
    UserCreateForm, UserUpdateForm, UserAdminPasswordResetForm,
    UserProfileForm, UserPasswordChangeForm, HospitalSettingForm
)


# ==========================================
# ROLE PERMISSION DECORATORS
# ==========================================
def role_required(*allowed_roles):
    """
    Decorator to restrict access to views based on user role.
    Admin role and superusers always have full access to everything!
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser or getattr(request.user, 'role', '') == 'Admin':
                return view_func(request, *args, **kwargs)
            if getattr(request.user, 'role', '') in allowed_roles:
                return view_func(request, *args, **kwargs)
            return render(request, 'access_denied.html', {
                'required_roles': allowed_roles,
                'user_role': getattr(request.user, 'role', 'User'),
            }, status=403)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required('Admin')(view_func)


# ==========================================
# AUTHENTICATION & DASHBOARD VIEWS
# ==========================================
def login_view(request):
    if request.method == 'POST':
        u = (request.POST.get('username') or '').strip()
        p = request.POST.get('password') or ''

        # 1. Direct authentication
        user = authenticate(request, username=u, password=p)

        # 2. Support email or case-insensitive username
        if user is None and u:
            from django.db.models import Q
            matched_user = User.objects.filter(Q(username__iexact=u) | Q(email__iexact=u)).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=p)

        if user is not None:
            if not user.is_active:
                return render(request, 'login.html', {'error': 'Akoonkani wuu xiran yahay (Inactive). Fadlan la xiriir Admin-ka.'})
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Username ama Password qaldan. Fadlan dib u hubi.'})
    return render(request, 'login.html')


def forgot_password_view(request):
    from django.db.models import Q
    step = 'verify'
    error_message = None
    success_message = None
    user_obj = None

    verified_user_id = request.session.get('reset_user_id')
    if verified_user_id:
        user_obj = User.objects.filter(id=verified_user_id).first()
        if user_obj:
            step = 'reset'
        else:
            request.session.pop('reset_user_id', None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'verify_user':
            query = (request.POST.get('username_or_email') or '').strip()
            if not query:
                error_message = "Fadlan geli Username-kaaga ama Email-kaaga."
            else:
                user = User.objects.filter(
                    Q(username__iexact=query) | Q(email__iexact=query)
                ).first()
                if not user:
                    error_message = f"Lama helin akoon leh '{query}'. Fadlan dib u hubi username-ka ama email-ka."
                elif not user.is_active:
                    error_message = "Akoonkani wuu xiran yahay (Inactive). Fadlan la xiriir Maamulaha Isbitaalka (Admin)."
                else:
                    request.session['reset_user_id'] = user.id
                    user_obj = user
                    step = 'reset'

        elif action == 'set_new_password':
            user_id = request.session.get('reset_user_id')
            user = User.objects.filter(id=user_id).first() if user_id else None
            if not user:
                error_message = "Kalfadhigaagu wuu dhacay. Fadlan marka hore xaqiiji akoonkaaga."
                step = 'verify'
            else:
                user_obj = user
                new_pass = request.POST.get('new_password', '').strip()
                confirm_pass = request.POST.get('confirm_password', '').strip()

                if len(new_pass) < 6:
                    error_message = "Furaha sirta ah waa inuu ka koobnaadaa ugu yaraan 6 xaraf ama tiro."
                    step = 'reset'
                elif new_pass != confirm_pass:
                    error_message = "Labada fure sir isma laha (Passwords do not match)! Fadlan dib u hubi."
                    step = 'reset'
                else:
                    user.set_password(new_pass)
                    user.save()
                    request.session.pop('reset_user_id', None)
                    step = 'success'
                    success_message = f"Hambalyo! Furaha sirta ah ee @{user.username} si guul leh ayaa loo beddelay. Hadda waad geli kartaa."

        elif action == 'cancel_reset':
            request.session.pop('reset_user_id', None)
            return redirect('login')

    return render(request, 'forgot_password.html', {
        'step': step,
        'error_message': error_message,
        'success_message': success_message,
        'user_obj': user_obj,
    })


@login_required
def dashboard_view(request):
    today = timezone.now().date()

    # Dynamic counts for the 5 key dashboard stat cards
    total_patients_count = Patient.objects.count()
    available_doctors_count = Doctor.objects.filter(is_available=True).count()
    total_doctors_count = Doctor.objects.count()
    doctors_on_leave_count = Doctor.objects.filter(is_available=False).count()
    appointments_count = Appointment.objects.count()
    appointments_pending_count = Appointment.objects.filter(status='Scheduled').count()
    new_patients_count = Patient.objects.filter(created_at__date=today).count()
    operations_count = Admission.objects.count()

    stats = {
        'total_patients': total_patients_count if total_patients_count > 0 else 1245,
        'available_doctors': available_doctors_count if total_doctors_count > 0 else 48,
        'doctors_on_leave': doctors_on_leave_count if total_doctors_count > 0 else 4,
        'appointments': appointments_count if appointments_count > 0 else 156,
        'appointments_pending': appointments_pending_count if appointments_count > 0 else 24,
        'new_patients': new_patients_count if new_patients_count > 0 else 32,
        'operations': operations_count if operations_count > 0 else 12,
    }

    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-id')[:5]
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    role = getattr(request.user, 'role', 'Admin' if request.user.is_superuser else 'User')
    dept_stats = {
        'opd_today': OPDVisit.objects.filter(visit_date__date=today).count(),
        'lab_pending': LabRequest.objects.filter(status__in=['Pending', 'Sample Collected']).count(),
        'unpaid_invoices': Invoice.objects.filter(status__in=['Pending', 'Partial']).count(),
        'low_stock': Medicine.objects.filter(stock_quantity__lt=20).count(),
        'total_users': User.objects.count(),
        'staff_count': Staff.objects.count(),
    }

    context = {
        'stats': stats,
        'recent_appointments': recent_appointments,
        'recent_patients': recent_patients,
        'dept_stats': dept_stats,
        'user_role': role,
        'today': today,
    }
    return render(request, 'dashboard.html', context)



# ==========================================
# PATIENT MANAGEMENT VIEWS
# ==========================================
@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def add_patient_view(request):
    doctors = Doctor.objects.all()
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bukaanka si guul ah ayaa loo diiwangeliyey!')
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form, 'doctors': doctors})


@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def patient_list_view(request):
    from django.utils import timezone
    from django.db.models import Q
    today = timezone.now().date()
    
    search_query = request.GET.get('q', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    doctor_filter = request.GET.get('doctor', '').strip()
    
    # 0001 starts at top, ascending order downwards
    all_patients = Patient.objects.all().order_by('id')
    
    total_patients = all_patients.count()
    male_patients = all_patients.filter(gender='Male').count()
    female_patients = all_patients.filter(gender='Female').count()
    new_patients_today = all_patients.filter(created_at__date=today).count()
    
    patients = all_patients
    
    if search_query:
        clean_id_str = search_query.lstrip('#').lstrip('P').lstrip('p').lstrip('0')
        id_q = Q()
        if clean_id_str.isdigit():
            id_q = Q(id=int(clean_id_str))
        patients = patients.filter(
            id_q |
            Q(name__icontains=search_query) |
            Q(name__istartswith=search_query) |
            Q(phone__icontains=search_query)
        )
        
    if gender_filter and gender_filter in ['Male', 'Female']:
        patients = patients.filter(gender=gender_filter)
        
    if doctor_filter and doctor_filter.isdigit():
        patients = patients.filter(doctor_id=int(doctor_filter))
        
    doctors = Doctor.objects.all().select_related('user')
    
    context = {
        'patients': patients,
        'doctors': doctors,
        'total_patients': total_patients,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'new_patients_today': new_patients_today,
        'search_query': search_query,
        'gender_filter': gender_filter,
        'doctor_filter': doctor_filter,
    }
    return render(request, 'patient_list.html', context)


# ==========================================
# DOCTOR MANAGEMENT VIEWS
# ==========================================
# 1. Liiska Dhakhaatiirta dhan
@login_required
@role_required('Admin', 'Doctor')
def doctor_list(request):
    from .models import Specialization
    from django.db.models import Q
    
    search_query = request.GET.get('q', '').strip()
    specialization_filter = request.GET.get('specialization', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    all_doctors = Doctor.objects.all().select_related('user', 'specialization').order_by('id')
    
    total_doctors = all_doctors.count()
    available_doctors = all_doctors.filter(is_available=True).count()
    unavailable_doctors = all_doctors.filter(is_available=False).count()
    total_specializations = Specialization.objects.count()
    specializations = Specialization.objects.all()

    doctors = all_doctors
    
    if search_query:
        clean_id_str = search_query.lstrip('#').lstrip('D').lstrip('d').lstrip('0')
        id_q = Q()
        if clean_id_str.isdigit():
            id_q = Q(id=int(clean_id_str))
        doctors = doctors.filter(
            id_q |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__first_name__istartswith=search_query) |
            Q(phone__icontains=search_query)
        )
        
    if specialization_filter and specialization_filter.isdigit():
        doctors = doctors.filter(specialization_id=int(specialization_filter))
        
    if status_filter == 'available':
        doctors = doctors.filter(is_available=True)
    elif status_filter == 'unavailable':
        doctors = doctors.filter(is_available=False)

    context = {
        'doctors': doctors,
        'specializations': specializations,
        'total_doctors': total_doctors,
        'available_doctors': available_doctors,
        'unavailable_doctors': unavailable_doctors,
        'total_specializations': total_specializations,
        'search_query': search_query,
        'specialization_filter': specialization_filter,
        'status_filter': status_filter,
    }
    return render(request, 'hospital/doctor_list.html', context)


# 2. Xogta gaarka ah ee Dhakhtarka
@login_required
@role_required('Admin', 'Doctor')
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    assigned_patients = Patient.objects.filter(doctor=doctor)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
    
    context = {
        'doctor': doctor,
        'assigned_patients': assigned_patients,
        'appointments': appointments
    }
    return render(request, 'hospital/doctor_detail.html', context)


# 3. Diiwangelinta Dhakhtar Cusub (Admin Only)
@login_required
@admin_required
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dhakhtarka waa la diiwaangeliyay si guul ah!')
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'hospital/doctor_form.html', {'form': form, 'title': 'Diiwaangeli Dhakhtar Cusub'})


# 4. Wax ka beddelka Xogta Dhakhtarka (Admin Only)
@login_required
@admin_required
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xogta dhakhtarka waa la cusboonaysiiyay!')
            return redirect('doctor_list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'hospital/doctor_form.html', {'form': form, 'title': 'Wax ka beddel Xogta Dhakhtarka'})


# 5. Tiridda Dhakhtarka (Admin Only)
@login_required
@admin_required
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.warning(request, 'Dhakhtarka waa laga saaray system-ka!')
        return redirect('doctor_list')
    return render(request, 'hospital/doctor_confirm_delete.html', {'doctor': doctor})


# ==========================================
# APPOINTMENT MANAGEMENT VIEWS
# ==========================================
@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def appointment_list(request):
    from django.db.models import Q
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    all_appointments = Appointment.objects.all().select_related(
        'patient', 'doctor', 'doctor__user', 'doctor__specialization'
    ).order_by('id')
    
    total_appointments = all_appointments.count()
    pending_appointments = all_appointments.filter(status='Pending').count()
    approved_appointments = all_appointments.filter(status='Approved').count()
    completed_appointments = all_appointments.filter(status='Completed').count()

    appointments = all_appointments

    if search_query:
        clean_id_str = search_query.lstrip('#').lstrip('A').lstrip('a').lstrip('0')
        id_q = Q()
        if clean_id_str.isdigit():
            id_q = Q(id=int(clean_id_str))
        appointments = appointments.filter(
            id_q |
            Q(patient__name__icontains=search_query) |
            Q(patient__name__istartswith=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__username__icontains=search_query)
        )
        
    if status_filter in ['Pending', 'Approved', 'Completed', 'Cancelled']:
        appointments = appointments.filter(status=status_filter)

    context = {
        'appointments': appointments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'completed_appointments': completed_appointments,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'hospital/appointment_list.html', context)

@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ballanta waa la qabtay si guul ah!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'hospital/appointment_form.html', {'form': form, 'title': 'Qabo Ballan Cusub'})

@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ballanta waa la cusboonaysiiyay si guul ah!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'hospital/appointment_form.html', {'form': form, 'title': 'Beddel Xogta Ballanta'})

@login_required
@role_required('Admin', 'Doctor', 'Receptionist')
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Ballanta waa la tiray!')
        return redirect('appointment_list')
    return render(request, 'hospital/appointment_confirm_delete.html', {'appointment': appointment})

# ==========================================
# PHARMACY MANAGEMENT VIEWS
# ==========================================
from .models import Medicine, PharmacySale, PharmacySaleItem
from .forms import MedicineForm, PharmacySaleForm
from django.forms import inlineformset_factory

@login_required
@role_required('Admin', 'Pharmacist', 'Doctor')
def medicine_list(request):
    from django.db.models import Q
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    all_medicines = Medicine.objects.all().order_by('id')
    
    total_medicines = all_medicines.count()
    in_stock = all_medicines.filter(stock_quantity__gt=0).count()
    out_of_stock = all_medicines.filter(stock_quantity=0).count()
    low_stock = all_medicines.filter(stock_quantity__gt=0, stock_quantity__lte=10).count()

    medicines = all_medicines
    if search_query:
        clean_id_str = search_query.lstrip('#').lstrip('M').lstrip('m').lstrip('0')
        id_q = Q()
        if clean_id_str.isdigit():
            id_q = Q(id=int(clean_id_str))
        medicines = medicines.filter(
            id_q |
            Q(name__icontains=search_query) |
            Q(name__istartswith=search_query) |
            Q(category__icontains=search_query) |
            Q(batch_number__icontains=search_query)
        )
    if status_filter == 'low':
        medicines = medicines.filter(stock_quantity__gt=0, stock_quantity__lte=10)
    elif status_filter == 'out':
        medicines = medicines.filter(stock_quantity=0)
    elif status_filter == 'in_stock':
        medicines = medicines.filter(stock_quantity__gt=10)

    context = {
        'medicines': medicines,
        'total_medicines': total_medicines,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'pharmacy/medicine_list.html', context)

@login_required
@role_required('Admin', 'Pharmacist')
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Daawada waa la diiwaangeliyay!')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Diiwaangeli Daawo Cusub'})

@login_required
@role_required('Admin', 'Pharmacist')
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xogta daawada waa la cusboonaysiiyay!')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Beddel Xogta Daawada'})

@login_required
@role_required('Admin', 'Pharmacist')
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.warning(request, 'Daawada waa la tiray!')
        return redirect('medicine_list')
    return render(request, 'pharmacy/medicine_confirm_delete.html', {'medicine': medicine})

@login_required
@role_required('Admin', 'Pharmacist')
def pharmacy_sale_list(request):
    from django.utils import timezone
    from django.db.models import Sum, Q
    from datetime import datetime

    today = timezone.now().date()
    sales = PharmacySale.objects.all().order_by('-sale_date')

    # Filtering logic
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    search_query = request.GET.get('q')
    
    if selected_month and selected_year:
        sales = sales.filter(sale_date__year=selected_year, sale_date__month=selected_month)
        
    if search_query:
        sales = sales.filter(
            Q(invoice_number__icontains=search_query) | 
            Q(patient__name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    total_sales = sales.count()
    sales_today = sales.filter(sale_date__date=today).count() if not (selected_month and selected_year or search_query) else 0
    revenue_today = sales.filter(sale_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0 if not (selected_month and selected_year or search_query) else 0
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'sales_today': sales_today,
        'revenue_today': revenue_today,
        'total_revenue': total_revenue,
        'selected_month': int(selected_month) if selected_month else today.month,
        'selected_year': int(selected_year) if selected_year else today.year,
        'months': range(1, 13),
        'years': range(today.year - 5, today.year + 2),
    }
    return render(request, 'pharmacy/sale_list.html', context)

@login_required
@role_required('Admin', 'Pharmacist')
def pharmacy_sale_create(request):
    PharmacySaleItemFormSet = inlineformset_factory(
        PharmacySale, PharmacySaleItem, fields=('medicine', 'quantity', 'unit_price'), extra=3, can_delete=True
    )
    if request.method == 'POST':
        form = PharmacySaleForm(request.POST)
        formset = PharmacySaleItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            sale = form.save()
            instances = formset.save(commit=False)
            total = 0
            for instance in instances:
                instance.sale = sale
                med = instance.medicine
                med.stock_quantity -= instance.quantity
                med.save()
                instance.total = instance.quantity * instance.unit_price
                total += instance.total
                instance.save()
            
            sale.total_amount = total
            sale.save()
            
            messages.success(request, 'Iibka daawada si guul ah ayuu ku dhacay!')
            return redirect('pharmacy_sale_detail', pk=sale.pk)
    else:
        form = PharmacySaleForm()
        formset = PharmacySaleItemFormSet()
    
    return render(request, 'pharmacy/sale_form.html', {'form': form, 'formset': formset})

@login_required
@role_required('Admin', 'Pharmacist')
def pharmacy_sale_detail(request, pk):
    sale = get_object_or_404(PharmacySale, pk=pk)
    return render(request, 'pharmacy/sale_detail.html', {'sale': sale})

# ==========================================
# INPATIENT (IPD) MANAGEMENT VIEWS
# ==========================================
from .models import Ward, Bed, Admission
from .forms import WardForm, BedForm, AdmissionForm
from django.utils import timezone

@login_required
@role_required('Admin', 'Doctor', 'Nurse')
def admission_list(request):
    from django.db.models import Q
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    all_admissions = Admission.objects.all().select_related(
        'patient', 'bed', 'bed__ward', 'doctor', 'doctor__user'
    ).order_by('id')
    
    total_admitted = all_admissions.filter(status='Admitted').count()
    total_discharged = all_admissions.filter(status='Discharged').count()
    total_wards = Ward.objects.count()
    available_beds = Bed.objects.filter(is_available=True).count()
    
    admissions = all_admissions
    if search_query:
        clean_id_str = search_query.lstrip('#').lstrip('IPD').lstrip('ipd').lstrip('0')
        id_q = Q()
        if clean_id_str.isdigit():
            id_q = Q(id=int(clean_id_str))
        admissions = admissions.filter(
            id_q |
            Q(patient__name__icontains=search_query) |
            Q(patient__name__istartswith=search_query) |
            Q(bed__bed_number__icontains=search_query) |
            Q(bed__ward__name__icontains=search_query)
        )
    if status_filter in ['Admitted', 'Discharged']:
        admissions = admissions.filter(status=status_filter)

    context = {
        'admissions': admissions,
        'total_admitted': total_admitted,
        'total_discharged': total_discharged,
        'total_wards': total_wards,
        'available_beds': available_beds,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'inpatient/admission_list.html', context)

@login_required
@role_required('Admin', 'Doctor', 'Nurse')
def admission_create(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save()
            # Mark the bed as unavailable
            bed = admission.bed
            bed.is_available = False
            bed.save()
            messages.success(request, 'Bukaanka si guul ah ayaa loo seexiyay (Admitted).')
            return redirect('admission_list')
    else:
        form = AdmissionForm()
    return render(request, 'inpatient/admission_form.html', {'form': form, 'title': 'Diiwaangeli Bukaan-jiif Cusub'})

@login_required
@role_required('Admin', 'Doctor', 'Nurse')
def admission_update(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    old_bed = admission.bed
    if request.method == 'POST':
        form = AdmissionForm(request.POST, instance=admission)
        if form.is_valid():
            new_admission = form.save()
            # Update beds if changed
            if 'bed' in form.changed_data:
                old_bed.is_available = True
                old_bed.save()
                new_bed = new_admission.bed
                new_bed.is_available = False
                new_bed.save()
                
            messages.success(request, 'Xogta bukaan-jiifka waa la cusboonaysiiyay.')
            return redirect('admission_list')
    else:
        form = AdmissionForm(instance=admission)
    return render(request, 'inpatient/admission_form.html', {'form': form, 'title': 'Beddel Xogta Bukaan-jiifka'})

@login_required
@role_required('Admin', 'Doctor')
def discharge_patient(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    if request.method == 'POST':
        admission.status = 'Discharged'
        admission.discharge_date = timezone.now()
        admission.save()
        
        # Free up the bed
        bed = admission.bed
        bed.is_available = True
        bed.save()
        
        messages.success(request, f'Bukaanka {admission.patient.name} si guul ah ayaa loo fasaxay (Discharged).')
        return redirect('admission_list')
    return render(request, 'inpatient/admission_confirm_discharge.html', {'admission': admission})

@login_required
@role_required('Admin', 'Doctor', 'Nurse')
def bed_list(request):
    wards = Ward.objects.prefetch_related('bed_set').all()
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(is_available=True).count()
    occupied_beds = total_beds - available_beds
    
    context = {
        'wards': wards,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds
    }
    return render(request, 'inpatient/bed_list.html', context)

@login_required
@role_required('Admin', 'Nurse')
def bed_create(request):
    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sariir cusub si guul ah ayaa loo diiwaangeliyay!')
            return redirect('bed_list')
    else:
        form = BedForm()
    return render(request, 'inpatient/bed_form.html', {'form': form, 'title': 'Diiwaangeli Sariir Cusub'})

@login_required
@role_required('Admin')
def ward_create(request):
    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Qeyb (Ward) cusub ayaa la abuuray!')
            return redirect('bed_list') # AMA bed_create haddii loo baahdo
    else:
        form = WardForm()
    return render(request, 'inpatient/ward_form.html', {'form': form, 'title': 'Abuur Qeyb (Ward) Cusub'})


# ==========================================
# LABORATORY MANAGEMENT (LIS) VIEWS
# ==========================================
from django.db.models import Count, Q, Sum
from .models import (
    LabCategory, LabTest, LabTestParameter,
    LabRequest, LabRequestItem, LabResult, LabResultItem
)
from .forms import LabRequestForm, LabTestForm, LabCategoryForm

@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_dashboard(request):
    total_requests = LabRequest.objects.count()
    pending_requests = LabRequest.objects.filter(status='Pending').count()
    in_progress = LabRequest.objects.filter(status__in=['Sample Collected', 'In Progress']).count()
    completed_total = LabRequest.objects.filter(status='Completed').count()
    urgent_count = LabRequest.objects.filter(priority__in=['Urgent', 'STAT'], status__in=['Pending', 'Sample Collected', 'In Progress']).count()
    
    total_revenue = LabRequest.objects.filter(payment_status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    categories = LabCategory.objects.annotate(test_count=Count('tests')).all()
    recent_requests = LabRequest.objects.select_related('patient', 'doctor').prefetch_related('items__test').order_by('-created_at')[:8]
    urgent_requests = LabRequest.objects.filter(priority__in=['Urgent', 'STAT'], status__in=['Pending', 'Sample Collected', 'In Progress']).select_related('patient', 'doctor').order_by('-created_at')[:5]

    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress': in_progress,
        'completed_total': completed_total,
        'urgent_count': urgent_count,
        'total_revenue': total_revenue,
        'categories': categories,
        'recent_requests': recent_requests,
        'urgent_requests': urgent_requests,
    }
    return render(request, 'laboratory/dashboard.html', context)


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_request_list(request):
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')
    search_query = request.GET.get('q', '').strip()

    requests_qs = LabRequest.objects.select_related('patient', 'doctor').prefetch_related('items__test').order_by('-created_at')

    if status_filter and status_filter != 'all':
        requests_qs = requests_qs.filter(status=status_filter)
    
    if priority_filter and priority_filter != 'all':
        requests_qs = requests_qs.filter(priority=priority_filter)

    if search_query:
        requests_qs = requests_qs.filter(
            Q(order_number__icontains=search_query) |
            Q(patient__name__icontains=search_query) |
            Q(patient__phone__icontains=search_query)
        )

    counts = {
        'all': LabRequest.objects.count(),
        'pending': LabRequest.objects.filter(status='Pending').count(),
        'sample_collected': LabRequest.objects.filter(status='Sample Collected').count(),
        'in_progress': LabRequest.objects.filter(status='In Progress').count(),
        'completed': LabRequest.objects.filter(status='Completed').count(),
    }

    context = {
        'requests': requests_qs,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'counts': counts,
    }
    return render(request, 'laboratory/request_list.html', context)


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_request_create(request):
    if request.method == 'POST':
        form = LabRequestForm(request.POST)
        if form.is_valid():
            lab_req = form.save(commit=False)
            lab_req.status = 'Pending'
            lab_req.save()

            # Create items for selected tests
            selected_tests = form.cleaned_data['tests']
            total = 0
            for t in selected_tests:
                LabRequestItem.objects.create(
                    request=lab_req,
                    test=t,
                    price=t.price,
                    status='Pending'
                )
                total += t.price
            
            lab_req.total_amount = total
            lab_req.save()

            messages.success(request, f"Baaritaanka {lab_req.order_number} ee bukaanka {lab_req.patient.name} si guul leh ayaa loo diiwaangeliyey!")
            return redirect('lab_request_detail', pk=lab_req.pk)
    else:
        patient_id = request.GET.get('patient')
        initial_data = {}
        if patient_id:
            initial_data['patient'] = patient_id
        form = LabRequestForm(initial=initial_data)

    categories = LabCategory.objects.prefetch_related('tests').all()
    patients = Patient.objects.all().order_by('name')
    doctors = Doctor.objects.select_related('user').all()

    context = {
        'form': form,
        'categories': categories,
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'laboratory/request_form.html', context)


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_request_detail(request, pk):
    lab_req = get_object_or_404(
        LabRequest.objects.select_related('patient', 'doctor', 'technician')
        .prefetch_related('items__test', 'results__values'),
        pk=pk
    )
    return render(request, 'laboratory/request_detail.html', {'lab_req': lab_req})


@login_required
@role_required('Admin', 'Lab Technician')
def lab_sample_collect(request, pk):
    lab_req = get_object_or_404(LabRequest, pk=pk)
    lab_req.status = 'Sample Collected'
    lab_req.sample_collected_at = timezone.now()
    lab_req.save()
    lab_req.items.update(status='Sample Collected')
    messages.success(request, f"Muunada (Sample) baaritaanka {lab_req.order_number} si guul leh ayaa loo xaqiijiyey in la qaaday!")
    return redirect('lab_request_detail', pk=lab_req.pk)


@login_required
@role_required('Admin', 'Lab Technician')
def lab_result_entry(request, pk):
    lab_req = get_object_or_404(
        LabRequest.objects.select_related('patient', 'doctor')
        .prefetch_related('items__test__parameters'),
        pk=pk
    )

    if request.method == 'POST':
        for item in lab_req.items.all():
            test = item.test
            interpretation = request.POST.get(f'interpretation_{test.id}', '').strip()
            result, _ = LabResult.objects.get_or_create(
                request=lab_req,
                test=test,
                defaults={
                    'technician': request.user,
                    'performed_at': timezone.now(),
                    'overall_interpretation': interpretation
                }
            )
            result.technician = request.user
            result.performed_at = timezone.now()
            result.overall_interpretation = interpretation
            
            result.values.all().delete()
            test_has_abnormal = False

            params = test.parameters.all()
            if params.exists():
                for param in params:
                    val = request.POST.get(f'param_{param.id}', '').strip()
                    flag = request.POST.get(f'flag_{param.id}', 'Normal')
                    if val:
                        LabResultItem.objects.create(
                            result=result,
                            parameter_name=param.name,
                            result_value=val,
                            unit=param.unit or '',
                            reference_range=param.reference_range or '',
                            flag=flag
                        )
                        if flag in ['High', 'Low', 'Abnormal', 'Positive']:
                            test_has_abnormal = True
            else:
                val = request.POST.get(f'direct_val_{test.id}', '').strip()
                flag = request.POST.get(f'direct_flag_{test.id}', 'Normal')
                if val:
                    LabResultItem.objects.create(
                        result=result,
                        parameter_name=test.name,
                        result_value=val,
                        unit='',
                        reference_range='Normal / Negative',
                        flag=flag
                    )
                    if flag in ['High', 'Low', 'Abnormal', 'Positive']:
                        test_has_abnormal = True

            result.is_abnormal = test_has_abnormal
            result.save()
            item.status = 'Completed'
            item.save()

        lab_req.status = 'Completed'
        lab_req.completed_at = timezone.now()
        lab_req.technician = request.user
        lab_req.save()

        messages.success(request, f"Natiijooyinka baaritaanka {lab_req.order_number} si guul leh ayaa loo diiwaangeliyey loona daabici karaa!")
        return redirect('lab_report_view', pk=lab_req.pk)

    return render(request, 'laboratory/result_entry.html', {'lab_req': lab_req})


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_result_list(request):
    search_query = request.GET.get('q', '').strip()
    results_qs = LabRequest.objects.filter(status='Completed').select_related('patient', 'doctor', 'technician').prefetch_related('items__test', 'results__values').order_by('-completed_at')

    if search_query:
        results_qs = results_qs.filter(
            Q(order_number__icontains=search_query) |
            Q(patient__name__icontains=search_query)
        )

    context = {
        'results': results_qs,
        'search_query': search_query,
    }
    return render(request, 'laboratory/result_list.html', context)


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_report_view(request, pk):
    lab_req = get_object_or_404(
        LabRequest.objects.select_related('patient', 'doctor', 'technician')
        .prefetch_related('results__test__category', 'results__values'),
        pk=pk
    )
    return render(request, 'laboratory/report_view.html', {'lab_req': lab_req})


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def lab_test_catalog(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()

    tests_qs = LabTest.objects.select_related('category').prefetch_related('parameters').all()

    if category_id:
        tests_qs = tests_qs.filter(category_id=category_id)

    if search_query:
        tests_qs = tests_qs.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(sample_type__icontains=search_query)
        )

    categories = LabCategory.objects.annotate(test_count=Count('tests')).all()

    context = {
        'tests': tests_qs,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    return render(request, 'laboratory/test_catalog.html', context)


@login_required
@role_required('Admin', 'Lab Technician')
def lab_test_create(request):
    if request.method == 'POST':
        form = LabTestForm(request.POST)
        if form.is_valid():
            test = form.save()
            messages.success(request, f"Baaritaanka '{test.name}' si guul ah ayaa loogu daray liiska!")
            return redirect('lab_test_catalog')
    else:
        form = LabTestForm()
    return render(request, 'laboratory/test_form.html', {'form': form, 'title': 'Ku dar Baaritaan Cusub'})


@login_required
@role_required('Admin', 'Lab Technician')
def lab_test_update(request, pk):
    test = get_object_or_404(LabTest, pk=pk)
    if request.method == 'POST':
        form = LabTestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, f"Xogta baaritaanka '{test.name}' waa la cusboonaysiiyay!")
            return redirect('lab_test_catalog')
    else:
        form = LabTestForm(instance=test)
    return render(request, 'laboratory/test_form.html', {'form': form, 'title': 'Wax ka beddel Baaritaanka'})


@login_required
@role_required('Admin', 'Lab Technician')
def lab_category_create(request):
    if request.method == 'POST':
        form = LabCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Qaybta '{cat.name}' si guul ah ayaa loo abuuray!")
            return redirect('lab_test_catalog')
    else:
        form = LabCategoryForm()
    return render(request, 'laboratory/category_form.html', {'form': form, 'title': 'Abuur Qayb Cusub (Lab Category)'})


# ==========================================
# OUTPATIENT (OPD) MANAGEMENT VIEWS
# ==========================================
from .models import OPDVisit, OPDVitalSign, OPDConsultation, OPDPrescriptionItem
from .forms import OPDVisitForm, OPDVitalSignForm, OPDConsultationForm

@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def opd_dashboard(request):
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    total_today = OPDVisit.objects.filter(visit_date__gte=today_start).count()
    queue_waiting = OPDVisit.objects.filter(status='Waiting').count()
    queue_triage = OPDVisit.objects.filter(status='Triage Done').count()
    completed_today = OPDVisit.objects.filter(status='Completed', visit_date__gte=today_start).count()
    
    total_fee = OPDVisit.objects.filter(payment_status='Paid').aggregate(Sum('consultation_fee'))['consultation_fee__sum'] or 0

    active_queue = OPDVisit.objects.filter(
        status__in=['Waiting', 'Triage Done', 'In Consultation']
    ).select_related('patient', 'doctor', 'vitals').order_by('token_number')[:10]

    recent_completed = OPDVisit.objects.filter(
        status='Completed'
    ).select_related('patient', 'doctor', 'consultation').order_by('-visit_date')[:6]

    doctors = Doctor.objects.select_related('user', 'specialization').all()

    context = {
        'total_today': total_today,
        'queue_waiting': queue_waiting,
        'queue_triage': queue_triage,
        'completed_today': completed_today,
        'total_fee': total_fee,
        'active_queue': active_queue,
        'recent_completed': recent_completed,
        'doctors': doctors,
    }
    return render(request, 'opd/dashboard.html', context)


@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def opd_visit_list(request):
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    visits_qs = OPDVisit.objects.select_related('patient', 'doctor', 'vitals', 'consultation').order_by('-visit_date')

    if status_filter and status_filter != 'all':
        visits_qs = visits_qs.filter(status=status_filter)

    if search_query:
        visits_qs = visits_qs.filter(
            Q(visit_number__icontains=search_query) |
            Q(patient__name__icontains=search_query) |
            Q(patient__phone__icontains=search_query)
        )

    counts = {
        'all': OPDVisit.objects.count(),
        'waiting': OPDVisit.objects.filter(status='Waiting').count(),
        'triage_done': OPDVisit.objects.filter(status='Triage Done').count(),
        'in_consultation': OPDVisit.objects.filter(status='In Consultation').count(),
        'completed': OPDVisit.objects.filter(status='Completed').count(),
    }

    context = {
        'visits': visits_qs,
        'status_filter': status_filter,
        'search_query': search_query,
        'counts': counts,
    }
    return render(request, 'opd/visit_list.html', context)


@login_required
@role_required('Admin', 'Receptionist', 'Doctor', 'Nurse')
def opd_visit_create(request):
    if request.method == 'POST':
        form = OPDVisitForm(request.POST)
        if form.is_valid():
            visit = form.save()
            messages.success(request, f"Bukaanka {visit.patient.name} si guul ah ayaa loogu diiwaangeliyey safka OPD (Token #{visit.token_number})!")
            return redirect('opd_vitals_record', pk=visit.pk)
    else:
        patient_id = request.GET.get('patient')
        initial_data = {}
        if patient_id:
            initial_data['patient'] = patient_id
        form = OPDVisitForm(initial=initial_data)

    return render(request, 'opd/visit_form.html', {'form': form, 'title': 'Diiwaangeli Bukaan-Socod Cusub (New OPD Visit)'})


@login_required
@role_required('Admin', 'Doctor', 'Nurse', 'Receptionist')
def opd_visit_detail(request, pk):
    visit = get_object_or_404(
        OPDVisit.objects.select_related('patient', 'doctor', 'triage_nurse')
        .prefetch_related('consultation__prescriptions'),
        pk=pk
    )
    vitals = getattr(visit, 'vitals', None)
    consultation = getattr(visit, 'consultation', None)

    context = {
        'visit': visit,
        'vitals': vitals,
        'consultation': consultation,
    }
    return render(request, 'opd/visit_detail.html', context)


@login_required
@role_required('Admin', 'Nurse', 'Doctor')
def opd_vitals_record(request, pk):
    visit = get_object_or_404(OPDVisit.objects.select_related('patient', 'doctor'), pk=pk)
    vitals_instance = getattr(visit, 'vitals', None)

    if request.method == 'POST':
        form = OPDVitalSignForm(request.POST, instance=vitals_instance)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.visit = visit
            vitals.recorded_by = request.user
            vitals.save()

            if visit.status == 'Waiting':
                visit.status = 'Triage Done'
                visit.triage_nurse = request.user
                visit.save()

            messages.success(request, f"Calaamadaha muhiimka ah (Vitals) ee bukaanka {visit.patient.name} si guul ah ayaa loo keydiyay!")
            return redirect('opd_visit_detail', pk=visit.pk)
    else:
        form = OPDVitalSignForm(instance=vitals_instance)

    context = {
        'form': form,
        'visit': visit,
        'vitals': vitals_instance,
    }
    return render(request, 'opd/vitals_form.html', context)


@login_required
@role_required('Admin', 'Doctor')
def opd_consultation_view(request, pk):
    visit = get_object_or_404(
        OPDVisit.objects.select_related('patient', 'doctor')
        .prefetch_related('consultation__prescriptions'),
        pk=pk
    )
    vitals = getattr(visit, 'vitals', None)
    consultation_instance = getattr(visit, 'consultation', None)

    active_doctor = visit.doctor
    if not active_doctor:
        active_doctor = Doctor.objects.first()

    if request.method == 'POST':
        form = OPDConsultationForm(request.POST, instance=consultation_instance)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.visit = visit
            if not consultation.doctor_id:
                consultation.doctor = active_doctor
            consultation.save()

            consultation.prescriptions.all().delete()
            med_names = request.POST.getlist('med_name[]')
            dosages = request.POST.getlist('med_dosage[]')
            frequencies = request.POST.getlist('med_frequency[]')
            durations = request.POST.getlist('med_duration[]')
            instructions = request.POST.getlist('med_instructions[]')

            for i in range(len(med_names)):
                name = med_names[i].strip()
                if name:
                    OPDPrescriptionItem.objects.create(
                        consultation=consultation,
                        medicine_name=name,
                        dosage=dosages[i].strip() if i < len(dosages) else '',
                        frequency=frequencies[i].strip() if i < len(frequencies) else '',
                        duration=durations[i].strip() if i < len(durations) else '',
                        instructions=instructions[i].strip() if i < len(instructions) else '',
                    )

            visit.status = 'Completed'
            visit.save()

            messages.success(request, f"Baaritaanka iyo daawada bukaanka {visit.patient.name} si guul ah ayaa loo dhameystiray!")
            return redirect('opd_prescription_print', pk=visit.pk)
    else:
        form = OPDConsultationForm(instance=consultation_instance)

    medicines = Medicine.objects.filter(stock_quantity__gt=0)

    context = {
        'form': form,
        'visit': visit,
        'vitals': vitals,
        'consultation': consultation_instance,
        'medicines': medicines,
    }
    return render(request, 'opd/consultation_form.html', context)


@login_required
@role_required('Admin', 'Doctor', 'Pharmacist')
def opd_prescription_print(request, pk):
    visit = get_object_or_404(
        OPDVisit.objects.select_related('patient', 'doctor')
        .prefetch_related('consultation__prescriptions'),
        pk=pk
    )
    vitals = getattr(visit, 'vitals', None)
    consultation = getattr(visit, 'consultation', None)

    context = {
        'visit': visit,
        'vitals': vitals,
        'consultation': consultation,
    }
    return render(request, 'opd/prescription_print.html', context)


# ==========================================
# BILLING AND FINANCE MANAGEMENT VIEWS
# ==========================================
from .models import Invoice, InvoiceItem, PaymentTransaction
from .forms import InvoiceForm, PaymentTransactionForm

@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def billing_dashboard(request):
    total_billed = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_collected = Invoice.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    total_outstanding = Invoice.objects.filter(status__in=['Unpaid', 'Partially Paid', 'Overdue']).aggregate(Sum('balance_due'))['balance_due__sum'] or 0
    total_invoices = Invoice.objects.count()

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_collections = PaymentTransaction.objects.filter(payment_date__gte=today_start).aggregate(Sum('amount'))['amount__sum'] or 0

    recent_invoices = Invoice.objects.select_related('patient', 'doctor').prefetch_related('items').order_by('-billing_date')[:8]
    recent_payments = PaymentTransaction.objects.select_related('invoice__patient', 'received_by').order_by('-payment_date')[:6]

    service_breakdown = InvoiceItem.objects.values('service_type').annotate(
        total_revenue=Sum('total_price'),
        count=Count('id')
    ).order_by('-total_revenue')

    context = {
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'total_invoices': total_invoices,
        'today_collections': today_collections,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'service_breakdown': service_breakdown,
    }
    return render(request, 'billing/dashboard.html', context)


@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def invoice_list(request):
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    invoices_qs = Invoice.objects.select_related('patient', 'doctor').prefetch_related('items').order_by('-billing_date')

    if status_filter and status_filter != 'all':
        invoices_qs = invoices_qs.filter(status=status_filter)

    if search_query:
        invoices_qs = invoices_qs.filter(
            Q(invoice_number__icontains=search_query) |
            Q(patient__name__icontains=search_query) |
            Q(patient__phone__icontains=search_query)
        )

    counts = {
        'all': Invoice.objects.count(),
        'unpaid': Invoice.objects.filter(status='Unpaid').count(),
        'partially_paid': Invoice.objects.filter(status='Partially Paid').count(),
        'paid': Invoice.objects.filter(status='Paid').count(),
        'overdue': Invoice.objects.filter(status='Overdue').count(),
    }

    context = {
        'invoices': invoices_qs,
        'status_filter': status_filter,
        'search_query': search_query,
        'counts': counts,
    }
    return render(request, 'billing/invoice_list.html', context)


@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()

            service_types = request.POST.getlist('service_type[]')
            descriptions = request.POST.getlist('item_desc[]')
            quantities = request.POST.getlist('item_qty[]')
            prices = request.POST.getlist('item_price[]')

            subtotal = 0.0
            for i in range(len(descriptions)):
                desc = descriptions[i].strip()
                if desc:
                    qty = int(quantities[i]) if i < len(quantities) and quantities[i].isdigit() else 1
                    try:
                        price = float(prices[i]) if i < len(prices) else 0.0
                    except ValueError:
                        price = 0.0
                    total = qty * price
                    subtotal += total

                    InvoiceItem.objects.create(
                        invoice=invoice,
                        service_type=service_types[i] if i < len(service_types) else 'Other',
                        description=desc,
                        quantity=qty,
                        unit_price=price,
                        total_price=total
                    )

            invoice.subtotal = subtotal
            discount = float(invoice.discount or 0.0)
            tax = float(invoice.tax or 0.0)
            invoice.total_amount = max(0, subtotal - discount + tax)

            initial_paid = request.POST.get('initial_paid', '0').strip()
            try:
                initial_paid_val = float(initial_paid)
            except ValueError:
                initial_paid_val = 0.0

            if initial_paid_val > 0:
                PaymentTransaction.objects.create(
                    invoice=invoice,
                    amount=min(initial_paid_val, float(invoice.total_amount)),
                    payment_method=invoice.payment_method,
                    reference_number=request.POST.get('initial_ref', ''),
                    received_by=request.user,
                    notes='Initial payment upon invoice creation'
                )

            invoice.save()

            messages.success(request, f"Qaansada {invoice.invoice_number} ee bukaanka {invoice.patient.name} si guul ah ayaa loo abuuray!")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        patient_id = request.GET.get('patient')
        initial_data = {}
        if patient_id:
            initial_data['patient'] = patient_id
        form = InvoiceForm(initial=initial_data)

    patients = Patient.objects.all().order_by('name')
    doctors = Doctor.objects.select_related('user').all()

    context = {
        'form': form,
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'billing/invoice_form.html', context)


@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('patient', 'doctor', 'created_by')
        .prefetch_related('items', 'payments__received_by'),
        pk=pk
    )
    payment_form = PaymentTransactionForm(initial={'amount': invoice.balance_due})

    context = {
        'invoice': invoice,
        'payment_form': payment_form,
    }
    return render(request, 'billing/invoice_detail.html', context)


@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def payment_record(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = PaymentTransactionForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.received_by = request.user
            payment.save()

            messages.success(request, f"Lacag-bixinta dhan ${payment.amount} ee qaansada {invoice.invoice_number} si guul ah ayaa loo qabtay!")
            return redirect('invoice_detail', pk=invoice.pk)
        else:
            messages.error(request, "Fadlan sax xogta lacag-bixinta.")
    return redirect('invoice_detail', pk=invoice.pk)


@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def invoice_print(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('patient', 'doctor', 'created_by')
        .prefetch_related('items', 'payments__received_by'),
        pk=pk
    )
    return render(request, 'billing/invoice_print.html', {'invoice': invoice})


@login_required
@role_required('Admin', 'Accountant', 'Receptionist')
def payment_list(request):
    search_query = request.GET.get('q', '').strip()
    payments_qs = PaymentTransaction.objects.select_related('invoice__patient', 'received_by').order_by('-payment_date')

    if search_query:
        payments_qs = payments_qs.filter(
            Q(transaction_id__icontains=search_query) |
            Q(reference_number__icontains=search_query) |
            Q(invoice__invoice_number__icontains=search_query) |
            Q(invoice__patient__name__icontains=search_query)
        )

    total_amount = payments_qs.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'payments': payments_qs,
        'search_query': search_query,
        'total_amount': total_amount,
    }
    return render(request, 'billing/payment_list.html', context)


# ==========================================
# HR & STAFF MANAGEMENT VIEWS
# ==========================================
from .models import User, Staff, StaffAttendance, StaffLeave, StaffPayroll
from .forms import StaffForm, StaffAttendanceForm, StaffLeaveForm, StaffPayrollForm
import datetime


@login_required
@admin_required
def hr_dashboard(request):
    total_staff = Staff.objects.count()
    active_staff = Staff.objects.filter(status='Active').count()
    on_leave_staff = Staff.objects.filter(status='On Leave').count()

    today = timezone.now().date()
    today_attendances = StaffAttendance.objects.filter(date=today)
    present_today = today_attendances.filter(status='Present').count()
    late_today = today_attendances.filter(status='Late').count()
    absent_today = today_attendances.filter(status='Absent').count()
    on_leave_today = today_attendances.filter(status='On Leave').count()

    total_monthly_payroll = Staff.objects.filter(status='Active').aggregate(Sum('salary'))['salary__sum'] or 0
    pending_leaves = StaffLeave.objects.filter(status='Pending').select_related('staff__user').order_by('-applied_on')[:5]
    pending_leaves_count = StaffLeave.objects.filter(status='Pending').count()

    recent_staff = Staff.objects.select_related('user').order_by('-hire_date')[:6]
    recent_payrolls = StaffPayroll.objects.select_related('staff__user').order_by('-payment_date')[:5]

    # Department breakdown
    department_stats = Staff.objects.values('department').annotate(count=Count('id')).order_by('-count')

    context = {
        'total_staff': total_staff,
        'active_staff': active_staff,
        'on_leave_staff': on_leave_staff,
        'today': today,
        'present_today': present_today,
        'late_today': late_today,
        'absent_today': absent_today,
        'on_leave_today': on_leave_today,
        'total_monthly_payroll': total_monthly_payroll,
        'pending_leaves': pending_leaves,
        'pending_leaves_count': pending_leaves_count,
        'recent_staff': recent_staff,
        'recent_payrolls': recent_payrolls,
        'department_stats': department_stats,
    }
    return render(request, 'hr/dashboard.html', context)


@login_required
@admin_required
def staff_list(request):
    search_query = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('department', '').strip()
    shift_filter = request.GET.get('shift', '').strip()
    status_filter = request.GET.get('status', '').strip()

    staff_qs = Staff.objects.select_related('user').order_by('employee_id')

    if search_query:
        staff_qs = staff_qs.filter(
            Q(employee_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if dept_filter:
        staff_qs = staff_qs.filter(department=dept_filter)

    if shift_filter:
        staff_qs = staff_qs.filter(shift=shift_filter)

    if status_filter:
        staff_qs = staff_qs.filter(status=status_filter)

    departments = Staff.DEPARTMENT_CHOICES
    shifts = Staff.SHIFT_CHOICES
    statuses = Staff.STATUS_CHOICES

    context = {
        'staff_list': staff_qs,
        'search_query': search_query,
        'selected_dept': dept_filter,
        'selected_shift': shift_filter,
        'selected_status': status_filter,
        'departments': departments,
        'shifts': shifts,
        'statuses': statuses,
        'total_count': staff_qs.count(),
    }
    return render(request, 'hr/staff_list.html', context)


@login_required
@admin_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data.get('email', '')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            if not username:
                base_username = f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

            if not password:
                password = 'Hospital@2026'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first_name, 'last_name': last_name, 'email': email}
            )
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
            user.set_password(password)
            user.save()

            staff = form.save(commit=False)
            staff.user = user
            staff.save()

            messages.success(request, f"Shaqaalaha {user.get_full_name()} ({staff.designation}) si guul ah ayaa loo diiwaangeliyay!")
            return redirect('staff_detail', pk=staff.pk)
        else:
            messages.error(request, "Fadlan sax khaladaadka foomka ku jira.")
    else:
        form = StaffForm()

    return render(request, 'hr/staff_form.html', {'form': form, 'title': 'Diiwaangeli Shaqaale Cusub'})


@login_required
def staff_update(request, pk):
    staff = get_object_or_404(Staff.objects.select_related('user'), pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data.get('email', '')
            password = form.cleaned_data.get('password')

            staff.user.first_name = first_name
            staff.user.last_name = last_name
            staff.user.email = email
            if password:
                staff.user.set_password(password)
            staff.user.save()

            form.save()
            messages.success(request, f"Xogta shaqaalaha {staff.user.get_full_name()} si guul ah ayaa loo cusbooneysiiyay!")
            return redirect('staff_detail', pk=staff.pk)
        else:
            messages.error(request, "Fadlan sax khaladaadka foomka ku jira.")
    else:
        form = StaffForm(instance=staff)

    return render(request, 'hr/staff_form.html', {'form': form, 'staff': staff, 'title': f'Wax ka bedel: {staff.user.get_full_name()}'})


@login_required
def staff_detail(request, pk):
    staff = get_object_or_404(Staff.objects.select_related('user'), pk=pk)
    attendances = staff.attendances.order_by('-date')[:30]
    leaves = staff.leaves.order_by('-applied_on')[:15]
    payrolls = staff.payrolls.order_by('-payment_date')[:12]

    # Pre-filled forms for quick actions inside staff detail
    attendance_form = StaffAttendanceForm(initial={'staff': staff, 'date': timezone.now().date(), 'status': 'Present'})
    leave_form = StaffLeaveForm(initial={'staff': staff, 'start_date': timezone.now().date(), 'end_date': timezone.now().date()})
    payroll_form = StaffPayrollForm(initial={
        'staff': staff,
        'basic_salary': staff.salary,
        'salary_month': timezone.now().strftime('%B %Y'),
        'payment_date': timezone.now().date()
    })

    # Stats for this staff
    present_days = staff.attendances.filter(status='Present').count()
    late_days = staff.attendances.filter(status='Late').count()
    absent_days = staff.attendances.filter(status='Absent').count()
    total_leaves = staff.leaves.filter(status='Approved').count()
    total_earned = staff.payrolls.filter(status='Paid').aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    context = {
        'staff': staff,
        'attendances': attendances,
        'leaves': leaves,
        'payrolls': payrolls,
        'attendance_form': attendance_form,
        'leave_form': leave_form,
        'payroll_form': payroll_form,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'total_leaves': total_leaves,
        'total_earned': total_earned,
    }
    return render(request, 'hr/staff_detail.html', context)


@login_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        name = staff.user.get_full_name() or staff.user.username
        staff.status = 'Terminated'
        staff.save()
        messages.warning(request, f"Shaqaalaha {name} xaaladdiisa waxaa laga dhigay 'La Eryay/Terminated'.")
        return redirect('staff_list')
    return redirect('staff_detail', pk=pk)


@login_required
def attendance_list(request):
    date_str = request.GET.get('date', '').strip()
    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    all_staff = Staff.objects.filter(status__in=['Active', 'On Leave']).select_related('user').order_by('employee_id')
    existing_attendances = {a.staff_id: a for a in StaffAttendance.objects.filter(date=selected_date)}

    staff_roster = []
    present_count = 0
    late_count = 0
    absent_count = 0
    half_day_count = 0
    on_leave_count = 0
    unmarked_count = 0

    for member in all_staff:
        record = existing_attendances.get(member.id)
        if record:
            st = record.status
            if st == 'Present':
                present_count += 1
            elif st == 'Late':
                late_count += 1
            elif st == 'Absent':
                absent_count += 1
            elif st == 'Half Day':
                half_day_count += 1
            elif st == 'On Leave':
                on_leave_count += 1
        else:
            st = 'Unmarked'
            unmarked_count += 1

        staff_roster.append({
            'staff': member,
            'record': record,
            'status': st
        })

    context = {
        'selected_date': selected_date,
        'staff_roster': staff_roster,
        'total_staff': len(all_staff),
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'half_day_count': half_day_count,
        'on_leave_count': on_leave_count,
        'unmarked_count': unmarked_count,
    }
    return render(request, 'hr/attendance_list.html', context)


@login_required
def attendance_mark(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        date_str = request.POST.get('date')
        status = request.POST.get('status', 'Present')
        check_in = request.POST.get('check_in') or None
        check_out = request.POST.get('check_out') or None
        notes = request.POST.get('notes', '')

        if date_str:
            try:
                date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date_val = timezone.now().date()
        else:
            date_val = timezone.now().date()

        staff = get_object_or_404(Staff, pk=staff_id)
        attendance, created = StaffAttendance.objects.update_or_create(
            staff=staff,
            date=date_val,
            defaults={
                'status': status,
                'check_in': check_in if check_in else None,
                'check_out': check_out if check_out else None,
                'notes': notes,
                'recorded_by': request.user
            }
        )

        messages.success(request, f"Xaadirka {staff.user.get_full_name()} ee {date_val} ({status}) waa la keydiyay!")
        redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'attendance_list'
        return redirect(redirect_to)

    return redirect('attendance_list')


@login_required
def leave_list(request):
    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('leave_type', '').strip()
    search_query = request.GET.get('q', '').strip()

    leaves_qs = StaffLeave.objects.select_related('staff__user', 'approved_by').order_by('-applied_on')

    if status_filter:
        leaves_qs = leaves_qs.filter(status=status_filter)

    if type_filter:
        leaves_qs = leaves_qs.filter(leave_type=type_filter)

    if search_query:
        leaves_qs = leaves_qs.filter(
            Q(staff__user__first_name__icontains=search_query) |
            Q(staff__user__last_name__icontains=search_query) |
            Q(staff__employee_id__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    leave_form = StaffLeaveForm(initial={'start_date': timezone.now().date(), 'end_date': timezone.now().date()})

    pending_count = StaffLeave.objects.filter(status='Pending').count()
    approved_count = StaffLeave.objects.filter(status='Approved').count()
    rejected_count = StaffLeave.objects.filter(status='Rejected').count()

    context = {
        'leaves': leaves_qs,
        'leave_form': leave_form,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'leave_types': StaffLeave.LEAVE_TYPE_CHOICES,
    }
    return render(request, 'hr/leave_list.html', context)


@login_required
def leave_create(request):
    if request.method == 'POST':
        form = StaffLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save()
            messages.success(request, f"Codsiga fasaxa ee {leave.staff.user.get_full_name()} waa la diray!")
            return redirect('leave_list')
        else:
            messages.error(request, "Fadlan sax khaladaadka codsiga fasaxa.")
    return redirect('leave_list')


@login_required
def leave_action(request, pk, action):
    leave = get_object_or_404(StaffLeave, pk=pk)
    admin_remarks = request.POST.get('admin_remarks', '')

    if action == 'approve':
        leave.status = 'Approved'
        leave.approved_by = request.user
        if admin_remarks:
            leave.admin_remarks = admin_remarks
        leave.save()

        # Update staff status to On Leave if currently active and leave is active today
        today = timezone.now().date()
        if leave.start_date <= today <= leave.end_date:
            leave.staff.status = 'On Leave'
            leave.staff.save()

        messages.success(request, f"Codsiga fasaxa ee {leave.staff.user.get_full_name()} waa la oggolaaday (Approved)!")
    elif action == 'reject':
        leave.status = 'Rejected'
        leave.approved_by = request.user
        if admin_remarks:
            leave.admin_remarks = admin_remarks
        leave.save()
        messages.warning(request, f"Codsiga fasaxa ee {leave.staff.user.get_full_name()} waa la diiday (Rejected).")

    return redirect('leave_list')


@login_required
def payroll_list(request):
    month_filter = request.GET.get('month', '').strip()
    status_filter = request.GET.get('status', '').strip()
    search_query = request.GET.get('q', '').strip()

    payrolls_qs = StaffPayroll.objects.select_related('staff__user', 'created_by').order_by('-payment_date')

    if month_filter:
        payrolls_qs = payrolls_qs.filter(salary_month__icontains=month_filter)

    if status_filter:
        payrolls_qs = payrolls_qs.filter(status=status_filter)

    if search_query:
        payrolls_qs = payrolls_qs.filter(
            Q(payroll_number__icontains=search_query) |
            Q(staff__user__first_name__icontains=search_query) |
            Q(staff__user__last_name__icontains=search_query) |
            Q(staff__employee_id__icontains=search_query) |
            Q(reference_number__icontains=search_query)
        )

    total_gross = payrolls_qs.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    total_allowances = payrolls_qs.aggregate(Sum('allowances'))['allowances__sum'] or 0
    total_deductions = payrolls_qs.aggregate(Sum('deductions'))['deductions__sum'] or 0
    total_net = payrolls_qs.aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    payroll_form = StaffPayrollForm(initial={
        'salary_month': timezone.now().strftime('%B %Y'),
        'payment_date': timezone.now().date(),
        'status': 'Paid'
    })

    context = {
        'payrolls': payrolls_qs,
        'payroll_form': payroll_form,
        'month_filter': month_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_gross': total_gross,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'total_net': total_net,
        'staff_members': Staff.objects.filter(status='Active').select_related('user'),
    }
    return render(request, 'hr/payroll_list.html', context)


@login_required
def payroll_create(request):
    if request.method == 'POST':
        form = StaffPayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.created_by = request.user
            payroll.save()
            messages.success(request, f"Mushaharka {payroll.staff.user.get_full_name()} ee {payroll.salary_month} (${payroll.net_salary}) si guul ah ayaa loo bixiyay!")
            return redirect('payroll_print', pk=payroll.pk)
        else:
            messages.error(request, "Fadlan sax xogta lacag-bixinta mushaharka.")
    return redirect('payroll_list')


@login_required
def payroll_print(request, pk):
    payroll = get_object_or_404(
        StaffPayroll.objects.select_related('staff__user', 'created_by'),
        pk=pk
    )
    return render(request, 'hr/payroll_print.html', {'payroll': payroll})


# ==========================================
# REPORTS & ANALYTICS VIEWS
# ==========================================
from .models import (
    Ward, Bed, Admission,
    LabCategory, LabTest, LabRequest, LabRequestItem, LabResult,
    PharmacySale, PharmacySaleItem, Medicine,
    Invoice, InvoiceItem, PaymentTransaction,
    Staff, StaffAttendance, StaffLeave, StaffPayroll
)
import datetime
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone


def get_report_dates(request):
    period = request.GET.get('period', 'this_month')
    today = timezone.now().date()

    if period == 'today':
        start_date = today
        end_date = today
        period_label = f"Maanta ({today.strftime('%d %b %Y')})"
    elif period == 'this_week':
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = today
        period_label = f"Toddobaadkan ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')})"
    elif period == 'this_year':
        start_date = datetime.date(today.year, 1, 1)
        end_date = today
        period_label = f"Sanadkan {today.year} ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')})"
    elif period == 'custom':
        start_str = request.GET.get('start_date', '')
        end_str = request.GET.get('end_date', '')
        try:
            start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else today.replace(day=1)
        except ValueError:
            start_date = today.replace(day=1)
        try:
            end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else today
        except ValueError:
            end_date = today
        period_label = f"Taariikh Gaar ah ({start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')})"
    else:  # default 'this_month'
        period = 'this_month'
        start_date = today.replace(day=1)
        end_date = today
        period_label = f"Bishan ({today.strftime('%B %Y')})"

    start_dt = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
    end_dt = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))

    return period, start_date, end_date, start_dt, end_dt, period_label


@login_required
@role_required('Admin', 'Doctor', 'Accountant', 'Pharmacist', 'Lab Technician')
def reports_hub(request):
    period, start_date, end_date, start_dt, end_dt, period_label = get_report_dates(request)

    # 1. Financial Metrics in Range
    invoices_qs = Invoice.objects.filter(billing_date__range=(start_dt, end_dt))
    total_billed = invoices_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_collected = invoices_qs.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    total_balance_due = invoices_qs.aggregate(Sum('balance_due'))['balance_due__sum'] or 0
    invoices_count = invoices_qs.count()

    # 2. Patients & Clinical Workload
    new_patients_count = Patient.objects.filter(created_at__range=(start_dt, end_dt)).count()
    total_patients_system = Patient.objects.count()
    opd_visits_count = OPDVisit.objects.filter(visit_date__range=(start_dt, end_dt)).count()
    admissions_count = Admission.objects.filter(admission_date__range=(start_dt, end_dt)).count()

    # 3. Diagnostics & Pharmacy
    lab_requests_count = LabRequest.objects.filter(created_at__range=(start_dt, end_dt)).count()
    lab_revenue = LabRequest.objects.filter(created_at__range=(start_dt, end_dt)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pharmacy_sales_count = PharmacySale.objects.filter(sale_date__range=(start_dt, end_dt)).count()
    pharmacy_revenue = PharmacySale.objects.filter(sale_date__range=(start_dt, end_dt)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # 4. HR & Workforce
    active_staff_count = Staff.objects.filter(status='Active').count()
    payroll_disbursed = StaffPayroll.objects.filter(payment_date__range=(start_date, end_date)).aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    # 5. Service Category Revenue Breakdown
    service_revenue = InvoiceItem.objects.filter(
        invoice__billing_date__range=(start_dt, end_dt)
    ).values('service_type').annotate(total=Sum('total_price'), count=Count('id')).order_by('-total')

    # 6. Top Doctors by consultations
    top_doctors = OPDConsultation.objects.filter(
        consultation_date__range=(start_dt, end_dt)
    ).values(
        'doctor__user__first_name',
        'doctor__user__last_name',
        'doctor__specialization__name'
    ).annotate(count=Count('id')).order_by('-count')[:5]

    # 7. Recent Invoices & Payments for table preview
    recent_invoices = invoices_qs.select_related('patient', 'doctor').order_by('-billing_date')[:6]

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'period_label': period_label,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_balance_due': total_balance_due,
        'invoices_count': invoices_count,
        'new_patients_count': new_patients_count,
        'total_patients_system': total_patients_system,
        'opd_visits_count': opd_visits_count,
        'admissions_count': admissions_count,
        'lab_requests_count': lab_requests_count,
        'lab_revenue': lab_revenue,
        'pharmacy_sales_count': pharmacy_sales_count,
        'pharmacy_revenue': pharmacy_revenue,
        'active_staff_count': active_staff_count,
        'payroll_disbursed': payroll_disbursed,
        'service_revenue': service_revenue,
        'top_doctors': top_doctors,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@role_required('Admin', 'Accountant')
def report_financial(request):
    period, start_date, end_date, start_dt, end_dt, period_label = get_report_dates(request)

    invoices_qs = Invoice.objects.filter(billing_date__range=(start_dt, end_dt)).select_related('patient', 'doctor')
    payments_qs = PaymentTransaction.objects.filter(payment_date__range=(start_dt, end_dt)).select_related('invoice__patient', 'received_by')

    total_billed = invoices_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_collected = invoices_qs.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    total_balance_due = invoices_qs.aggregate(Sum('balance_due'))['balance_due__sum'] or 0
    total_discount = invoices_qs.aggregate(Sum('discount'))['discount__sum'] or 0
    total_tax = invoices_qs.aggregate(Sum('tax'))['tax__sum'] or 0

    collection_rate = (float(total_collected) / float(total_billed) * 100) if total_billed > 0 else 0

    # Invoices by status
    paid_count = invoices_qs.filter(status='Paid').count()
    partial_count = invoices_qs.filter(status='Partially Paid').count()
    unpaid_count = invoices_qs.filter(status='Unpaid').count()
    overdue_count = invoices_qs.filter(status='Overdue').count()

    # Revenue by Service Type
    service_breakdown = InvoiceItem.objects.filter(
        invoice__billing_date__range=(start_dt, end_dt)
    ).values('service_type').annotate(total=Sum('total_price'), items_count=Count('id')).order_by('-total')

    # Revenue by Payment Method
    method_breakdown = payments_qs.values('payment_method').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'period_label': period_label,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_balance_due': total_balance_due,
        'total_discount': total_discount,
        'total_tax': total_tax,
        'collection_rate': round(collection_rate, 1),
        'invoices': invoices_qs.order_by('-billing_date'),
        'payments': payments_qs.order_by('-payment_date'),
        'paid_count': paid_count,
        'partial_count': partial_count,
        'unpaid_count': unpaid_count,
        'overdue_count': overdue_count,
        'service_breakdown': service_breakdown,
        'method_breakdown': method_breakdown,
    }
    return render(request, 'reports/financial.html', context)


@login_required
@role_required('Admin', 'Doctor')
def report_patients(request):
    period, start_date, end_date, start_dt, end_dt, period_label = get_report_dates(request)

    # Patient demographics
    patients_in_period = Patient.objects.filter(created_at__range=(start_dt, end_dt))
    total_patients_all = Patient.objects.count()
    new_patients_count = patients_in_period.count()

    male_count = Patient.objects.filter(gender='Male').count()
    female_count = Patient.objects.filter(gender='Female').count()

    # Age groups across all patients
    pediatric_count = Patient.objects.filter(age__lt=18).count()
    young_adult_count = Patient.objects.filter(age__gte=18, age__lte=35).count()
    middle_age_count = Patient.objects.filter(age__gte=36, age__lte=55).count()
    elderly_count = Patient.objects.filter(age__gt=55).count()

    # OPD Visits
    opd_visits = OPDVisit.objects.filter(visit_date__range=(start_dt, end_dt)).select_related('patient', 'doctor')
    total_visits = opd_visits.count()
    visit_type_stats = opd_visits.values('visit_type').annotate(count=Count('id')).order_by('-count')
    visit_status_stats = opd_visits.values('status').annotate(count=Count('id')).order_by('-count')

    # OPD Consultations & Outcomes
    consultations = OPDConsultation.objects.filter(consultation_date__range=(start_dt, end_dt)).select_related('visit__patient', 'doctor')
    total_consultations = consultations.count()
    outcomes_stats = consultations.values('outcome').annotate(count=Count('id')).order_by('-count')
    top_diagnoses = consultations.values('diagnosis').annotate(count=Count('id')).order_by('-count')[:8]

    # Inpatient (IPD)
    admissions = Admission.objects.filter(admission_date__range=(start_dt, end_dt)).select_related('patient', 'bed__ward', 'doctor')
    total_admissions = admissions.count()
    active_admitted = Admission.objects.filter(status='Admitted').count()
    discharges_in_period = Admission.objects.filter(discharge_date__range=(start_dt, end_dt), status='Discharged').count()
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_available=False).count()
    available_beds = Bed.objects.filter(is_available=True).count()

    # Top Doctors by Consultations
    doctor_workload = consultations.values(
        'doctor__user__first_name',
        'doctor__user__last_name',
        'doctor__specialization__name'
    ).annotate(count=Count('id')).order_by('-count')[:6]

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'period_label': period_label,
        'new_patients_count': new_patients_count,
        'total_patients_all': total_patients_all,
        'male_count': male_count,
        'female_count': female_count,
        'pediatric_count': pediatric_count,
        'young_adult_count': young_adult_count,
        'middle_age_count': middle_age_count,
        'elderly_count': elderly_count,
        'total_visits': total_visits,
        'visit_type_stats': visit_type_stats,
        'visit_status_stats': visit_status_stats,
        'total_consultations': total_consultations,
        'outcomes_stats': outcomes_stats,
        'top_diagnoses': top_diagnoses,
        'total_admissions': total_admissions,
        'active_admitted': active_admitted,
        'discharges_in_period': discharges_in_period,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'doctor_workload': doctor_workload,
        'recent_admissions': admissions.order_by('-admission_date')[:10],
    }
    return render(request, 'reports/patients.html', context)


@login_required
@role_required('Admin', 'Lab Technician', 'Doctor')
def report_laboratory(request):
    period, start_date, end_date, start_dt, end_dt, period_label = get_report_dates(request)

    lab_requests = LabRequest.objects.filter(created_at__range=(start_dt, end_dt)).select_related('patient', 'doctor', 'technician')
    total_requests = lab_requests.count()
    total_revenue = lab_requests.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Status counts
    completed_count = lab_requests.filter(status='Completed').count()
    processing_count = lab_requests.filter(status='In Progress').count()
    sample_collected_count = lab_requests.filter(status='Sample Collected').count()
    pending_count = lab_requests.filter(status='Pending').count()

    # Priority counts
    urgent_count = lab_requests.filter(priority='Urgent').count()
    stat_count = lab_requests.filter(priority='Stat').count()
    normal_priority_count = lab_requests.filter(priority='Normal').count()

    # Results breakdown
    results_in_period = LabResult.objects.filter(performed_at__range=(start_dt, end_dt))
    total_results = results_in_period.count()
    abnormal_count = results_in_period.filter(is_abnormal=True).count()
    normal_results_count = results_in_period.filter(is_abnormal=False).count()
    abnormal_rate = (abnormal_count / total_results * 100) if total_results > 0 else 0

    # Top Tests conducted in range
    top_tests = LabRequestItem.objects.filter(
        request__created_at__range=(start_dt, end_dt)
    ).values(
        'test__name', 'test__code', 'test__category__name', 'test__price'
    ).annotate(count=Count('id'), total_val=Sum('price')).order_by('-count')[:10]

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'period_label': period_label,
        'total_requests': total_requests,
        'total_revenue': total_revenue,
        'completed_count': completed_count,
        'processing_count': processing_count,
        'sample_collected_count': sample_collected_count,
        'pending_count': pending_count,
        'urgent_count': urgent_count,
        'stat_count': stat_count,
        'normal_priority_count': normal_priority_count,
        'total_results': total_results,
        'abnormal_count': abnormal_count,
        'normal_results_count': normal_results_count,
        'abnormal_rate': round(abnormal_rate, 1),
        'top_tests': top_tests,
        'recent_requests': lab_requests.order_by('-created_at')[:15],
    }
    return render(request, 'reports/laboratory.html', context)


@login_required
@role_required('Admin', 'Pharmacist')
def report_pharmacy(request):
    period, start_date, end_date, start_dt, end_dt, period_label = get_report_dates(request)

    sales_qs = PharmacySale.objects.filter(sale_date__range=(start_dt, end_dt)).select_related('patient')
    total_sales = sales_qs.count()
    total_revenue = sales_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    avg_sale_val = (float(total_revenue) / total_sales) if total_sales > 0 else 0

    total_units_sold = PharmacySaleItem.objects.filter(
        sale__sale_date__range=(start_dt, end_dt)
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Top selling medicines in range
    top_medicines = PharmacySaleItem.objects.filter(
        sale__sale_date__range=(start_dt, end_dt)
    ).values(
        'medicine__name', 'medicine__batch_number', 'medicine__unit_price'
    ).annotate(total_qty=Sum('quantity'), total_rev=Sum('total')).order_by('-total_qty')[:10]

    # Low stock medicines in the hospital
    low_stock_medicines = Medicine.objects.filter(stock_quantity__lte=20).order_by('stock_quantity')[:10]

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'period_label': period_label,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'avg_sale_val': round(avg_sale_val, 2),
        'total_units_sold': total_units_sold,
        'top_medicines': top_medicines,
        'low_stock_medicines': low_stock_medicines,
        'recent_sales': sales_qs.order_by('-sale_date')[:15],
    }
    return render(request, 'reports/pharmacy.html', context)


@login_required
@admin_required
def report_hr(request):
    period, start_date, end_date, start_dt, end_dt, period_label = get_report_dates(request)

    total_staff = Staff.objects.count()
    active_staff = Staff.objects.filter(status='Active').count()
    on_leave_staff = Staff.objects.filter(status='On Leave').count()

    dept_stats = Staff.objects.values('department').annotate(count=Count('id')).order_by('-count')
    shift_stats = Staff.objects.values('shift').annotate(count=Count('id')).order_by('-count')

    # Attendances in range
    attendances_qs = StaffAttendance.objects.filter(date__range=(start_date, end_date))
    total_att_records = attendances_qs.count()
    present_count = attendances_qs.filter(status='Present').count()
    late_count = attendances_qs.filter(status='Late').count()
    absent_count = attendances_qs.filter(status='Absent').count()
    half_day_count = attendances_qs.filter(status='Half Day').count()
    on_leave_att_count = attendances_qs.filter(status='On Leave').count()

    attendance_rate = ((present_count + late_count) / total_att_records * 100) if total_att_records > 0 else 0

    # Leaves in range
    leaves_qs = StaffLeave.objects.filter(applied_on__range=(start_dt, end_dt))
    total_leaves = leaves_qs.count()
    approved_leaves = leaves_qs.filter(status='Approved').count()
    pending_leaves = leaves_qs.filter(status='Pending').count()
    rejected_leaves = leaves_qs.filter(status='Rejected').count()

    # Payroll in range
    payrolls_qs = StaffPayroll.objects.filter(payment_date__range=(start_date, end_date))
    total_payrolls_count = payrolls_qs.count()
    total_basic = payrolls_qs.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    total_allowances = payrolls_qs.aggregate(Sum('allowances'))['allowances__sum'] or 0
    total_deductions = payrolls_qs.aggregate(Sum('deductions'))['deductions__sum'] or 0
    total_net_paid = payrolls_qs.aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'period_label': period_label,
        'total_staff': total_staff,
        'active_staff': active_staff,
        'on_leave_staff': on_leave_staff,
        'dept_stats': dept_stats,
        'shift_stats': shift_stats,
        'total_att_records': total_att_records,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'half_day_count': half_day_count,
        'on_leave_att_count': on_leave_att_count,
        'attendance_rate': round(attendance_rate, 1),
        'total_leaves': total_leaves,
        'approved_leaves': approved_leaves,
        'pending_leaves': pending_leaves,
        'rejected_leaves': rejected_leaves,
        'total_payrolls_count': total_payrolls_count,
        'total_basic': total_basic,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'total_net_paid': total_net_paid,
        'recent_payrolls': payrolls_qs.select_related('staff__user').order_by('-payment_date')[:10],
    }
    return render(request, 'reports/hr.html', context)


# ==========================================
# HOSPITAL SETTINGS & BACKUP VIEWS
# ==========================================
import os
import shutil
import platform
import django
from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib.auth import update_session_auth_hash
from .models import HospitalSetting
from .forms import HospitalSettingForm, UserProfileForm, UserPasswordChangeForm


def get_backups_dir():
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def list_backup_files():
    b_dir = get_backups_dir()
    files = []
    if os.path.exists(b_dir):
        for fname in os.listdir(b_dir):
            if fname.endswith('.sqlite3') or fname.endswith('.json') or fname.endswith('.bak'):
                fpath = os.path.join(b_dir, fname)
                st = os.stat(fpath)
                files.append({
                    'name': fname,
                    'size_kb': round(st.st_size / 1024, 1),
                    'size_mb': round(st.st_size / (1024 * 1024), 2),
                    'created_at': datetime.datetime.fromtimestamp(st.st_mtime),
                })
    files.sort(key=lambda x: x['created_at'], reverse=True)
    return files


@login_required
@admin_required
def settings_general(request):
    hospital_setting = HospitalSetting.get_settings()

    # System Info
    db_path = settings.DATABASES['default']['NAME']
    db_size_mb = 0
    if os.path.exists(str(db_path)):
        db_size_mb = round(os.path.getsize(str(db_path)) / (1024 * 1024), 2)

    system_info = {
        'django_version': django.get_version(),
        'python_version': platform.python_version(),
        'os_name': platform.system() + " " + platform.release(),
        'database_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
        'db_size_mb': db_size_mb,
        'server_time': timezone.now(),
        'total_users': User.objects.count(),
        'total_patients': Patient.objects.count(),
        'total_staff': Staff.objects.count(),
    }

    hospital_form = HospitalSettingForm(instance=hospital_setting)
    profile_form = UserProfileForm(instance=request.user)
    password_form = UserPasswordChangeForm()
    backups = list_backup_files()[:5]

    context = {
        'hospital_setting': hospital_setting,
        'hospital_form': hospital_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'system_info': system_info,
        'backups': backups,
        'active_tab': request.GET.get('tab', 'hospital'),
    }
    return render(request, 'settings/dashboard.html', context)


@login_required
@admin_required
def settings_hospital(request):
    hospital_setting = HospitalSetting.get_settings()
    if request.method == 'POST':
        form = HospitalSettingForm(request.POST, request.FILES, instance=hospital_setting)
        if form.is_valid():
            form.save()
            messages.success(request, "Macluumaadka iyo astaanta (logo-da) isbitaalka si guul ah ayaa loo cusbooneysiiyay!")
            return redirect('/settings/?tab=hospital')
        else:
            messages.error(request, "Fadlan sax khaladaadka foomka isbitaalka.")
    return redirect('settings_general')


@login_required
def settings_password(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            p_form = UserProfileForm(request.POST, instance=request.user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, "Xogtaada shakhsiga ah si guul ah ayaa loo cusbooneysiiyay!")
            else:
                messages.error(request, "Fadlan sax xogta shakhsiga.")
            return redirect('/settings/?tab=profile')

        elif action == 'change_password':
            form = UserPasswordChangeForm(request.POST)
            if form.is_valid():
                old_pass = form.cleaned_data['old_password']
                new_pass = form.cleaned_data['new_password']

                if not request.user.check_password(old_pass):
                    messages.error(request, "Furahaagii hore (Old Password) ma saxna! Fadlan dib u hubi.")
                    return redirect('/settings/?tab=password')

                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Furaha sirta ah (Password) si guul ah ayaa loo bedelay!")
                return redirect('/settings/?tab=password')
            else:
                for err in form.non_field_errors():
                    messages.error(request, err)
                return redirect('/settings/?tab=password')

    return redirect('settings_general')


@login_required
@admin_required
def settings_backup(request):
    backups = list_backup_files()
    db_path = settings.DATABASES['default']['NAME']
    db_size_mb = 0
    if os.path.exists(str(db_path)):
        db_size_mb = round(os.path.getsize(str(db_path)) / (1024 * 1024), 2)

    context = {
        'backups': backups,
        'db_size_mb': db_size_mb,
        'db_path': str(db_path),
        'active_tab': 'backup',
    }
    return render(request, 'settings/backup.html', context)


@login_required
@admin_required
def backup_create(request):
    if request.method == 'POST':
        db_path = str(settings.DATABASES['default']['NAME'])
        if os.path.exists(db_path):
            b_dir = get_backups_dir()
            ts = timezone.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"medicare_backup_{ts}.sqlite3"
            target_path = os.path.join(b_dir, backup_filename)
            shutil.copy2(db_path, target_path)

            file_size_kb = round(os.path.getsize(target_path) / 1024, 1)
            messages.success(request, f"Keydinta database-ka (Backup: {backup_filename} - {file_size_kb} KB) si guul ah ayaa loo abuuray!")
        else:
            messages.error(request, "Lama helin faylka database-ka!")

        return redirect(request.POST.get('next') or 'settings_backup')

    return redirect('settings_backup')





@login_required
def backup_download(request, filename):
    b_dir = get_backups_dir()
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(b_dir, safe_filename)

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/x-sqlite3')
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
        return response
    else:
        raise Http404("Faylka backup-ka lama helin.")


@login_required
def backup_delete(request, filename):
    if request.method == 'POST':
        b_dir = get_backups_dir()
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(b_dir, safe_filename)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                messages.warning(request, f"Faylkii backup-ka {safe_filename} waa la tirtiray.")
            except Exception as e:
                messages.error(request, f"Lama tirtiri karo faylka sababtoo ah wuu furan yahay ama waa la isticmaalayaa: {e}")
        else:
            messages.error(request, "Fadlan backup-ka lama helin.")

        return redirect(request.POST.get('next') or 'settings_backup')

    return redirect('settings_backup')


# ==========================================
# USERS & ROLE MANAGEMENT VIEWS (ADMIN ONLY)
# ==========================================
@login_required
@admin_required
def user_list(request):
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()

    users_qs = User.objects.all().order_by('-date_joined')

    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    if role_filter:
        users_qs = users_qs.filter(role__iexact=role_filter)
    if status_filter == 'active':
        users_qs = users_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        users_qs = users_qs.filter(is_active=False)

    total_users = User.objects.count()
    active_count = User.objects.filter(is_active=True).count()
    inactive_count = User.objects.filter(is_active=False).count()

    context = {
        'users': users_qs,
        'total_users': total_users,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'roles': User.ROLE_CHOICES,
        'query': query,
        'selected_role': role_filter,
        'selected_status': status_filter,
    }
    return render(request, 'users/user_list.html', context)


@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User-ka @{user.username} (Doorka: {user.role}) si guul leh ayaa loo abuuray!")
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'users/user_form.html', {'form': form, 'is_edit': False})


@login_required
@admin_required
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Macluumaadka user-ka @{user_obj.username} si guul leh ayaa loo cusbooneysiiyay!")
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user_obj)
    return render(request, 'users/user_form.html', {'form': form, 'is_edit': True, 'user_obj': user_obj})


@login_required
@admin_required
def user_toggle_status(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.pk == request.user.pk:
        messages.error(request, "Ma xiri kartid akoonka aad hadda ku jirto!")
        return redirect('user_list')

    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    status_str = "waa la furay (Active)" if user_obj.is_active else "waa la xiray (Inactive)"
    messages.success(request, f"Akoonka @{user_obj.username} {status_str}.")
    return redirect('user_list')


@login_required
@admin_required
def user_reset_password(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserAdminPasswordResetForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data['new_password']
            user_obj.set_password(new_pass)
            user_obj.save()
            messages.success(request, f"Furaha sirta ah ee @{user_obj.username} si guul leh ayaa loo bedelay!")
            return redirect('user_list')
    else:
        form = UserAdminPasswordResetForm()
    return render(request, 'users/user_reset_password.html', {'form': form, 'user_obj': user_obj})


@login_required
@admin_required
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.pk == request.user.pk:
        messages.error(request, "Ma tirtiri kartid akoonka aad hadda ku jirto!")
        return redirect('user_list')
    username = user_obj.username
    user_obj.delete()
    messages.warning(request, f"User-kii @{username} gabi ahaanba waa la tirtiray.")
    return redirect('user_list')








