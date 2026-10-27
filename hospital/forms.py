from django import forms
from .models import (
    User, Patient, Doctor, Specialization, Appointment, Medicine, PharmacySale, PharmacySaleItem,
    Ward, Bed, Admission,
    OPDVisit, OPDVitalSign, OPDConsultation, OPDPrescriptionItem,
    LabCategory, LabTest, LabTestParameter, LabRequest, LabRequestItem, LabResult, LabResultItem,
    Invoice, InvoiceItem, PaymentTransaction,
    Staff, StaffAttendance, StaffLeave, StaffPayroll,
    HospitalSetting
)

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        # Halkan ku dar field-yada aad ku leedahay model-kaaga
        fields = ['name', 'age', 'gender', 'address', 'phone', 'doctor']
        
        # Halkan waxaad ku qurxin kartaa CSS-ka form-ka
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca Bukaanka'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Da\'da'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Cinwaanka'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lambarka Telefoonka'}),
        }
        
class DoctorForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, label='Fullname (Magaca Buuxa)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Geli magaca buuxa ee dhakhtarka'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Haddii xogta la bedelayo (update), magaca horay ugu jirtay soo saar
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['full_name'].initial = f"{self.instance.user.first_name} {self.instance.user.last_name}".strip() or self.instance.user.username
        
    class Meta:
        model = Doctor
        fields = ['specialization', 'phone', 'shift_start', 'shift_end', 'is_available']
        
        labels = {
            'specialization': 'Takhasuska (Specialization)',
            'phone': 'Lambarka Telefoonka',
            'shift_start': 'Saacadda uu Bilaabayo',
            'shift_end': 'Saacadda uu Bixi doono',
            'is_available': 'Wuu Joogaa (Available)'
        }
        
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Geli talefoonka dhakhtarka'}),
            'shift_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        doctor = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name').strip()
        names = full_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''

        if not doctor.pk:
            # Haddii dhakhtar cusub la diiwaangelinayo, samee User account cusub
            from django.contrib.auth import get_user_model
            User = get_user_model()
            base_username = first_name.lower()
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username, 
                password='password123', # Password kumeel gaar ah
                first_name=first_name, 
                last_name=last_name, 
                role='Doctor'
            )
            doctor.user = user
        else:
            # Haddii magaca la bedelayo, cusboonaysii User-ka
            doctor.user.first_name = first_name
            doctor.user.last_name = last_name
            doctor.user.save()

        if commit:
            doctor.save()
        return doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'status']
        labels = {
            'patient': 'Bukaanka (Patient)',
            'doctor': 'Dhakhtarka (Doctor)',
            'appointment_date': 'Taariikhda iyo Saacadda (Date & Time)',
            'status': 'Xaaladda (Status)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-control'}),
            'appointment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
        }

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'batch_number', 'expiry_date', 'stock_quantity', 'unit_price']
        labels = {
            'name': 'Magaca Daawada (Medicine Name)',
            'description': 'Faahfaahin (Description)',
            'batch_number': 'Batch Number',
            'expiry_date': 'Taariikhda Dhicitaanka (Expiry Date)',
            'stock_quantity': 'Tirada Kaydka (Stock Quantity)',
            'unit_price': 'Qiimaha Xabadda (Unit Price)'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca daawada'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Faahfaahinta...'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tusaale: BATCH-001'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PharmacySaleForm(forms.ModelForm):
    class Meta:
        model = PharmacySale
        fields = ['patient']
        labels = {
            'patient': 'Bukaanka (Patient)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
        }

# ==========================================
# INPATIENT (IPD) FORMS
# ==========================================

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name']
        labels = {'name': 'Ward Name'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., General Ward'}),
        }

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['ward', 'room_number', 'bed_number', 'is_available']
        labels = {
            'ward': 'Qeybta (Ward)',
            'room_number': 'Nambarka Qolka (Room Number)',
            'bed_number': 'Nambarka Sariirta (Bed Number)',
            'is_available': 'Waa Banaan Tahay (Available)?'
        }
        widgets = {
            'ward': forms.Select(attrs={'class': 'form-select form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tusaale: Qolka 101'}),
            'bed_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tusaale: Sariirta A'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['patient', 'doctor', 'bed', 'admission_date', 'expected_discharge_date', 'status', 'notes']
        labels = {
            'patient': 'Bukaanka (Patient)',
            'doctor': 'Dhakhtarka Masuulka ah (Assigned Doctor)',
            'bed': 'Qolka iyo Sariirta (Room & Bed)',
            'admission_date': 'Taariikhda Gelitaanka (Admission Date)',
            'expected_discharge_date': 'Taariikhda Bixitaanka La Filayo (Expected Discharge)',
            'status': 'Xaaladda (Status)',
            'notes': 'Faahfaahin (Notes)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-control'}),
            'bed': forms.Select(attrs={'class': 'form-select form-control'}),
            'admission_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expected_discharge_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Geli wixii faahfaahin ah oo ku saabsan gelitaanka bukaanka...'})
        }

    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['bed'].queryset = Bed.objects.filter(is_available=True)
        else:
            self.fields['bed'].queryset = Bed.objects.filter(is_available=True) | Bed.objects.filter(pk=self.instance.bed.pk)


