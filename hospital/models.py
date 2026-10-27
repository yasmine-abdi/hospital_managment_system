from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ==========================================
# 1. ACCOUNT AND AUTHENTICATION
# ==========================================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'), 
        ('Doctor', 'Doctor'), 
        ('Nurse', 'Nurse'),
        ('Pharmacist', 'Pharmacist'), 
        ('Lab Technician', 'Lab Technician'),
        ('Receptionist', 'Receptionist'),
        ('Accountant', 'Accountant'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Admin')

    @property
    def is_admin_user(self):
        return self.is_superuser or self.role == 'Admin'

    @property
    def is_doctor_user(self):
        return self.role == 'Doctor'

    @property
    def is_nurse_user(self):
        return self.role == 'Nurse'

    @property
    def is_pharmacist_user(self):
        return self.role == 'Pharmacist'

    @property
    def is_lab_user(self):
        return self.role == 'Lab Technician'

    @property
    def is_receptionist_user(self):
        return self.role == 'Receptionist'

    @property
    def is_accountant_user(self):
        return self.role == 'Accountant'

    def __str__(self):
        return f"{self.username} ({self.role})"

# ==========================================
# 2. PROFILES (Doctor, Nurse, Receptionist)
# ==========================================


class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    qualification = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)

    def __str__(self): return f"Nurse {self.user.username}"

class Receptionist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='receptionist_profile')
    shift = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)

    def __str__(self): return f"Receptionist {self.user.username}"

# ==========================================
# 3. RECEPTION & PATIENT MANAGEMENT
# ==========================================
class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    phone = models.CharField(max_length=15)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, related_name='patients')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
    # ==========================================
# 3. DOCTOR MANAGEMENT (Sida uu PDF-ka ku qoran yahay)
# ==========================================
class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True) # Tusaale: Cardiology, Pediatrics

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, related_name='doctors')
    phone = models.CharField(max_length=50)
    shift_start = models.TimeField(null=True, blank=True) # Waqtiga uu shaqada bilaabo
    shift_end = models.TimeField(null=True, blank=True)   # Waqtiga uu shaqada dhameeyo
    is_available = models.BooleanField(default=True)      # Hubinta inuu dhakhtarku joogo

    def __str__(self): 
        return f"Dr. {self.user.first_name} {self.user.last_name} ({self.specialization.name if self.specialization else 'N/A'})"
