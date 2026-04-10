"""
Setup SQLite Database for Clinic Management System
Creates schema and inserts realistic dummy data
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinic.db"

# Sample data generators
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Olivia",
    "James", "Sophia", "William", "Isabella", "Benjamin", "Mia", "Alexander",
    "Charlotte", "Daniel", "Amelia", "Matthew", "Harper", "Anthony", "Evelyn",
    "Mark", "Abigail", "Donald", "Ella", "Steven", "Scarlett", "Paul", "Victoria"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Miami", "Seattle", "Boston", "Denver", "Austin"]

DOCTOR_NAMES = [
    "Dr. Emily Watson", "Dr. James Mitchell", "Dr. Sarah Johnson",
    "Dr. Michael Chen", "Dr. Lisa Anderson", "Dr. Robert Smith",
    "Dr. Jennifer Brown", "Dr. William Davis", "Dr. Patricia Wilson",
    "Dr. Christopher Lee", "Dr. Maria Garcia", "Dr. David Martinez",
    "Dr. Jessica Taylor", "Dr. Daniel Rodriguez", "Dr. Nancy Martinez"
]

SPECIALIZATIONS = ["Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"]
DEPARTMENTS = ["Dermatology", "Cardiology", "Orthopedic", "General Practice", "Pediatric Care"]
APPOINTMENT_STATUS = ["Scheduled", "Completed", "Cancelled", "No-Show"]
INVOICE_STATUS = ["Paid", "Pending", "Overdue"]

TREATMENTS = [
    "Consultation", "Blood Test", "X-Ray", "ECG", "Skin Biopsy",
    "Vaccination", "Injection", "Ultrasound", "CT Scan", "Physical Therapy",
    "Surgery", "Wound Care", "Dental Cleaning", "Eye Exam", "Prescription",
    "Lab Work", "EEG", "Endoscopy", "Colonoscopy", "Bone Density Test"
]


def create_schema(conn):
    """Create all tables"""
    cursor = conn.cursor()
    
    # Patients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            date_of_birth DATE,
            gender TEXT,
            city TEXT,
            registered_date DATE NOT NULL
        )
    """)
    
    # Doctors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            department TEXT,
            phone TEXT
        )
    """)
    
    # Appointments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date DATETIME NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    
    # Treatments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            treatment_name TEXT NOT NULL,
            cost REAL NOT NULL,
            duration_minutes INTEGER,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        )
    """)
    
    # Invoices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            invoice_date DATE NOT NULL,
            total_amount REAL NOT NULL,
            paid_amount REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    
    conn.commit()
    print("✓ Schema created successfully")


def insert_doctors(conn):
    """Insert 15 doctors across 5 specializations"""
    cursor = conn.cursor()
    
    doctors = []
    for i, name in enumerate(DOCTOR_NAMES):
        spec_idx = i % len(SPECIALIZATIONS)
        specialization = SPECIALIZATIONS[spec_idx]
        department = DEPARTMENTS[spec_idx]
        phone = f"555-{1000 + i:04d}"
        
        doctors.append((name, specialization, department, phone))
    
    cursor.executemany("""
        INSERT INTO doctors (name, specialization, department, phone)
        VALUES (?, ?, ?, ?)
    """, doctors)
    
    conn.commit()
    print(f"✓ Created {len(doctors)} doctors")
    return len(doctors)


