import os
import sys
import django

sys.path.insert(0, os.path.abspath('hospital_management_system-master'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.utils import timezone
from hospital.models import (
    User, Doctor, Patient,
    LabCategory, LabTest, LabTestParameter,
    LabRequest, LabRequestItem, LabResult, LabResultItem
)

def run():
    print("Populating Laboratory Data...")

    # Ensure admin user
    user = User.objects.first()
    doctor = Doctor.objects.first()

    # Create more sample patients if only 1 exists
    p1 = Patient.objects.first()
    if not p1:
        p1 = Patient.objects.create(
            name="Maxamed Cali Faarax", age=34, gender="Male",
            address="Hodhan, Muqdisho", phone="+252 61 5123456"
        )
    
    p2, _ = Patient.objects.get_or_create(
        name="Faadumo Axmed Warsame",
        defaults={
            'age': 28, 'gender': "Female",
            'address': "Waberi, Muqdisho", 'phone': "+252 61 7890123"
        }
    )
    p3, _ = Patient.objects.get_or_create(
        name="Cismaan Nuur Xasan",
        defaults={
            'age': 45, 'gender': "Male",
            'address': "Yaqshid, Muqdisho", 'phone': "+252 61 8887766"
        }
    )
    p4, _ = Patient.objects.get_or_create(
        name="Deeqa Jaamac Cilmi",
        defaults={
            'age': 19, 'gender': "Female",
            'address': "Hamar Weyne, Muqdisho", 'phone': "+252 61 2233445"
        }
    )

    # 1. Categories
    categories_data = [
        ("Hematology (Dhiigga)", "Baaritaannada dhiigga guud, unugyada iyo dhiig-yarida", "bloodtype"),
        ("Clinical Biochemistry (Kiimikada)", "Sonkorta, subagga dhiigga, shaqada beerka iyo kelyaha", "science"),
        ("Parasitology & Infections (Dulinka & Cudurada)", "Baaritaannada Kaneecada, Tiifowga, iyo dulin-ku-nooleyaasha", "coronavirus"),
        ("Urinalysis (Kaadida)", "Baaritaanka guud iyo mikroskoobka ee kaadida", "water_drop"),
        ("Serology & Immunology (Fayrasyada)", "Baaritaannada cagaarshowga B/C, HIV iyo difaaca jirka", "biotech"),
    ]

    cats = {}
    for name, desc, icon in categories_data:
        cat, _ = LabCategory.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'icon': icon}
        )
        cats[name] = cat

    # 2. Tests & Parameters
    tests_data = [
        # Hematology
        (
            cats["Hematology (Dhiigga)"],
            "Complete Blood Count (CBC)", "CBC-001", "Whole Blood (EDTA)", 15.00, "1-2 hours",
            "Baaritaan buuxa oo lagu ogaanayo dhiig-yaro, caabuqa iyo unugyada dhiigga",
            [
                ("Hemoglobin (Hb)", "g/dL", "13.0 - 17.5"),
                ("RBC Count", "x10^6/µL", "4.5 - 5.9"),
                ("Total WBC Count", "/µL", "4,000 - 11,000"),
                ("Platelet Count", "/µL", "150,000 - 450,000"),
                ("Hematocrit (PCV)", "%", "40 - 52"),
                ("MCV", "fL", "80 - 100"),
                ("MCH", "pg", "27 - 33"),
            ]
        ),
        (
            cats["Hematology (Dhiigga)"],
            "Blood Grouping & Rh Factor", "BG-002", "Whole Blood", 5.00, "20 mins",
            "Ogaanshaha nooca dhiigga (A, B, AB, O) iyo Rh factor",
            [
                ("ABO Blood Group", "", "A / B / AB / O"),
                ("Rh (D) Factor", "", "Positive / Negative"),
            ]
        ),
        (
            cats["Hematology (Dhiigga)"],
            "ESR (Erythrocyte Sedimentation Rate)", "ESR-003", "Whole Blood (Citrate)", 6.00, "1 hour",
            "Calaamadda caabuqa daba-dheeraaday ama xanuunnada lafaha",
            [
                ("ESR 1st Hour", "mm/hr", "0 - 15"),
            ]
        ),

        # Biochemistry
        (
            cats["Clinical Biochemistry (Kiimikada)"],
            "Fasting Blood Sugar (FBS)", "FBS-101", "Serum / Plasma", 5.00, "30 mins",
            "Cabbiraadda heerka sonkorta dhiigga marka bukaanku sooman yahay",
            [
                ("Fasting Blood Glucose", "mg/dL", "70 - 100"),
            ]
        ),
        (
            cats["Clinical Biochemistry (Kiimikada)"],
            "HbA1c (Glycated Hemoglobin)", "HBA1C-102", "Whole Blood", 20.00, "2 hours",
            "Celceliska sonkorta dhiigga ee 3-dii bilood ee ugu dambeeyey",
            [
                ("HbA1c Level", "%", "4.0 - 5.6"),
            ]
        ),
        (
            cats["Clinical Biochemistry (Kiimikada)"],
            "Lipid Profile (Subagga Dhiigga)", "LIPID-103", "Serum", 25.00, "2 hours",
            "Cabbiraadda cholesterol, triglycerides iyo subagga caafimaadka u roon",
            [
                ("Total Cholesterol", "mg/dL", "< 200"),
                ("Triglycerides", "mg/dL", "< 150"),
                ("HDL Cholesterol", "mg/dL", "> 40"),
                ("LDL Cholesterol", "mg/dL", "< 100"),
            ]
        ),
        (
            cats["Clinical Biochemistry (Kiimikada)"],
            "Liver Function Test (LFT)", "LFT-104", "Serum", 30.00, "3 hours",
            "Baaritaanka fayo-qabka iyo shaqada beerka",
            [
                ("Total Bilirubin", "mg/dL", "0.2 - 1.2"),
                ("Direct Bilirubin", "mg/dL", "0.0 - 0.3"),
                ("ALT (SGPT)", "U/L", "7 - 56"),
                ("AST (SGOT)", "U/L", "10 - 40"),
                ("Alkaline Phosphatase (ALP)", "U/L", "44 - 147"),
                ("Total Protein", "g/dL", "6.0 - 8.3"),
                ("Serum Albumin", "g/dL", "3.5 - 5.0"),
            ]
        ),
        (
            cats["Clinical Biochemistry (Kiimikada)"],
            "Kidney Function Test (KFT)", "KFT-105", "Serum", 25.00, "2 hours",
            "Baaritaanka shaqada kelyaha, creatinine iyo urea",
            [
                ("Serum Creatinine", "mg/dL", "0.6 - 1.2"),
                ("Blood Urea", "mg/dL", "15 - 45"),
                ("Uric Acid", "mg/dL", "3.5 - 7.2"),
                ("Sodium (Na+)", "mmol/L", "135 - 145"),
                ("Potassium (K+)", "mmol/L", "3.5 - 5.0"),
            ]
        ),

        # Parasitology
        (
            cats["Parasitology & Infections (Dulinka & Cudurada)"],
            "Malaria Rapid Diagnostic Test (RDT)", "MAL-201", "Whole Blood", 5.00, "20 mins",
            "Baaritaanka degdegga ah ee jeermiska kaneecada",
            [
                ("Malaria Antigen (P. falciparum)", "", "Negative"),
                ("Malaria Antigen (Pan / P. vivax)", "", "Negative"),
            ]
        ),
        (
            cats["Parasitology & Infections (Dulinka & Cudurada)"],
            "Widal Test (Tiifowga)", "WIDAL-202", "Serum", 8.00, "30 mins",
            "Baaritaanka unugyada difaaca ee xumadda tiifowga (Salmonella)",
            [
                ("Salmonella Typhi 'O' Titre", "", "< 1:80"),
                ("Salmonella Typhi 'H' Titre", "", "< 1:80"),
            ]
        ),
        (
            cats["Parasitology & Infections (Dulinka & Cudurada)"],
            "Stool Routine & Microscopy", "STL-203", "Fresh Stool", 8.00, "45 mins",
            "Baaritaanka saxarada, dulin-ku-noolayaasha iyo dheefshiidka",
            [
                ("Consistency", "", "Formed / Soft"),
                ("Color", "", "Brownish"),
                ("Ova & Parasites", "", "Not Detected"),
                ("Pus Cells", "/HPF", "0 - 2"),
                ("RBCs", "/HPF", "Nil"),
            ]
        ),
        (
            cats["Parasitology & Infections (Dulinka & Cudurada)"],
            "H. Pylori Antigen Test", "HP-204", "Stool / Blood", 10.00, "20 mins",
            "Baaritaanka bakteeriyada caloosha boogta ku yeelata (Gaastari)",
            [
                ("H. Pylori Antigen", "", "Negative"),
            ]
        ),

        # Urinalysis
        (
            cats["Urinalysis (Kaadida)"],
            "Urine Routine & Microscopy", "URN-301", "Midstream Urine", 6.00, "30 mins",
            "Baaritaanka guud ee kaadida, caabuqa kaadi mareenka iyo kelyaha",
            [
                ("Color", "", "Pale Yellow"),
                ("Appearance", "", "Clear"),
                ("Specific Gravity", "", "1.005 - 1.030"),
                ("pH", "", "5.0 - 7.5"),
                ("Protein / Albumin", "", "Negative"),
                ("Glucose", "", "Negative"),
                ("Ketones", "", "Negative"),
                ("Pus Cells (WBC)", "/HPF", "0 - 5"),
                ("Red Blood Cells", "/HPF", "0 - 2"),
            ]
        ),

        # Serology
        (
            cats["Serology & Immunology (Fayrasyada)"],
            "Hepatitis B Surface Antigen (HBsAg)", "HBS-401", "Serum", 10.00, "30 mins",
            "Baaritaanka caabuqa beerka ee Hepatitis B",
            [
                ("HBsAg Screening", "", "Negative / Non-reactive"),
            ]
        ),
        (
            cats["Serology & Immunology (Fayrasyada)"],
            "Hepatitis C Antibody (Anti-HCV)", "HCV-402", "Serum", 10.00, "30 mins",
            "Baaritaanka caabuqa beerka ee Hepatitis C",
            [
                ("Anti-HCV Antibody", "", "Negative / Non-reactive"),
            ]
        ),
        (
            cats["Serology & Immunology (Fayrasyada)"],
            "HIV I & II Antibody Rapid Screen", "HIV-403", "Serum / Whole Blood", 10.00, "20 mins",
            "Baaritaanka degdegga ah ee fayraska HIV",
            [
                ("HIV I & II Antibodies", "", "Negative / Non-reactive"),
            ]
        ),
    ]

    saved_tests = {}
    for cat, name, code, sample, price, tat, desc, params in tests_data:
        test, created = LabTest.objects.get_or_create(
            code=code,
            defaults={
                'category': cat,
                'name': name,
                'sample_type': sample,
                'price': price,
                'turnaround_time': tat,
                'description': desc,
                'is_active': True
            }
        )
        saved_tests[code] = test

        # Parameters
        for idx, (pname, unit, ref) in enumerate(params):
            LabTestParameter.objects.get_or_create(
                test=test,
                name=pname,
                defaults={
                    'unit': unit,
                    'reference_range': ref,
                    'order': idx + 1
                }
            )

    print(f"Created {len(saved_tests)} lab tests with parameters.")

    # 3. Create Sample Lab Requests if none exist
    if LabRequest.objects.count() == 0:
        # Sample 1: Completed CBC & Malaria for Patient 1
        cbc_test = saved_tests["CBC-001"]
        mal_test = saved_tests["MAL-201"]
        
        req1 = LabRequest.objects.create(
            patient=p1,
            doctor=doctor,
            technician=user,
            priority='Routine',
            status='Completed',
            payment_status='Paid',
            total_amount=cbc_test.price + mal_test.price,
            clinical_notes="Bukaanku wuxuu ka cabanayaa qandho, madax xanuun iyo tabardari guud.",
            sample_collected_at=timezone.now() - timezone.timedelta(hours=3),
            completed_at=timezone.now() - timezone.timedelta(hours=1),
        )
        LabRequestItem.objects.create(request=req1, test=cbc_test, price=cbc_test.price, status='Completed')
        LabRequestItem.objects.create(request=req1, test=mal_test, price=mal_test.price, status='Completed')

        # Results for CBC
        res_cbc = LabResult.objects.create(
            request=req1, test=cbc_test, technician=user,
            overall_interpretation="Mild microcytic anemia detected. Clinical correlation advised.",
            is_abnormal=True
        )
        cbc_values = [
            ("Hemoglobin (Hb)", "11.2", "g/dL", "13.0 - 17.5", "Low"),
            ("RBC Count", "4.1", "x10^6/µL", "4.5 - 5.9", "Low"),
            ("Total WBC Count", "8,200", "/µL", "4,000 - 11,000", "Normal"),
            ("Platelet Count", "260,000", "/µL", "150,000 - 450,000", "Normal"),
            ("Hematocrit (PCV)", "36", "%", "40 - 52", "Low"),
            ("MCV", "74", "fL", "80 - 100", "Low"),
            ("MCH", "24", "pg", "27 - 33", "Low"),
        ]
        for pname, rval, unit, ref, flag in cbc_values:
            LabResultItem.objects.create(
                result=res_cbc, parameter_name=pname, result_value=rval, unit=unit, reference_range=ref, flag=flag
            )

        # Results for Malaria
        res_mal = LabResult.objects.create(
            request=req1, test=mal_test, technician=user,
            overall_interpretation="Negative for Malaria Parasites by rapid immunochromatographic assay.",
            is_abnormal=False
        )
        LabResultItem.objects.create(
            result=res_mal, parameter_name="Malaria Antigen (P. falciparum)", result_value="Negative", unit="", reference_range="Negative", flag="Negative"
        )
        LabResultItem.objects.create(
            result=res_mal, parameter_name="Malaria Antigen (Pan / P. vivax)", result_value="Negative", unit="", reference_range="Negative", flag="Negative"
        )

        # Sample 2: In Progress - Fasting Blood Sugar & Lipid Profile for Patient 2
        fbs_test = saved_tests["FBS-101"]
        lipid_test = saved_tests["LIPID-103"]
        req2 = LabRequest.objects.create(
            patient=p2,
            doctor=doctor,
            priority='Routine',
            status='In Progress',
            payment_status='Paid',
            total_amount=fbs_test.price + lipid_test.price,
            clinical_notes="Dabagal joogto ah oo ku saabsan sonkorta iyo xakamaynta subagga.",
            sample_collected_at=timezone.now() - timezone.timedelta(minutes=45),
        )
        LabRequestItem.objects.create(request=req2, test=fbs_test, price=fbs_test.price, status='In Progress')
        LabRequestItem.objects.create(request=req2, test=lipid_test, price=lipid_test.price, status='In Progress')

        # Sample 3: STAT / Urgent - Widal & Malaria for Patient 3
        widal_test = saved_tests["WIDAL-202"]
        req3 = LabRequest.objects.create(
            patient=p3,
            doctor=doctor,
            priority='STAT',
            status='Sample Collected',
            payment_status='Unpaid',
            total_amount=widal_test.price + mal_test.price,
            clinical_notes="Xumad daran oo 4 maalmood jirtay (High grade pyrexia). Degdeg u baadh!",
            sample_collected_at=timezone.now() - timezone.timedelta(minutes=20),
        )
        LabRequestItem.objects.create(request=req3, test=widal_test, price=widal_test.price, status='Sample Collected')
        LabRequestItem.objects.create(request=req3, test=mal_test, price=mal_test.price, status='Sample Collected')

        # Sample 4: Pending - Urine Analysis for Patient 4
        urn_test = saved_tests["URN-301"]
        req4 = LabRequest.objects.create(
            patient=p4,
            doctor=doctor,
            priority='Routine',
            status='Pending',
            payment_status='Unpaid',
            total_amount=urn_test.price,
            clinical_notes="Xanuun xagga hoose ah marka uu kaadinayo (Dysuria suspicion).",
        )
        LabRequestItem.objects.create(request=req4, test=urn_test, price=urn_test.price, status='Pending')

        print("Created 4 sample lab orders with realistic medical results!")

if __name__ == '__main__':
    run()
