import os
import sys
import django

sys.path.insert(0, os.path.abspath('hospital_management_system-master'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.utils import timezone
from hospital.models import (
    User, Doctor, Patient, Medicine,
    OPDVisit, OPDVitalSign, OPDConsultation, OPDPrescriptionItem
)

def run():
    print("Populating OPD Data...")

    doctor = Doctor.objects.first()
    nurse = User.objects.filter(role__in=['Nurse', 'Admin']).first() or User.objects.first()
    patients = list(Patient.objects.all())

    if len(patients) < 4:
        p_extra = [
            ("Xamdi Cabdullaahi Jaamac", 24, "Female", "Hodan, Muqdisho", "+252 61 7776655"),
            ("Cabdiraxmaan Shariif Cumar", 52, "Male", "Boondheere, Muqdisho", "+252 61 4443322"),
        ]
        for name, age, gender, address, phone in p_extra:
            p, _ = Patient.objects.get_or_create(
                name=name,
                defaults={'age': age, 'gender': gender, 'address': address, 'phone': phone}
            )
            patients.append(p)

    # 1. Visit 1: Completed with Vitals, Consultation and Prescriptions
    p1 = patients[0]
    v1, _ = OPDVisit.objects.get_or_create(
        patient=p1,
        visit_number="OPD-2024-0001",
        defaults={
            'token_number': 1,
            'doctor': doctor,
            'department': 'General OPD',
            'visit_type': 'New Visit',
            'status': 'Completed',
            'consultation_fee': 10.00,
            'payment_status': 'Paid',
            'triage_nurse': nurse,
            'visit_date': timezone.now() - timezone.timedelta(hours=2),
        }
    )
    # Vitals for Visit 1
    OPDVitalSign.objects.get_or_create(
        visit=v1,
        defaults={
            'blood_pressure': '125/82',
            'temperature': 37.2,
            'pulse_rate': 76,
            'respiratory_rate': 18,
            'oxygen_saturation': 98,
            'weight': 70.0,
            'height': 172.0,
            'bmi': 23.7,
            'blood_sugar': '105 mg/dL',
            'triage_notes': 'Bukaanka dhiigkarkiisu waa caadi. Wax xumad daran ah ma lahan.',
            'recorded_by': nurse,
        }
    )
    # Consultation for Visit 1
    c1, _ = OPDConsultation.objects.get_or_create(
        visit=v1,
        defaults={
            'doctor': doctor or Doctor.objects.first(),
            'chief_complaint': 'Qufac qalalan, hunguri xanuun iyo cunto qaadasho la\'aan socotay 3 maalmood.',
            'history_of_illness': 'Xanuunku wuxuu bilowday 3 maalmood ka hor, wax xabad xanuun daran ah ma jiro.',
            'physical_examination': 'Pharynx congested, tonsils mildly enlarged, chest clear bilaterally on auscultation.',
            'diagnosis': 'Acute Pharyngitis / Upper Respiratory Tract Infection (URTI)',
            'clinical_notes': 'Bukaanka waxaa la siiyey talooyin ah inuu cabo biyo badan oo qandhac ah, nasasho qaato.',
            'outcome': 'Discharged',
            'next_follow_up': timezone.now().date() + timezone.timedelta(days=7),
        }
    )
    # Prescriptions
    if c1.prescriptions.count() == 0:
        OPDPrescriptionItem.objects.create(
            consultation=c1,
            medicine_name="Amoxicillin 500mg",
            dosage="1 Capsule",
            frequency="1x3 (3 jeer maalintii)",
            duration="5 maalmood",
            instructions="Cuntada kadib qaado"
        )
        OPDPrescriptionItem.objects.create(
            consultation=c1,
            medicine_name="Paracetamol 500mg",
            dosage="2 Tablets",
            frequency="1x3 (markii xanuun jiro)",
            duration="3 maalmood",
            instructions="Markii qandho ama madax xanuun jiro"
        )
        OPDPrescriptionItem.objects.create(
            consultation=c1,
            medicine_name="Vitamin C 1000mg",
            dosage="1 Effervescent Tab",
            frequency="1x1 (maalintiiba mar)",
            duration="7 maalmood",
            instructions="Biya ku dhex mil"
        )

    # 2. Visit 2: Triage Done (Ready for Doctor)
    p2 = patients[1]
    v2, _ = OPDVisit.objects.get_or_create(
        patient=p2,
        visit_number="OPD-2024-0002",
        defaults={
            'token_number': 2,
            'doctor': doctor,
            'department': 'Internal Medicine',
            'visit_type': 'Follow-up',
            'status': 'Triage Done',
            'consultation_fee': 10.00,
            'payment_status': 'Paid',
            'triage_nurse': nurse,
            'visit_date': timezone.now() - timezone.timedelta(minutes=45),
        }
    )
    OPDVitalSign.objects.get_or_create(
        visit=v2,
        defaults={
            'blood_pressure': '138/88',
            'temperature': 36.8,
            'pulse_rate': 82,
            'respiratory_rate': 16,
            'oxygen_saturation': 97,
            'weight': 82.5,
            'height': 168.0,
            'bmi': 29.2,
            'blood_sugar': '142 mg/dL',
            'triage_notes': 'Bukaanku wuxuu u yimid dabagalka sonkorta iyo dhiigkarka. Vitals-ka waa la qabtay.',
            'recorded_by': nurse,
        }
    )

    # 3. Visit 3: Waiting Queue (Just registered)
    p3 = patients[2]
    v3, _ = OPDVisit.objects.get_or_create(
        patient=p3,
        visit_number="OPD-2024-0003",
        defaults={
            'token_number': 3,
            'doctor': doctor,
            'department': 'General OPD',
            'visit_type': 'New Visit',
            'status': 'Waiting',
            'consultation_fee': 10.00,
            'payment_status': 'Paid',
            'visit_date': timezone.now() - timezone.timedelta(minutes=15),
        }
    )

    # 4. Visit 4: Waiting Queue (Emergency / STAT)
    if len(patients) > 3:
        p4 = patients[3]
        v4, _ = OPDVisit.objects.get_or_create(
            patient=p4,
            visit_number="OPD-2024-0004",
            defaults={
                'token_number': 4,
                'doctor': doctor,
                'department': 'Pediatrics',
                'visit_type': 'Emergency',
                'status': 'Waiting',
                'consultation_fee': 15.00,
                'payment_status': 'Unpaid',
                'visit_date': timezone.now() - timezone.timedelta(minutes=5),
            }
        )

    print("OPD sample data populated successfully!")

if __name__ == '__main__':
    run()
