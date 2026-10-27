import os
import sys
import django

sys.path.insert(0, os.path.abspath('hospital_management_system-master'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.utils import timezone
from hospital.models import (
    User, Doctor, Patient,
    Invoice, InvoiceItem, PaymentTransaction
)

def run():
    print("Populating Billing Data...")

    user = User.objects.first()
    doctor = Doctor.objects.first()
    patients = list(Patient.objects.all())

    if len(patients) < 4:
        print("Need patients to seed billing.")
        return

    # 1. Invoice 1: Paid ($45.00) - OPD + Lab CBC + Pharmacy
    p1 = patients[0]
    inv1, _ = Invoice.objects.get_or_create(
        invoice_number="INV-2024-0001",
        defaults={
            'patient': p1,
            'doctor': doctor,
            'billing_date': timezone.now() - timezone.timedelta(days=2),
            'status': 'Paid',
            'payment_method': 'EVC Plus / Mobile Money',
            'subtotal': 45.00,
            'discount': 0.00,
            'tax': 0.00,
            'total_amount': 45.00,
            'paid_amount': 45.00,
            'balance_due': 0.00,
            'notes': 'Adeegyadii bukaan-socodka ee maanta.',
            'created_by': user,
        }
    )
    if inv1.items.count() == 0:
        InvoiceItem.objects.create(invoice=inv1, service_type='Consultation', description='Doctor Consultation (General OPD)', quantity=1, unit_price=10.00, total_price=10.00)
        InvoiceItem.objects.create(invoice=inv1, service_type='Laboratory', description='Complete Blood Count (CBC)', quantity=1, unit_price=15.00, total_price=15.00)
        InvoiceItem.objects.create(invoice=inv1, service_type='Pharmacy', description='Amoxicillin 500mg & Paracetamol', quantity=1, unit_price=20.00, total_price=20.00)
    if inv1.payments.count() == 0:
        PaymentTransaction.objects.create(
            transaction_id="TRX-2024-00001",
            invoice=inv1,
            amount=45.00,
            payment_method='EVC Plus / Mobile Money',
            reference_number='EVC-998822331',
            payment_date=timezone.now() - timezone.timedelta(days=2),
            received_by=user,
            notes='Paid via EVC Plus to hospital merchant number'
        )

    # 2. Invoice 2: Partially Paid ($120.00 total, $70.00 paid, $50.00 balance due) - IPD Ward Bed & Nursing
    p2 = patients[1]
    inv2, _ = Invoice.objects.get_or_create(
        invoice_number="INV-2024-0002",
        defaults={
            'patient': p2,
            'doctor': doctor,
            'billing_date': timezone.now() - timezone.timedelta(days=1),
            'due_date': timezone.now().date() + timezone.timedelta(days=3),
            'status': 'Partially Paid',
            'payment_method': 'Cash',
            'subtotal': 125.00,
            'discount': 5.00,
            'tax': 0.00,
            'total_amount': 120.00,
            'paid_amount': 70.00,
            'balance_due': 50.00,
            'notes': 'Bukaan-jiif qolka General Ward 2 habeen.',
            'created_by': user,
        }
    )
    if inv2.items.count() == 0:
        InvoiceItem.objects.create(invoice=inv2, service_type='Inpatient / Bed', description='General Ward Bed Stay (2 Nights)', quantity=2, unit_price=25.00, total_price=50.00)
        InvoiceItem.objects.create(invoice=inv2, service_type='Nursing Care', description='Inpatient Daily Nursing & Vitals Care', quantity=2, unit_price=15.00, total_price=30.00)
        InvoiceItem.objects.create(invoice=inv2, service_type='Laboratory', description='Lipid Profile & Liver Function Panel', quantity=1, unit_price=45.00, total_price=45.00)
    if inv2.payments.count() == 0:
        PaymentTransaction.objects.create(
            transaction_id="TRX-2024-00002",
            invoice=inv2,
            amount=70.00,
            payment_method='Cash',
            reference_number='CASH-RCPT-042',
            payment_date=timezone.now() - timezone.timedelta(days=1),
            received_by=user,
            notes='Part payment in Cash at reception'
        )

    # 3. Invoice 3: Unpaid ($38.00) - Emergency OPD & Lab Panel
    p3 = patients[2]
    inv3, _ = Invoice.objects.get_or_create(
        invoice_number="INV-2024-0003",
        defaults={
            'patient': p3,
            'doctor': doctor,
            'billing_date': timezone.now() - timezone.timedelta(hours=4),
            'due_date': timezone.now().date() + timezone.timedelta(days=1),
            'status': 'Unpaid',
            'payment_method': 'Cash',
            'subtotal': 38.00,
            'discount': 0.00,
            'tax': 0.00,
            'total_amount': 38.00,
            'paid_amount': 0.00,
            'balance_due': 38.00,
            'notes': 'Baaritaanno degdeg ah oo sugaya lacag-bixinta.',
            'created_by': user,
        }
    )
    if inv3.items.count() == 0:
        InvoiceItem.objects.create(invoice=inv3, service_type='Consultation', description='Emergency Consultation & Assessment', quantity=1, unit_price=15.00, total_price=15.00)
        InvoiceItem.objects.create(invoice=inv3, service_type='Laboratory', description='Malaria RDT & Widal Typhoid Test', quantity=1, unit_price=13.00, total_price=13.00)
        InvoiceItem.objects.create(invoice=inv3, service_type='Pharmacy', description='Emergency IV Fluids & Cannula Set', quantity=1, unit_price=10.00, total_price=10.00)

    # 4. Invoice 4: Paid ($36.00) - Urinalysis & Ultrasound
    p4 = patients[3]
    inv4, _ = Invoice.objects.get_or_create(
        invoice_number="INV-2024-0004",
        defaults={
            'patient': p4,
            'doctor': doctor,
            'billing_date': timezone.now() - timezone.timedelta(hours=1),
            'status': 'Paid',
            'payment_method': 'Credit Card',
            'subtotal': 36.00,
            'discount': 0.00,
            'tax': 0.00,
            'total_amount': 36.00,
            'paid_amount': 36.00,
            'balance_due': 0.00,
            'notes': 'Adeegga Ultrasound iyo baaritaanka kaadida.',
            'created_by': user,
        }
    )
    if inv4.items.count() == 0:
        InvoiceItem.objects.create(invoice=inv4, service_type='Laboratory', description='Urine Routine & Microscopy', quantity=1, unit_price=6.00, total_price=6.00)
        InvoiceItem.objects.create(invoice=inv4, service_type='Radiology', description='Abdominal Ultrasound Sonography', quantity=1, unit_price=30.00, total_price=30.00)
    if inv4.payments.count() == 0:
        PaymentTransaction.objects.create(
            transaction_id="TRX-2024-00003",
            invoice=inv4,
            amount=36.00,
            payment_method='Credit Card',
            reference_number='AUTH-98310',
            payment_date=timezone.now() - timezone.timedelta(hours=1),
            received_by=user,
            notes='Paid via Visa Card terminal'
        )

    print("Billing sample data populated successfully!")

if __name__ == '__main__':
    run()
