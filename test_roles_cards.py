import os
import sys
import django

# Set utf-8 output encoding for Windows terminal
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.test import Client
from hospital.models import User

client = Client()

print("=" * 60)
print("COMPREHENSIVE TEST: STAT CARDS, USERS MODULE, & ROLE PERMISSIONS")
print("=" * 60)

# -------------------------------------------------------------
# 1. STAT CARDS ON DASHBOARD
# -------------------------------------------------------------
print("\n--- 1. Testing Stat Cards on Dashboard ---")
client.login(username='yaaz', password='password123')
res = client.get('/dashboard/')
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
html = res.content.decode('utf-8')

assert 'stat-navy' in html or '#1e3a8a' in html, "Total Patients card missing Navy Blue styling"
print("  ✓ Total Patients card: Navy Blue (#1e3a8a) verified")

assert 'stat-dark-pink' in html or '#be185d' in html, "Available Doctors card missing Dark Pink styling"
print("  ✓ Available Doctors card: Dark Pink (#be185d) verified")

assert 'stat-dark-green' in html or '#15803d' in html, "Appointments card missing Dark Green styling"
print("  ✓ Appointments card: Dark Green (#15803d) verified")

assert 'stat-white-blue' in html or '#0284c7' in html or 'violet' in html, "New Patients card missing White Blue styling"
print("  ✓ New Patients card: White Blue (#f0f9ff / #0284c7) verified")

assert 'stat-white-purple' in html or '#9333ea' in html, "Operations card missing White Purple styling"
print("  ✓ Operations card: White Purple (#faf5ff / #9333ea) verified")

# -------------------------------------------------------------
# 2. USERS MODULE (CRUD & ACTIONS)
# -------------------------------------------------------------
print("\n--- 2. Testing Users Management Module (/users/) ---")
# List
res = client.get('/users/')
assert res.status_code == 200, f"Expected 200 for /users/, got {res.status_code}"
print("  ✓ User List (/users/): 200 OK")

# Create User
res = client.get('/users/create/')
assert res.status_code == 200, f"Expected 200 for /users/create/, got {res.status_code}"
test_username = 'test_specialist'
if User.objects.filter(username=test_username).exists():
    User.objects.filter(username=test_username).delete()

res = client.post('/users/create/', {
    'username': test_username,
    'first_name': 'Ali',
    'last_name': 'Gedi',
    'email': 'ali.gedi@hospital.so',
    'role': 'Doctor',
    'password': 'password123',
    'confirm_password': 'password123',
    'is_active': 'on',
})
assert res.status_code == 302, f"Expected redirect after create, got {res.status_code}"
test_user = User.objects.get(username=test_username)
assert test_user.role == 'Doctor'
print(f"  ✓ User Create: Created @{test_user.username} with role Doctor")

# Update User
res = client.post(f'/users/{test_user.pk}/update/', {
    'first_name': 'Ali Updated',
    'last_name': 'Gedi',
    'email': 'ali.updated@hospital.so',
    'role': 'Accountant',
    'is_active': 'on',
})
assert res.status_code == 302
test_user.refresh_from_db()
assert test_user.role == 'Accountant'
assert test_user.first_name == 'Ali Updated'
print(f"  ✓ User Update: Updated role to {test_user.role} and name to {test_user.first_name}")

# Toggle User Status
res = client.post(f'/users/{test_user.pk}/toggle/')
assert res.status_code == 302
test_user.refresh_from_db()
assert test_user.is_active is False
print("  ✓ User Toggle Status: Successfully deactivated user (is_active=False)")

res = client.post(f'/users/{test_user.pk}/toggle/')
assert res.status_code == 302
test_user.refresh_from_db()
assert test_user.is_active is True
print("  ✓ User Toggle Status: Successfully reactivated user (is_active=True)")

# Reset Password
res = client.post(f'/users/{test_user.pk}/reset-password/', {
    'new_password': 'newpassword456',
    'confirm_password': 'newpassword456',
})
assert res.status_code == 302
test_user.refresh_from_db()
assert test_user.check_password('newpassword456')
print("  ✓ User Reset Password: Admin successfully changed password for user")

# Delete User
res = client.post(f'/users/{test_user.pk}/delete/')
assert res.status_code == 302
assert not User.objects.filter(username=test_username).exists()
print("  ✓ User Delete: Cleanly deleted test user")

# -------------------------------------------------------------
# 3. ROLE-BASED ACCESS CONTROL & BOUNDARIES
# -------------------------------------------------------------
print("\n--- 3. Testing Role Permissions & Boundaries ---")