# ==========================================
# 4. HR & STAFF MANAGEMENT
# ==========================================
class Staff(models.Model):
    DEPARTMENT_CHOICES = [
        ('Administration', 'Maamulka & Xafiiska (Administration)'),
        ('Medical / OPD', 'Dhaqaatiirta & OPD (Medical)'),
        ('Nursing', 'Kalkaaliyayaasha (Nursing)'),
        ('Pharmacy', 'Farmashiyaha (Pharmacy)'),
        ('Laboratory', 'Sheybaarka (Laboratory)'),
        ('Finance & Billing', 'Xisaabta & Lacag-qabashada (Finance)'),
        ('Human Resources', 'Shaqaalaha & HR (Human Resources)'),
        ('Security & Logistics', 'Amniga & Gaadiidka (Logistics)'),
        ('Cleaning & Maintenance', 'Nadaafadda & Dayactirka (Maintenance)'),
    ]

    SHIFT_CHOICES = [
        ('Morning', 'Subax (Morning: 07:00 - 15:00)'),
        ('Evening', 'Galab (Evening: 15:00 - 23:00)'),
        ('Night', 'Habeen (Night: 23:00 - 07:00)'),
        ('Full Time', 'Maalin Buuxda (Full Day)'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Shaqada Ku Jira (Active)'),
        ('On Leave', 'Fasax Ku Maqan (On Leave)'),
        ('Suspended', 'Hakad Ku Jira (Suspended)'),
        ('Resigned', 'Shaqada Ka Tagay (Resigned)'),
        ('Terminated', 'La Eryay (Terminated)'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Lab (Male)'),
        ('Female', 'Dhedig (Female)'),
        ('Other', 'Kale'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='Administration')
    designation = models.CharField(max_length=100, default='Staff Member')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True, help_text="Shahaadada / Takhasuska")
    experience_years = models.PositiveIntegerField(default=0)
    shift = models.CharField(max_length=30, choices=SHIFT_CHOICES, default='Morning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Mushaharka bishii ($)")
    hire_date = models.DateField(default=timezone.now)
    emergency_contact = models.CharField(max_length=150, blank=True, null=True, help_text="Qofka lagala xiriiro xaaladaha degdegga ah")
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.employee_id:
            self.employee_id = f"EMP-{self.hire_date.year if self.hire_date else timezone.now().year}-{self.pk:04d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        emp = self.employee_id or f"EMP-{self.pk}"
        return f"{emp} - {full_name} ({self.designation})"

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class StaffAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Jooga (Present)'),
        ('Late', 'Soo Daahay (Late)'),
        ('Absent', 'Maqan (Absent)'),
        ('Half Day', 'Nus Maalin (Half Day)'),
        ('On Leave', 'Fasax (On Leave)'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_attendances')
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('staff', 'date')
        ordering = ['-date', 'staff__user__first_name']

    def __str__(self):
        return f"{self.staff.user.get_full_name() or self.staff.user.username} - {self.date} ({self.status})"


class StaffLeave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Annual', 'Fasaxa Sanadka (Annual Leave)'),
        ('Sick', 'Fasaxa Xanuunka (Sick Leave)'),
        ('Maternity/Paternity', 'Fasaxa Umusha / Aabaha (Maternity/Paternity)'),
        ('Emergency', 'Fasax Degdeg Ah (Emergency Leave)'),
        ('Unpaid', 'Fasax Bilaa Mushahar Ah (Unpaid Leave)'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Sugaya (Pending)'),
        ('Approved', 'La Oggolaaday (Approved)'),
        ('Rejected', 'La Diiday (Rejected)'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES, default='Annual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    admin_remarks = models.TextField(blank=True, null=True)

    @property
    def days_count(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.staff.user.get_full_name() or self.staff.user.username} - {self.leave_type} ({self.status})"


class StaffPayroll(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Bank Transfer', 'Xawaalad / Bank Transfer'),
        ('EVC Plus / Mobile Money', 'EVC Plus / Zaad / Sahal'),
        ('Cash', 'Kaash (Cash)'),
        ('Cheque', 'Jeeg (Cheque)'),
    ]

    STATUS_CHOICES = [
        ('Paid', 'La Bixiyay (Paid)'),
        ('Pending', 'Sugaya (Pending)'),
        ('Cancelled', 'La Joojiyay (Cancelled)'),
    ]

    payroll_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='payrolls')
    salary_month = models.CharField(max_length=30, help_text="Tusaale: October 2026")
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Gunnada (Allowances/Overtime)")
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Jarista (Deductions/Taxes/Absences)")
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Bank Transfer')
    payment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Paid')
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Trx ID / Bank Reference")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_payrolls')

    def save(self, *args, **kwargs):
        self.net_salary = (self.basic_salary or 0) + (self.allowances or 0) - (self.deductions or 0)
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.payroll_number:
            self.payroll_number = f"PAY-{self.payment_date.year}-{self.pk:05d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        p_num = self.payroll_number or f"PAY #{self.pk}"
        return f"{p_num} - {self.staff.user.get_full_name() or self.staff.user.username} ({self.salary_month}: ${self.net_salary})"


# ==========================================
# 5. APPOINTMENT MANAGEMENT
# ==========================================
class Appointment(models.Model):
    STATUS = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Completed', 'Completed')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')

# ==========================================
# 5.5. OUTPATIENT DEPARTMENT (OPD) MANAGEMENT
# ==========================================
class OPDVisit(models.Model):
    VISIT_TYPE_CHOICES = [
        ('New Visit', 'Bukaan Cusub (New Visit)'),
        ('Follow-up', 'Soo Noqosho (Follow-up)'),
        ('Emergency', 'Degdeg (Emergency)'),
        ('Routine Checkup', 'Baaritaan Guud (Routine Checkup)'),
    ]
    STATUS_CHOICES = [
        ('Waiting', 'Sugaya (In Waiting Queue)'),
        ('Triage Done', 'Vitals La Qabtay (Triage Done)'),
        ('In Consultation', 'Dhakhtarka La Jooga (With Doctor)'),
        ('Completed', 'Dhamaaday (Completed)'),
        ('Cancelled', 'La Joojiyay (Cancelled)'),
    ]
    PAYMENT_CHOICES = [
        ('Paid', 'Bixiyay (Paid)'),
        ('Unpaid', 'Lama Bixin (Unpaid)'),
        ('Waived', 'Bilaash (Waived)'),
    ]

    visit_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    token_number = models.PositiveIntegerField(default=1)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='opd_visits')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='opd_visits')
    department = models.CharField(max_length=100, default='General OPD')
    visit_type = models.CharField(max_length=50, choices=VISIT_TYPE_CHOICES, default='New Visit')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Waiting')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Paid')
    triage_nurse = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='triaged_visits')
    visit_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.visit_number:
            self.visit_number = f"OPD-{timezone.now().year}-{self.pk:04d}"
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = OPDVisit.objects.filter(visit_date__gte=today_start).count()
            self.token_number = today_count if today_count > 0 else 1
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    def __str__(self):
        v_num = self.visit_number or f"Visit #{self.pk}"
        return f"{v_num} (Token #{self.token_number}) - {self.patient.name}"

    class Meta:
        ordering = ['-visit_date']