# ==========================================
# LABORATORY FORMS
# ==========================================
class LabRequestForm(forms.ModelForm):
    tests = forms.ModelMultipleChoiceField(
        queryset=LabTest.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Baaritaannada La Dalbanayo (Select Tests)"
    )

    class Meta:
        model = LabRequest
        fields = ['patient', 'doctor', 'priority', 'payment_status', 'clinical_notes']
        labels = {
            'patient': 'Bukaanka (Patient)',
            'doctor': 'Dhakhtarka Dalbay (Ordering Doctor)',
            'priority': 'Heerka Degdegga (Priority)',
            'payment_status': 'Xaaladda Lacag Bixinta (Payment Status)',
            'clinical_notes': 'Calaamadaha / Faahfaahin (Clinical Indications)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-select form-control'}),
            'clinical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Geli faahfaahinta ama calaamadaha bukaanka...'}),
        }


class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['category', 'name', 'code', 'sample_type', 'price', 'turnaround_time', 'description', 'is_active']
        labels = {
            'category': 'Qaybta (Category)',
            'name': 'Magaca Baaritaanka (Test Name)',
            'code': 'Koodhka (Test Code)',
            'sample_type': 'Nooca Muunada (Sample / Specimen)',
            'price': 'Qiimaha ($)',
            'turnaround_time': 'Waqtiga Natiijada (TAT)',
            'description': 'Faahfaahin',
            'is_active': 'Waa Shaqaynayaa (Active)'
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Complete Blood Count (CBC)'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CBC-001'}),
            'sample_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Whole Blood, Urine, Stool'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50'}),
            'turnaround_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1-2 hours'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class LabCategoryForm(forms.ModelForm):
    class Meta:
        model = LabCategory
        fields = ['name', 'description', 'icon']
        labels = {
            'name': 'Magaca Qaybta (Category Name)',
            'description': 'Faahfaahin (Description)',
            'icon': 'Astaanta (Icon name)'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hematology, Microbiology'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'biotech, bloodtype, science, etc.'})
        }


# ==========================================
# OUTPATIENT (OPD) FORMS
# ==========================================
class OPDVisitForm(forms.ModelForm):
    class Meta:
        model = OPDVisit
        fields = ['patient', 'doctor', 'department', 'visit_type', 'consultation_fee', 'payment_status']
        labels = {
            'patient': 'Bukaanka (Patient) *',
            'doctor': 'Dhakhtarka (Consulting Doctor)',
            'department': 'Qaybta (OPD Department)',
            'visit_type': 'Nooca Booqashada (Visit Type)',
            'consultation_fee': 'Lacagta Baaritaanka / Qidmada ($)',
            'payment_status': 'Lacag Bixinta (Payment Status)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. General OPD, Pediatrics, Cardiology'}),
            'visit_type': forms.Select(attrs={'class': 'form-select form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '1.00'}),
            'payment_status': forms.Select(attrs={'class': 'form-select form-control'}),
        }


class OPDVitalSignForm(forms.ModelForm):
    class Meta:
        model = OPDVitalSign
        fields = ['blood_pressure', 'temperature', 'pulse_rate', 'respiratory_rate', 'oxygen_saturation', 'weight', 'height', 'blood_sugar', 'triage_notes']
        labels = {
            'blood_pressure': 'Dhiigkarka (BP - mmHg)',
            'temperature': 'Heerkulka (Temp - °C)',
            'pulse_rate': 'Garaaca Wadnaha (Pulse - bpm)',
            'respiratory_rate': 'Neefsiga (Resp Rate - /min)',
            'oxygen_saturation': 'Ogsajiinta (SpO2 - %)',
            'weight': 'Miisaanka (Weight - kg)',
            'height': 'Dhererka (Height - cm)',
            'blood_sugar': 'Sonkorta Degdegga (RBS)',
            'triage_notes': 'Faallada Triage-ka (Nurse Notes)'
        }
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 120/80'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '37.0'}),
            'pulse_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '72'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '18'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '98'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': '65.0'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': '170'}),
            'blood_sugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 110 mg/dL'}),
            'triage_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Wixii xaalad ah oo kalkaalisadu aragtay...'}),
        }