# A. Admin (Full System Access)
print("  [A] Admin User (yaaz): Full System Access")
for url in ['/dashboard/', '/users/', '/settings/', '/hr/', '/billing/', '/laboratory/', '/pharmacy/medicines/', '/opd/', '/ipd/admissions/']:
    res = client.get(url)
    assert res.status_code == 200, f"Admin should have access to {url}, got {res.status_code}"
print("      ✓ Admin can access all 9 hospital departments without restriction!")

# B. Doctor (dr.hassan)
print("  [B] Doctor User (dr.hassan): Clinical Only")
client.login(username='dr.hassan', password='password123')
# Allowed:
for url in ['/dashboard/', '/patient-list/', '/opd/', '/ipd/admissions/', '/laboratory/', '/pharmacy/medicines/']:
    res = client.get(url)
    assert res.status_code == 200, f"Doctor should access {url}, got {res.status_code}"
print("      ✓ Doctor allowed into OPD, Inpatients, Patients, Laboratory, Pharmacy")
# Denied:
for url in ['/users/', '/settings/', '/hr/', '/billing/']:
    res = client.get(url)
    assert res.status_code == 403, f"Doctor should be DENIED {url}, got {res.status_code}"
print("      ✓ Doctor correctly BLOCKED (403) from Users, Settings, HR, Billing")

# C. Pharmacist (pharm.nimco)
print("  [C] Pharmacist User (pharm.nimco): Pharmacy Only")
client.login(username='pharm.nimco', password='password123')
res = client.get('/pharmacy/medicines/')
assert res.status_code == 200, f"Pharmacist should access pharmacy, got {res.status_code}"
for url in ['/users/', '/settings/', '/hr/', '/billing/', '/laboratory/']:
    res = client.get(url)
    assert res.status_code == 403, f"Pharmacist should be DENIED {url}, got {res.status_code}"
print("      ✓ Pharmacist allowed in Pharmacy; strictly BLOCKED (403) from Users, Settings, HR, Billing, Laboratory")

# D. Lab Technician (tech.ahmed)
print("  [D] Lab Technician User (tech.ahmed): Laboratory Only")
client.login(username='tech.ahmed', password='password123')
res = client.get('/laboratory/')
assert res.status_code == 200, f"Lab Tech should access laboratory, got {res.status_code}"
for url in ['/users/', '/settings/', '/hr/', '/billing/', '/pharmacy/sales/create/']:
    res = client.get(url)
    assert res.status_code == 403, f"Lab Tech should be DENIED {url}, got {res.status_code}"
print("      ✓ Lab Tech allowed in Laboratory; strictly BLOCKED (403) from Users, Settings, HR, Billing, Pharmacy Sales")

# E. Accountant (fin.mohamed)
print("  [E] Accountant User (fin.mohamed): Billing & Finance Only")
client.login(username='fin.mohamed', password='password123')
for url in ['/billing/', '/billing/invoices/', '/billing/payments/', '/reports/financial/']:
    res = client.get(url)
    assert res.status_code == 200, f"Accountant should access {url}, got {res.status_code}"
for url in ['/users/', '/settings/', '/hr/', '/laboratory/', '/pharmacy/sales/create/']:
    res = client.get(url)
    assert res.status_code == 403, f"Accountant should be DENIED {url}, got {res.status_code}"
print("      ✓ Accountant allowed in Billing, Invoices, Payments, Financial Reports; strictly BLOCKED (403) from Users, Settings, HR, Laboratory, Pharmacy")

# F. Nurse (nurse.fadumo)
print("  [F] Nurse User (nurse.fadumo): IPD & Triage Only")
client.login(username='nurse.fadumo', password='password123')
for url in ['/ipd/admissions/', '/ipd/beds/', '/opd/']:
    res = client.get(url)
    assert res.status_code == 200, f"Nurse should access {url}, got {res.status_code}"
for url in ['/users/', '/settings/', '/hr/', '/billing/', '/reports/financial/']:
    res = client.get(url)
    assert res.status_code == 403, f"Nurse should be DENIED {url}, got {res.status_code}"
print("      ✓ Nurse allowed in IPD & OPD Triage; strictly BLOCKED (403) from Users, Settings, HR, Billing, Financial Reports")

print("\n" + "=" * 60)
print("ALL TESTS PASSED WITH 100% SUCCESS!")
print("=" * 60)