class OPDVitalSign(models.Model):
    visit = models.OneToOneField(OPDVisit, on_delete=models.CASCADE, related_name='vitals')
    blood_pressure = models.CharField(max_length=20, blank=True, null=True, help_text='e.g. 120/80 mmHg')
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text='°C e.g. 37.0')
    pulse_rate = models.PositiveIntegerField(blank=True, null=True, help_text='bpm (Garaaca Wadnaha)')
    respiratory_rate = models.PositiveIntegerField(blank=True, null=True, help_text='breaths/min (Neefsiga)')
    oxygen_saturation = models.PositiveIntegerField(blank=True, null=True, help_text='SpO2 % (Ogsajiinta)')
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='kg (Miisaanka)')
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='cm (Dhererka)')
    bmi = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text='Body Mass Index')
    blood_sugar = models.CharField(max_length=50, blank=True, null=True, help_text='e.g. 110 mg/dL (RBS)')
    triage_notes = models.TextField(blank=True, null=True, help_text='Faallooyinka kalkaalisada triage-ka')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.weight and self.height and float(self.height) > 0:
            h_m = float(self.height) / 100.0
            self.bmi = round(float(self.weight) / (h_m * h_m), 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vitals for {self.visit.visit_number} - BP: {self.blood_pressure}, Temp: {self.temperature}°C"


class OPDConsultation(models.Model):
    OUTCOME_CHOICES = [
        ('Discharged', 'Guriga Loo Fasaxay (Sent Home)'),
        ('Admit to IPD', 'Bukaan-Jiif Loo Gudbiyey (Admit to Ward)'),
        ('Referral', 'Takhasus Sare Loo Gudbiyey (Referred)'),
        ('Follow-up', 'Ballan Dambe (Follow-up Scheduled)'),
    ]

    visit = models.OneToOneField(OPDVisit, on_delete=models.CASCADE, related_name='consultation')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='opd_consultations')
    chief_complaint = models.TextField(help_text='Cabashada ugu weyn ee bukaanku u yimid')
    history_of_illness = models.TextField(blank=True, null=True, help_text='Taariikhda xanuunka (HPI)')
    physical_examination = models.TextField(blank=True, null=True, help_text='Baaritaanka jirka ee dhakhtarka')
    diagnosis = models.CharField(max_length=255, help_text='Cudurka la helay / Provisional Diagnosis')
    clinical_notes = models.TextField(blank=True, null=True, help_text='Talada caafimaad iyo qoraalada dhakhtarka')
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES, default='Discharged')
    next_follow_up = models.DateField(blank=True, null=True, help_text='Taariikhda ballanta dambe haddii loo baahdo')
    consultation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Consultation: {self.visit.patient.name} - {self.diagnosis}"


class OPDPrescriptionItem(models.Model):
    consultation = models.ForeignKey(OPDConsultation, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, help_text='e.g. 500mg, 1 tablet')
    frequency = models.CharField(max_length=100, help_text='e.g. 1x3 (3 jeer maalintii)')
    duration = models.CharField(max_length=100, help_text='e.g. 5 maalmood')
    instructions = models.CharField(max_length=200, blank=True, null=True, help_text='e.g. Cuntada kadib')

    def __str__(self):
        return f"{self.medicine_name} ({self.dosage}) - {self.frequency}"


# ==========================================
# 6. PHARMACY MANAGEMENT
# ==========================================
class Medicine(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

class PharmacySale(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, related_name='pharmacy_sales')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.0)
    sale_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.invoice_number:
            self.invoice_number = f"INV-{self.pk:03d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    def __str__(self):
        patient_name = self.patient.name if self.patient else "Walk-in"
        inv = self.invoice_number if self.invoice_number else f"Sale #{self.id}"
        return f"{inv} - {patient_name}"

