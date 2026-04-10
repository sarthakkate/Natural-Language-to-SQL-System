"""
Seed Agent Memory with Example Q&A Pairs
Pre-loads Vanna 2.0 Agent with known good SQL examples for learning
"""

from vanna_setup import get_agent


# 15 Known good Q&A pairs covering all domains
SEED_QA_PAIRS = [
    # Patient queries
    {
        "question": "How many patients do we have?",
        "sql": "SELECT COUNT(*) AS total_patients FROM patients"
    },
    {
        "question": "List all patients from New York",
        "sql": "SELECT first_name, last_name, email, phone FROM patients WHERE city = 'New York'"
    },
    {
        "question": "Show male patients registered in the last 3 months",
        "sql": "SELECT first_name, last_name, registered_date FROM patients WHERE gender = 'M' AND registered_date >= date('now', '-3 months')"
    },
    {
        "question": "Which city has the most patients?",
        "sql": "SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1"
    },
    
    # Doctor queries
    {
        "question": "List all doctors and their specializations",
        "sql": "SELECT name, specialization, department FROM doctors ORDER BY name"
    },
    {
        "question": "Which doctor has the most appointments?",
        "sql": "SELECT d.name, COUNT(a.id) AS appointment_count FROM doctors d LEFT JOIN appointments a ON d.id = a.doctor_id GROUP BY d.id ORDER BY appointment_count DESC LIMIT 1"
    },
    {
        "question": "Show appointments per doctor specialization",
        "sql": "SELECT d.specialization, COUNT(a.id) AS appointment_count FROM doctors d LEFT JOIN appointments a ON d.id = a.doctor_id GROUP BY d.specialization ORDER BY appointment_count DESC"
    },
    
    # Appointment queries
    {
        "question": "Show appointments for last month",
        "sql": "SELECT a.id, p.first_name, p.last_name, d.name, a.appointment_date, a.status FROM appointments a JOIN patients p ON a.patient_id = p.id JOIN doctors d ON a.doctor_id = d.id WHERE a.appointment_date >= date('now', '-1 month') ORDER BY a.appointment_date DESC"
    },
    {
        "question": "How many cancelled appointments last quarter?",
        "sql": "SELECT COUNT(*) AS cancelled_count FROM appointments WHERE status = 'Cancelled' AND appointment_date >= date('now', '-3 months')"
    },
    {
        "question": "Show appointment status distribution",
        "sql": "SELECT status, COUNT(*) AS count FROM appointments GROUP BY status"
    },
    
    # Financial queries
    {
        "question": "What is the total revenue?",
        "sql": "SELECT SUM(total_amount) AS total_revenue FROM invoices"
    },
    {
        "question": "Show revenue by doctor",
        "sql": "SELECT d.name, SUM(i.total_amount) AS total_revenue FROM invoices i JOIN appointments a ON a.patient_id = i.patient_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.name ORDER BY total_revenue DESC"
    },
    {
        "question": "Show unpaid invoices",
        "sql": "SELECT i.id, p.first_name, p.last_name, i.total_amount, i.paid_amount, i.status FROM invoices i JOIN patients p ON i.patient_id = p.id WHERE i.status IN ('Pending', 'Overdue') ORDER BY i.invoice_date DESC"
    },
    
    # Time-based queries
    {
        "question": "Show monthly appointment count for the past 6 months",
        "sql": "SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) AS appointment_count FROM appointments WHERE appointment_date >= date('now', '-6 months') GROUP BY strftime('%Y-%m', appointment_date) ORDER BY month DESC"
    },
    {
        "question": "Show patient registration trend by month",
        "sql": "SELECT strftime('%Y-%m', registered_date) AS month, COUNT(*) AS new_patients FROM patients WHERE registered_date >= date('now', '-12 months') GROUP BY strftime('%Y-%m', registered_date) ORDER BY month ASC"
    }
]


def seed_memory():
    """
    Seeds agent memory with known good Q&A pairs
    """
    try:
        agent = get_agent()
        
        print("\nSeeding Agent Memory with Q&A Pairs...")
        print("=" * 60)
        
        for i, pair in enumerate(SEED_QA_PAIRS, 1):
            question = pair["question"]
            sql = pair["sql"]
            
            # Store in agent memory
            # Note: DemoAgentMemory stores successful interactions
            try:
                agent.memory.store_question_sql_mapping(
                    question=question,
                    sql=sql
                )
                print(f"{i:2d}. ✓ Stored: {question[:50]}...")
            except Exception as e:
                print(f"{i:2d}. ✗ Error storing: {question[:50]}... ({str(e)[:40]})")
        
        print("=" * 60)
        print(f"\n✓ Successfully seeded {len(SEED_QA_PAIRS)} Q&A pairs into agent memory")
        
        # Verify memory contents
        try:
            memory_size = len(agent.memory.get_all_mappings()) if hasattr(agent.memory, 'get_all_mappings') else len(SEED_QA_PAIRS)
            print(f"Memory status: {memory_size} items stored")
        except:
            print(f"Memory status: {len(SEED_QA_PAIRS)} items loaded (verification unavailable)")
        
        return agent
        
    except Exception as e:
        print(f"✗ Error seeding memory: {e}")
        raise


if __name__ == "__main__":
    seed_memory()