class OPDConsultationForm(forms.ModelForm):
    class Meta:
        model = OPDConsultation
        fields = ['chief_complaint', 'history_of_illness', 'physical_examination', 'diagnosis', 'clinical_notes', 'outcome', 'next_follow_up']
        labels = {
            'chief_complaint': 'Cabashada Ugu Weyn (Chief Complaint) *',
            'history_of_illness': 'Taariikhda Xanuunka (History of Present Illness - HPI)',
            'physical_examination': 'Baaritaanka Jirka (Physical Examination)',
            'diagnosis': 'Cudurka Laga Helay (Provisional / Final Diagnosis) *',
            'clinical_notes': 'Talada Caafimaadka & Faallada Dhakhtarka',
            'outcome': 'Go\'aanka Dambe (Disposition / Outcome)',
            'next_follow_up': 'Taariikhda Ballanta Xigta (Next Follow-up Date)'
        }
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Sababta ugu weyn ee bukaanku u yimid (e.g. Madax xanuun daran, qandho iyo matag)'}),
            'history_of_illness': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Faahfaahinta xanuunka, goorta uu bilowday, iyo calaamadaha la socda...'}),
            'physical_examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Wixii dhakhtarku ku arkay baaritaanka jirka...'}),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acute Upper Respiratory Tract Infection (URTI)'}),
            'clinical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Talada guud ee bukaanka la siiyey...'}),
            'outcome': forms.Select(attrs={'class': 'form-select form-control'}),
            'next_follow_up': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# ==========================================
# BILLING AND INVOICING FORMS
# ==========================================
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'doctor', 'due_date', 'payment_method', 'discount', 'tax', 'notes']
        labels = {
            'patient': 'Bukaanka (Patient) *',
            'doctor': 'Dhakhtarka Masuulka ah (Doctor)',
            'due_date': 'Taariikhda Lacag Bixinta (Due Date)',
            'payment_method': 'Habka Lacag Bixinta (Payment Method)',
            'discount': 'Qiimo Dhimis / Discount ($)',
            'tax': 'Canshuur / Tax ($)',
            'notes': 'Faahfaahin / Xusuusin (Notes)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'value': '0.00'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'value': '0.00'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Xusuusin ama shuruudaha lacag bixinta...'}),
        }


class PaymentTransactionForm(forms.ModelForm):
    class Meta:
        model = PaymentTransaction
        fields = ['amount', 'payment_method', 'reference_number', 'notes']
        labels = {
            'amount': 'Cadadka Lacagta La Qabtay ($) *',
            'payment_method': 'Habka Lacagta Lagu Bixiyay *',
            'reference_number': 'Nambarka Tixraaca (EVC Plus TXID / Ref)',
            'notes': 'Faahfaahin Dheeraad ah'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'placeholder': '0.00'}),
            'payment_method': forms.Select(attrs={'class': 'form-select form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tusaale: TXID-987654321 ama EVC Plus Ref'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Faahfaahin kasta oo dheeraad ah...'}),
        }


# ==========================================
# HR & STAFF FORMS
# ==========================================
class StaffForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, label='Magaca Koowaad (First Name) *', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca hore'}))
    last_name = forms.CharField(max_length=100, label='Magaca Labaad (Last Name) *', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca qoyska / aabaha'}))
    username = forms.CharField(max_length=100, required=False, label='Magaca Gelitaanka (Username)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Haddii aad ka tagto, si toos ah ayaa loo samaynayaa'}))
    password = forms.CharField(max_length=100, required=False, label='Furaha Sirta ah (Password)', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Furaha sirta ah ee koontada'}))

    class Meta:
        model = Staff
        fields = [
            'employee_id', 'department', 'designation', 'gender', 'phone', 'email',
            'qualification', 'experience_years', 'shift', 'status', 'salary',
            'hire_date', 'emergency_contact', 'address', 'notes'
        ]
        labels = {
            'employee_id': 'Lambarka Aqoonsiga Shaqaalaha (Employee ID)',
            'department': 'Qaybta Shaqada (Department) *',
            'designation': 'Darajada / Xilka (Designation) *',
            'gender': 'Jinsiga (Gender) *',
            'phone': 'Telefoonka (Phone Number) *',
            'email': 'Email-ka (Email Address)',
            'qualification': 'Aqoonta / Shahaadada (Qualification)',
            'experience_years': 'Khibradda (Sanooyin)',
            'shift': 'Waqtiga Shaqada (Work Shift) *',
            'status': 'Xaaladda Shaqada (Employment Status) *',
            'salary': 'Mushaharka Bishii ($) *',
            'hire_date': 'Taariikhda Shaqo Bilowga (Hire Date) *',
            'emergency_contact': 'Qofka Degdegga ah (Emergency Contact)',
            'address': 'Cinwaanka / Deegaanka (Address)',
            'notes': 'Faallo / Xusuusin Dheeraad ah'
        }
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EMP-2026-0001 (ama banaan u dhaaf)'}),
            'department': forms.Select(attrs={'class': 'form-select form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Nurse, Lab Tech, Cashier'}),
            'gender': forms.Select(attrs={'class': 'form-select form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +252 61 5000000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. staff@hospital.so'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BSc Nursing, Diploma MLT, MD'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'shift': forms.Select(attrs={'class': 'form-select form-control'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '10.00', 'placeholder': '450.00'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca qofka & telefoonkiisa'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Degmada, Xaafadda, Jidka...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Xusuusin ku saabsan shaqaalaha...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['username'].initial = self.instance.user.username


class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = ['staff', 'date', 'status', 'check_in', 'check_out', 'notes']
        labels = {
            'staff': 'Shaqaalaha (Staff Member) *',
            'date': 'Taariikhda (Date) *',
            'status': 'Xaaladda Xaadirka (Status) *',
            'check_in': 'Waqtiga Soo Gelitaanka (Check In)',
            'check_out': 'Waqtiga Baxitaanka (Check Out)',
            'notes': 'Faallada / Sababta Dib-u-dhaca'
        }
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
            'check_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sababta dib u dhaca ama faahfaahin'}),
        }