class PharmacySaleItem(models.Model):
    sale = models.ForeignKey(PharmacySale, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    total = models.DecimalField(max_digits=18, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

# ==========================================
# 7. INPATIENT MANAGEMENT (IPD)
# ==========================================
class Ward(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Bed(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    bed_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        room_info = f"Room {self.room_number} - " if self.room_number else ""
        return f"{self.ward.name} - {room_info}Bed {self.bed_number}"

class Admission(models.Model):
    STATUS_CHOICES = [
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged')
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    admission_date = models.DateTimeField(default=timezone.now)
    expected_discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Admitted')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Admission #{self.id} of {self.patient.name} - Bed: {self.bed.bed_number}"

# ==========================================
# 7.5. LABORATORY MANAGEMENT (LIS)
# ==========================================
class LabCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='biotech', help_text='Icon name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Lab Categories'
        ordering = ['name']


class LabTest(models.Model):
    category = models.ForeignKey(LabCategory, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    sample_type = models.CharField(max_length=100, default='Blood', help_text='e.g. Blood, Urine, Stool, Serum')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    turnaround_time = models.CharField(max_length=50, default='1-2 hours', help_text='Expected result time')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['name']


class LabTestParameter(models.Model):
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True, null=True)
    reference_range = models.CharField(max_length=100, blank=True, null=True)
    default_status = models.CharField(max_length=20, default='Normal')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.test.name} - {self.name}"

    class Meta:
        ordering = ['order', 'id']


class LabRequest(models.Model):
    PRIORITY_CHOICES = [
        ('Routine', 'Routine (Caadi)'),
        ('Urgent', 'Urgent (Degdeg)'),
        ('STAT', 'STAT (Xaalad Degdeg Ah)'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending (Sugaya)'),
        ('Sample Collected', 'Sample Collected (Muunada la qaaday)'),
        ('In Progress', 'In Progress (Socda)'),
        ('Completed', 'Completed (Dhamaaday)'),
        ('Cancelled', 'Cancelled (La joojiyay)'),
    ]
    PAYMENT_CHOICES = [
        ('Paid', 'Bixiyay (Paid)'),
        ('Unpaid', 'Lama Bixin (Unpaid)'),
        ('Waived', 'Bilaash (Waived)'),
    ]

    order_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_requests')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_requests')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_lab_requests')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Routine')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Unpaid')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    clinical_notes = models.TextField(blank=True, null=True, help_text='Sababta baaritaanka ama calaamadaha')
    created_at = models.DateTimeField(default=timezone.now)
    sample_collected_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.order_number:
            self.order_number = f"LAB-{timezone.now().year}-{self.pk:04d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    def __str__(self):
        order_num = self.order_number or f"Order #{self.pk}"
        return f"{order_num} - {self.patient.name}"

    class Meta:
        ordering = ['-created_at']


class LabRequestItem(models.Model):
    request = models.ForeignKey(LabRequest, on_delete=models.CASCADE, related_name='items')
    test = models.ForeignKey(LabTest, on_delete=models.PROTECT, related_name='order_items')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.request.order_number or self.request.id} - {self.test.name}"


class LabResult(models.Model):
    request = models.ForeignKey(LabRequest, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='results')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    performed_at = models.DateTimeField(default=timezone.now)
    overall_interpretation = models.TextField(blank=True, null=True, help_text='Faallada guud ee natiijada')
    is_abnormal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result: {self.test.name} for {self.request.order_number or self.request.id}"


class LabResultItem(models.Model):
    FLAG_CHOICES = [
        ('Normal', 'Normal'),
        ('High', 'High (Sareeyo)'),
        ('Low', 'Low (Hooseeyo)'),
        ('Abnormal', 'Abnormal (Aan Caadi Ahayn)'),
        ('Positive', 'Positive (+)'),
        ('Negative', 'Negative (-)'),
    ]
    result = models.ForeignKey(LabResult, on_delete=models.CASCADE, related_name='values')
    parameter_name = models.CharField(max_length=150)
    result_value = models.CharField(max_length=150)
    unit = models.CharField(max_length=50, blank=True, null=True)
    reference_range = models.CharField(max_length=100, blank=True, null=True)
    flag = models.CharField(max_length=20, choices=FLAG_CHOICES, default='Normal')

    def __str__(self):
        return f"{self.parameter_name}: {self.result_value} ({self.flag})"


# ==========================================
# 8. BILLING AND FINANCE
# ==========================================
class Bill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    is_paid = models.BooleanField(default=False)


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Lama Bixin (Unpaid)'),
        ('Partially Paid', 'Qayb Baa La Bixiyay (Partially Paid)'),
        ('Paid', 'Waa La Bixiyay (Paid)'),
        ('Overdue', 'Waqtigu Dhaafay (Overdue)'),
        ('Cancelled', 'La Joojiyay (Cancelled)'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Kaash (Cash)'),
        ('EVC Plus / Mobile Money', 'EVC Plus / Zaad / Sahal'),
        ('Credit Card', 'Kaarka Bangiga (Card)'),
        ('Bank Transfer', 'Xawaalad / Bank Transfer'),
        ('Insurance', 'Caymis (Insurance)'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    billing_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Unpaid')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    notes = models.TextField(blank=True, null=True, help_text='Faahfaahin ama ogeysiis')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.balance_due = max(0, float(self.total_amount) - float(self.paid_amount))
        if float(self.paid_amount) >= float(self.total_amount) and float(self.total_amount) > 0:
            self.status = 'Paid'
        elif float(self.paid_amount) > 0:
            self.status = 'Partially Paid'
        super().save(*args, **kwargs)
        if is_new and not self.invoice_number:
            self.invoice_number = f"INV-{timezone.now().year}-{self.pk:04d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)

    def __str__(self):
        inv_num = self.invoice_number or f"Invoice #{self.pk}"
        return f"{inv_num} - {self.patient.name} (${self.total_amount})"

    class Meta:
        ordering = ['-billing_date']


class InvoiceItem(models.Model):
    SERVICE_CHOICES = [
        ('Consultation', 'Qidmada Dhakhtarka (OPD)'),
        ('Laboratory', 'Baaritaanka Shaybaarka (Lab)'),
        ('Pharmacy', 'Daawooyinka (Pharmacy)'),
        ('Inpatient / Bed', 'Jiifka & Sariirta (IPD)'),
        ('Surgery', 'Qalliinka (Operation)'),
        ('Nursing Care', 'Daryeelka Kalkaalisada'),
        ('Radiology', 'Raajada (X-Ray / Scan)'),
        ('Other', 'Adeegyo Kale (Other)'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='Consultation')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = float(self.quantity) * float(self.unit_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} (${self.total_price})"


class PaymentTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('EVC Plus / Mobile Money', 'EVC Plus / Zaad / Sahal'),
        ('Cash', 'Kaash (Cash)'),
        ('Credit Card', 'Kaarka Bangiga (Card)'),
        ('Bank Transfer', 'Xawaalad / Bank Transfer'),
        ('Insurance', 'Caymis (Insurance)'),
    ]

    transaction_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text='EVC Plus TXID ama Reference')
    payment_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.transaction_id:
            self.transaction_id = f"TRX-{timezone.now().year}-{self.pk:05d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        total_paid = sum(p.amount for p in self.invoice.payments.all())
        self.invoice.paid_amount = total_paid
        self.invoice.save()

    def __str__(self):
        tx = self.transaction_id or f"TRX #{self.pk}"
        return f"{tx} - ${self.amount} for {self.invoice.invoice_number}"

    class Meta:
        ordering = ['-payment_date']


# ==========================================
# 9. DASHBOARD & 10. REPORT
# ==========================================
class GeneratedReport(models.Model):
    report_type = models.CharField(max_length=100)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    summary_data = models.TextField()


# ==========================================
# 11. HOSPITAL & SYSTEM SETTINGS
# ==========================================
class HospitalSetting(models.Model):
    hospital_name = models.CharField(max_length=200, default='MediCare General Hospital')
    hospital_tagline = models.CharField(max_length=250, default='Daryeel Caafimaad oo Casri ah & Daacadnimo')
    phone = models.CharField(max_length=50, default='+252 61 500 0000')
    email = models.EmailField(default='info@medicarehospital.so')
    address = models.CharField(max_length=255, default='Ex-Digfeer Road, Hodan District, Mogadishu, Somalia')
    website = models.URLField(default='https://medicarehospital.so', blank=True, null=True)
    logo = models.FileField(upload_to='hospital_logos/', null=True, blank=True)
    currency_symbol = models.CharField(max_length=10, default='$')
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    invoice_prefix = models.CharField(max_length=20, default='INV')
    opd_prefix = models.CharField(max_length=20, default='OPD')
    lab_prefix = models.CharField(max_length=20, default='LAB')
    invoice_disclaimer = models.TextField(default='Mahadsanid. Rasiidkan waa caddeyn rasmi ah oo muujinaysa bixinta adeegyada caafimaadka ee MediCare HMS.')
    enable_sms_alerts = models.BooleanField(default=True)
    enable_email_receipts = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(id=1)
        return setting

    def __str__(self):
        return self.hospital_name