def insert_patients(conn):
    """Insert 200 patients with realistic distribution"""
    cursor = conn.cursor()
    
    patients = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(200):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}@email.com" if random.random() > 0.2 else None
        phone = f"555-{1000 + i:04d}" if random.random() > 0.3 else None
        
        # Birth date between 18 and 80 years ago
        birth_offset = random.randint(18 * 365, 80 * 365)
        date_of_birth = (datetime.now() - timedelta(days=birth_offset)).date()
        
        gender = random.choice(["M", "F"])
        city = random.choice(CITIES)
        
        # Registration spread across last 12 months
        reg_offset = random.randint(0, 365)
        registered_date = (base_date + timedelta(days=reg_offset)).date()
        
        patients.append((first_name, last_name, email, phone, date_of_birth, gender, city, registered_date))
    
    cursor.executemany("""
        INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, patients)
    
    conn.commit()
    print(f"✓ Created {len(patients)} patients")
    return len(patients)


def insert_appointments(conn):
    """Insert 500 appointments over past 12 months"""
    cursor = conn.cursor()
    
    # Get patient and doctor counts
    cursor.execute("SELECT COUNT(*) FROM patients")
    patient_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = cursor.fetchone()[0]
    
    appointments = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(500):
        patient_id = random.randint(1, patient_count)
        doctor_id = random.randint(1, doctor_count)
        
        # Spread appointments across 12 months
        days_offset = random.randint(0, 365)
        appointment_date = base_date + timedelta(days=days_offset, hours=random.randint(8, 16))
        
        status = random.choices(
            APPOINTMENT_STATUS,
            weights=[30, 50, 15, 5],  # More completed than cancelled
            k=1
        )[0]
        
        notes = random.choice([None, "Routine checkup", "Follow-up", "Emergency", "Scheduled surgery prep"])
        
        appointments.append((patient_id, doctor_id, appointment_date, status, notes))
    
    cursor.executemany("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
    """, appointments)
    
    conn.commit()
    print(f"✓ Created {len(appointments)} appointments")
    return len(appointments)


def insert_treatments(conn):
    """Insert 350 treatments linked to completed appointments"""
    cursor = conn.cursor()
    
    # Get completed appointments
    cursor.execute("SELECT id FROM appointments WHERE status = 'Completed'")
    completed_appts = [row[0] for row in cursor.fetchall()]
    
    # Pick random 350 (or less if fewer than 350 completed)
    treatment_appts = random.sample(completed_appts, min(350, len(completed_appts)))
    
    treatments = []
    for appt_id in treatment_appts:
        treatment_name = random.choice(TREATMENTS)
        cost = random.uniform(50, 5000)
        duration = random.randint(15, 240)
        
        treatments.append((appt_id, treatment_name, cost, duration))
    
    cursor.executemany("""
        INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
        VALUES (?, ?, ?, ?)
    """, treatments)
    
    conn.commit()
    print(f"✓ Created {len(treatments)} treatments")
    return len(treatments)


def insert_invoices(conn):
    """Insert 300 invoices with mixed statuses"""
    cursor = conn.cursor()
    
    # Get all patients
    cursor.execute("SELECT id FROM patients")
    patient_ids = [row[0] for row in cursor.fetchall()]
    
    invoices = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(300):
        patient_id = random.choice(patient_ids)
        
        # Spread invoices across 12 months
        days_offset = random.randint(0, 365)
        invoice_date = (base_date + timedelta(days=days_offset)).date()
        
        total_amount = random.uniform(100, 8000)
        
        status = random.choices(
            INVOICE_STATUS,
            weights=[50, 30, 20],  # More paid than pending/overdue
            k=1
        )[0]
        
        if status == "Paid":
            paid_amount = total_amount
        elif status == "Pending":
            paid_amount = 0
        else:  # Overdue
            paid_amount = random.uniform(0, total_amount * 0.5)
        
        invoices.append((patient_id, invoice_date, total_amount, paid_amount, status))
    
    cursor.executemany("""
        INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
        VALUES (?, ?, ?, ?, ?)
    """, invoices)
    
    conn.commit()
    print(f"✓ Created {len(invoices)} invoices")
    return len(invoices)


def main():
    """Main setup function"""
    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed existing {DB_PATH}")
    
    # Create connection
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        # Create schema
        create_schema(conn)
        
        # Insert data
        doctor_count = insert_doctors(conn)
        patient_count = insert_patients(conn)
        appointment_count = insert_appointments(conn)
        treatment_count = insert_treatments(conn)
        invoice_count = insert_invoices(conn)
        
        # Summary
        print("\n" + "="*50)
        print("Database Setup Complete!")
        print("="*50)
        print(f"Created {patient_count} patients")
        print(f"Created {doctor_count} doctors")
        print(f"Created {appointment_count} appointments")
        print(f"Created {treatment_count} treatments")
        print(f"Created {invoice_count} invoices")
        print(f"Database saved to: {DB_PATH}")
        print("="*50 + "\n")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