class StaffLeaveForm(forms.ModelForm):
    class Meta:
        model = StaffLeave
        fields = ['staff', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'admin_remarks']
        labels = {
            'staff': 'Shaqaalaha Codsanaya (Staff Member) *',
            'leave_type': 'Nooca Fasaxa (Leave Type) *',
            'start_date': 'Taariikhda Bilowga (Start Date) *',
            'end_date': 'Taariikhda Dhammaadka (End Date) *',
            'reason': 'Sababta Fasaxa (Reason for Leave) *',
            'status': 'Xaaladda Codsiga (Status)',
            'admin_remarks': 'Go\'aanka & Faallada Maamulka'
        }
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Sababta uu fasaxa u doonayo shaqaaluhu...'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
            'admin_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Jawaabta maamulka ama shuruudaha...'}),
        }


class StaffPayrollForm(forms.ModelForm):
    class Meta:
        model = StaffPayroll
        fields = [
            'staff', 'salary_month', 'basic_salary', 'allowances', 'deductions',
            'payment_method', 'payment_date', 'status', 'reference_number', 'notes'
        ]
        labels = {
            'staff': 'Shaqaalaha (Staff Member) *',
            'salary_month': 'Bisha Mushaharka (Salary Month) *',
            'basic_salary': 'Mushaharka Asaasiga ah ($) *',
            'allowances': 'Gunno / Overtime ($)',
            'deductions': 'Jarista / Deductions ($)',
            'payment_method': 'Habka Lacag Bixinta (Payment Method) *',
            'payment_date': 'Taariikhda Bixinta (Payment Date) *',
            'status': 'Xaaladda (Payment Status) *',
            'reference_number': 'Tixraaca Bixinta (Bank Ref / Trx ID)',
            'notes': 'Faahfaahin Dheeraad ah'
        }
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select form-control', 'id': 'staffSelect'}),
            'salary_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. October 2026'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'id': 'basicSalaryInput', 'step': '0.50', 'placeholder': '0.00'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control', 'id': 'allowancesInput', 'step': '0.50', 'value': '0.00'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'id': 'deductionsInput', 'step': '0.50', 'value': '0.00'}),
            'payment_method': forms.Select(attrs={'class': 'form-select form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TXID-123456 ama Bank Ref'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Faallo ku saabsan bixinta mushaharka...'}),
        }


# ==========================================
# SETTINGS FORMS
# ==========================================
class HospitalSettingForm(forms.ModelForm):
    class Meta:
        model = HospitalSetting
        fields = [
            'hospital_name', 'hospital_tagline', 'phone', 'email', 'address', 'website',
            'logo', 'currency_symbol', 'tax_percentage', 'invoice_prefix', 'opd_prefix', 'lab_prefix',
            'invoice_disclaimer', 'enable_sms_alerts', 'enable_email_receipts'
        ]
        labels = {
            'hospital_name': 'Magaca Isbitaalka (Hospital Name) *',
            'hospital_tagline': 'Halkudhigga Isbitaalka (Slogan / Tagline)',
            'phone': 'Telefoonka Xiriirka (Phone Number) *',
            'email': 'Email-ka Rasmiga ah (Email Address) *',
            'address': 'Cinwaanka / Goobta (Physical Address) *',
            'website': 'Webseetka (Website URL)',
            'logo': 'Astaanta Isbitaalka (Hospital Logo)',
            'currency_symbol': 'Astaanta Lacagta (Currency Symbol)',
            'tax_percentage': 'Canshuurta (Tax %)',
            'invoice_prefix': 'Prefix-ka Qaansada (Invoice Prefix)',
            'opd_prefix': 'Prefix-ka OPD (OPD Token Prefix)',
            'lab_prefix': 'Prefix-ka Shaybaarka (Lab Order Prefix)',
            'invoice_disclaimer': 'Qoraalka Hoos Ee Rasiidhada (Invoice Footer / Terms)',
            'enable_sms_alerts': 'Fariimaha SMS-ka (Enable SMS Alerts)',
            'enable_email_receipts': 'Rasiidhada Email-ka (Email Invoices)',
        }
        widgets = {
            'hospital_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MediCare General Hospital'}),
            'hospital_tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Daryeel Caafimaad oo Casri ah'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +252 61 500 0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. info@medicarehospital.so'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hodan, Mogadishu, Somalia'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://medicarehospital.so'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INV'}),
            'opd_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OPD'}),
            'lab_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LAB'}),
            'invoice_disclaimer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Mahadsanid...'}),
            'enable_sms_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_email_receipts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Magaca Koowaad (First Name)',
            'last_name': 'Magaca Labaad (Last Name)',
            'email': 'Email-ka Shakhsiga (Email Address)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Furaha Sirta ah ee Hadda (Current Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Geli furahaaga hadda'}),
    )
    new_password = forms.CharField(
        label='Furaha Sirta ah ee Cusub (New Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ugu yaraan 6 xaraf'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        label='Xaqiiji Furaha Cusub (Confirm Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dib u geli furaha cusub'}),
        min_length=6
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get('new_password')
        confirm_pass = cleaned_data.get('confirm_password')

        if new_pass and confirm_pass and new_pass != confirm_pass:
            raise forms.ValidationError("Labada fure ee cusub isma leha! Fadlan si sax ah u hubi.")
        return cleaned_data


