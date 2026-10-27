import os
import sys
import django
import datetime

sys.path.insert(0, os.path.abspath('hospital_management_system-master'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.utils import timezone
from hospital.models import User, Staff, StaffAttendance, StaffLeave, StaffPayroll

def run():
    print("Populating HR & Staff Management Data...")

    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()

    staff_data = [
        {
            'username': 'dr.hassan',
            'first_name': 'Hassan',
            'last_name': 'Nur Cali',
            'department': 'Medical / OPD',
            'designation': 'Senior Consultant Physician',
            'gender': 'Male',
            'phone': '+252 61 511 2233',
            'email': 'hassan.nur@medicare.so',
            'qualification': 'MBBS, MD Internal Medicine',
            'experience_years': 12,
            'shift': 'Morning',
            'status': 'Active',
            'salary': 2500.00,
            'hire_date': datetime.date(2022, 3, 1),
            'emergency_contact': 'Faadumo Cali (Xaaska) - 0615223344',
            'address': 'Hodan, Mogadishu',
        },
        {
            'username': 'nurse.fadumo',
            'first_name': 'Fadumo',
            'last_name': 'Axmed Nuur',
            'department': 'Nursing',
            'designation': 'Head Nurse & Triage In-Charge',
            'gender': 'Female',
            'phone': '+252 61 544 5566',
            'email': 'fadumo.ahmed@medicare.so',
            'qualification': 'BSc Nursing, Critical Care Cert',
            'experience_years': 8,
            'shift': 'Morning',
            'status': 'Active',
            'salary': 850.00,
            'hire_date': datetime.date(2023, 1, 15),
            'emergency_contact': 'Axmed Nuur (Aabe) - 0615556677',
            'address': 'Waberi, Mogadishu',
        },
        {
            'username': 'tech.ahmed',
            'first_name': 'Ahmed',
            'last_name': 'Warsame Shire',
            'department': 'Laboratory',
            'designation': 'Senior Medical Lab Technologist',
            'gender': 'Male',
            'phone': '+252 61 577 8899',
            'email': 'ahmed.warsame@medicare.so',
            'qualification': 'BSc Medical Laboratory Technology',
            'experience_years': 6,
            'shift': 'Morning',
            'status': 'Active',
            'salary': 950.00,
            'hire_date': datetime.date(2023, 6, 1),
            'emergency_contact': 'Cabdi Warsame (Walaal) - 0615889900',
            'address': 'Howlwadaag, Mogadishu',
        },
        {
            'username': 'pharm.nimco',
            'first_name': 'Nimco',
            'last_name': 'Cabdi Jaamac',
            'department': 'Pharmacy',
            'designation': 'Chief Pharmacist',
            'gender': 'Female',
            'phone': '+252 61 599 0011',
            'email': 'nimco.abdi@medicare.so',
            'qualification': 'B.Pharm, Clinical Pharmacology',
            'experience_years': 7,
            'shift': 'Evening',
            'status': 'Active',
            'salary': 1100.00,
            'hire_date': datetime.date(2022, 8, 10),
            'emergency_contact': 'Cabdi Jaamac (Aabe) - 0615001122',
            'address': 'Yaqshid, Mogadishu',
        },
        {
            'username': 'fin.mohamed',
            'first_name': 'Mohamed',
            'last_name': 'Shire Geedi',
            'department': 'Finance & Billing',
            'designation': 'Senior Cashier & Billing Officer',
            'gender': 'Male',
            'phone': '+252 61 522 3344',
            'email': 'mohamed.shire@medicare.so',
            'qualification': 'BBA Accounting & Finance',
            'experience_years': 5,
            'shift': 'Morning',
            'status': 'Active',
            'salary': 750.00,
            'hire_date': datetime.date(2024, 2, 1),
            'emergency_contact': 'Geedi Shire (Aabe) - 0615334455',
            'address': 'Hodan, Mogadishu',
        },
        {
            'username': 'hr.sahra',
            'first_name': 'Sahra',
            'last_name': 'Cusmaan Warsame',
            'department': 'Human Resources',
            'designation': 'HR Specialist & Personnel Officer',
            'gender': 'Female',
            'phone': '+252 61 566 7788',
            'email': 'sahra.osman@medicare.so',
            'qualification': 'BA Human Resource Management',
            'experience_years': 4,
            'shift': 'Full Time',
            'status': 'Active',
            'salary': 800.00,
            'hire_date': datetime.date(2024, 1, 10),
            'emergency_contact': 'Cusmaan Warsame - 0615778899',
            'address': 'Kaxda, Mogadishu',
        },
        {
            'username': 'sec.jaamac',
            'first_name': 'Jaamac',
            'last_name': 'Mire Maxamed',
            'department': 'Security & Logistics',
            'designation': 'Head of Hospital Security',
            'gender': 'Male',
            'phone': '+252 61 533 1122',
            'email': 'jaamac.mire@medicare.so',
            'qualification': 'Security & Safety Operations',
            'experience_years': 9,
            'shift': 'Night',
            'status': 'Active',
            'salary': 500.00,
            'hire_date': datetime.date(2023, 4, 1),
            'emergency_contact': 'Mire Maxamed - 0615442233',
            'address': 'Dharkenley, Mogadishu',
        },
        {
            'username': 'clean.deeqo',
            'first_name': 'Deeqo',
            'last_name': 'Yuusuf Maxamuud',
            'department': 'Cleaning & Maintenance',
            'designation': 'Hygiene & Infection Control Lead',
            'gender': 'Female',
            'phone': '+252 61 588 3344',
            'email': 'deeqo.yusuf@medicare.so',
            'qualification': 'Hospital Hygiene & Sanitation',
            'experience_years': 4,
            'shift': 'Morning',
            'status': 'On Leave',
            'salary': 420.00,
            'hire_date': datetime.date(2023, 9, 15),
            'emergency_contact': 'Yuusuf Maxamuud - 0615994455',
            'address': 'Hodan, Mogadishu',
        }
    ]

    staff_objs = []
    for idx, data in enumerate(staff_data, start=1):
        u, _ = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email']
            }
        )
        u.set_password('Staff@2026')
        u.first_name = data['first_name']
        u.last_name = data['last_name']
        u.email = data['email']
        u.save()

        emp_id = f"EMP-2024-{idx:04d}"
        s, created = Staff.objects.update_or_create(
            user=u,
            defaults={
                'employee_id': emp_id,
                'department': data['department'],
                'designation': data['designation'],
                'gender': data['gender'],
                'phone': data['phone'],
                'email': data['email'],
                'qualification': data['qualification'],
                'experience_years': data['experience_years'],
                'shift': data['shift'],
                'status': data['status'],
                'salary': data['salary'],
                'hire_date': data['hire_date'],
                'emergency_contact': data['emergency_contact'],
                'address': data['address'],
                'notes': f"Diiwaanka rasmiga ah ee {data['first_name']} {data['last_name']}."
            }
        )
        staff_objs.append(s)

    print(f"Created/Updated {len(staff_objs)} staff members.")

    # 2. Seed Attendances for Today & Yesterday
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)

    attendance_plan_today = [
        ('Present', datetime.time(7, 45), datetime.time(15, 30), 'Waqtigiisa ayuu ku yimid'),
        ('Present', datetime.time(7, 50), datetime.time(15, 10), 'Jooga'),
        ('Late', datetime.time(8, 25), datetime.time(15, 45), 'Gaadiidka ayaa ka xumaaday'),
        ('Present', datetime.time(14, 50), None, 'Shift galab - jooga'),
        ('Present', datetime.time(7, 55), datetime.time(16, 0), 'Jooga'),
        ('Present', datetime.time(8, 0), datetime.time(16, 30), 'Jooga'),
        ('Present', datetime.time(22, 55), None, 'Shift habeen - diyaar ah'),
        ('On Leave', None, None, 'Fasax xanuun ku maqan'),
    ]

    for s, plan in zip(staff_objs, attendance_plan_today):
        st, cin, cout, note = plan
        StaffAttendance.objects.update_or_create(
            staff=s,
            date=today,
            defaults={
                'status': st,
                'check_in': cin,
                'check_out': cout,
                'notes': note,
                'recorded_by': admin_user
            }
        )

        # Yesterday attendance
        StaffAttendance.objects.update_or_create(
            staff=s,
            date=yesterday,
            defaults={
                'status': 'Present' if st != 'On Leave' else 'On Leave',
                'check_in': datetime.time(8, 0) if st != 'On Leave' else None,
                'check_out': datetime.time(16, 0) if st != 'On Leave' else None,
                'notes': 'Shaqada si caadi ah ayuu u gutay',
                'recorded_by': admin_user
            }
        )

    print("Created attendance records for today and yesterday.")

    # 3. Seed Leaves
    # Pending leave for Dr. Hassan
    StaffLeave.objects.get_or_create(
        staff=staff_objs[0],
        start_date=today + datetime.timedelta(days=7),
        end_date=today + datetime.timedelta(days=14),
        defaults={
            'leave_type': 'Annual',
            'reason': 'Fasaxa sanadlaha ah ee qoyska iyo safar gudaha ah.',
            'status': 'Pending',
        }
    )

    # Approved leave for Deeqo Yusuf
    StaffLeave.objects.get_or_create(
        staff=staff_objs[7],
        start_date=today - datetime.timedelta(days=2),
        end_date=today + datetime.timedelta(days=3),
        defaults={
            'leave_type': 'Sick',
            'reason': 'Qandho iyo daal daran, warqad dhakhtar ayaa la socota.',
            'status': 'Approved',
            'approved_by': admin_user,
            'admin_remarks': 'La oggolaaday 5 maalmood oo fasax xanuun ah.'
        }
    )

    # Another pending leave for Ahmed Warsame
    StaffLeave.objects.get_or_create(
        staff=staff_objs[2],
        start_date=today + datetime.timedelta(days=3),
        end_date=today + datetime.timedelta(days=5),
        defaults={
            'leave_type': 'Emergency',
            'reason': 'Arin qoys oo degdeg ah oo gobolka ka timid.',
            'status': 'Pending',
        }
    )

    print("Created sample leave requests (Pending and Approved).")

    # 4. Seed Payroll Records (for October 2026)
    month_name = today.strftime("%B %Y")
    for idx, s in enumerate(staff_objs[:5], start=1):
        allowance = 50.00 if idx % 2 == 0 else 0.00
        deduction = 20.00 if idx == 3 else 0.00
        net = float(s.salary) + allowance - deduction

        StaffPayroll.objects.update_or_create(
            payroll_number=f"PAY-2026-{idx:05d}",
            defaults={
                'staff': s,
                'salary_month': month_name,
                'basic_salary': s.salary,
                'allowances': allowance,
                'deductions': deduction,
                'net_salary': net,
                'payment_method': 'Bank Transfer' if idx <= 2 else 'EVC Plus / Mobile Money',
                'payment_date': today - datetime.timedelta(days=idx),
                'status': 'Paid',
                'reference_number': f"TXID-BOK-{987600 + idx}",
                'notes': f"Mushaharka bisha {month_name} ee {s.user.get_full_name()}.",
                'created_by': admin_user
            }
        )

    print("Created payroll records.")
    print("HR & Staff Data seeding completed successfully!")

if __name__ == '__main__':
    run()