# ==========================================
# USER & ROLE MANAGEMENT FORMS (ADMIN)
# ==========================================
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label='Furaha Sirta ah (Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ugu yaraan 6 xaraf'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        label='Xaqiiji Furaha Sirta ah (Confirm Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dib u geli furaha sirta'}),
        min_length=6
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']
        labels = {
            'username': 'Magaca Galitaanka (Username) *',
            'first_name': 'Magaca Koowaad (First Name)',
            'last_name': 'Magaca Labaad (Last Name)',
            'email': 'Email-ka (Email Address)',
            'role': 'Doorka / Shaqada (System Role) *',
            'is_active': 'Akoonku Wuu Shaqaynayaa (Active)',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tusaale: dr.ali ama nurse.amina'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca hore'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca aabbaha/qoyska'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'user@hospital.com'}),
            'role': forms.Select(attrs={'class': 'form-select form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Magacan galitaanka (username) hore ayaa loo qaatay! Fadlan dooro mid kale.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Labada fure ee sirta ah isma leha! Fadlan si sax ah u qor.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active']
        labels = {
            'first_name': 'Magaca Koowaad (First Name)',
            'last_name': 'Magaca Labaad (Last Name)',
            'email': 'Email-ka (Email Address)',
            'role': 'Doorka / Shaqada (System Role) *',
            'is_active': 'Akoonku Wuu Shaqaynayaa (Active)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserAdminPasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label='Furaha Cusub (New Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ugu yaraan 6 xaraf'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        label='Xaqiiji Furaha Cusub (Confirm Password) *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dib u geli furaha cusub'}),
        min_length=6
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get('new_password')
        confirm_pass = cleaned_data.get('confirm_password')

        if new_pass and confirm_pass and new_pass != confirm_pass:
            raise forms.ValidationError("Labada fure isma leha! Fadlan dib u hubi.")
        return cleaned_data





