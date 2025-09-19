import random, csv
from faker import Faker
from datetime import datetime

fake = Faker()

departments = ["ICU", "ER", "Surgical", "Oncology", "Pediatrics", "Cardiology"]
medications = ["antibiotic", "insulin", "painkiller", "IV fluids", "steroids", "oxygen therapy"]
routes = ["oral tablet", "IV line", "injection"]

def generate_compliance_data_flat(n=10000):
    records = []
    for i in range(n):
        hospital = fake.company() + " Hospital"
        branch = random.choice(["Main", "East Wing", "West Pavilion", "North Tower"])
        department = random.choice(departments)
        floor = f"{random.randint(1,10)}th Floor - Unit {random.choice(['A','B','C'])}"
        date = fake.date_this_year()
        patient_id = "PT_" + str(random.randint(100, 999))
        nurse_id = "RN_" + str(random.randint(100, 500))
        doctor_name = random.choice(["Smith", "Lee", "Patel", "Brown", "Nguyen", "Garcia"])
        
        # Doctor order
        med = random.choice(medications)
        route = random.choice(routes)
        freq = random.choice(["once daily", "twice daily", "every 6 hours", "night only"])
        order_text = f"Doctor {doctor_name}: Administer {med} via {route}, {freq}, to patient {patient_id}."
        
        # Nurse action (sometimes compliant, sometimes not)
        compliance_case = random.choice(["match", "partial", "miss"])
        
        if compliance_case == "match":
            action_text = f"Nurse {nurse_id}: Administered {med} via {route}, {freq}, to patient {patient_id} as ordered."
            compliance_status = "Compliant"
        elif compliance_case == "partial":
            alt_route = random.choice(routes)
            action_text = f"Nurse {nurse_id}: Gave {med} via {alt_route}, once to patient {patient_id}."
            compliance_status = "Partial"
        else:  # miss
            other_med = random.choice(medications)
            action_text = f"Nurse {nurse_id}: Administered {other_med} to patient {patient_id}, no matching order found."
            compliance_status = "Missed"
        
        records.append({
            "record_id": f"PAIR_{i:06}",
            "hospital": hospital,
            "branch": branch,
            "department": department,
            "floor": floor,
            "date": str(date),
            "patient_id": patient_id,
            "nurse_id": nurse_id,
            "doctor_order": order_text,
            "nurse_action": action_text,
            "compliance_status": compliance_status
        })
    
    return records


if __name__ == "__main__":
    data = generate_compliance_data_flat(10000)
    
    # Save as JSON
    import json
    with open("data/compliance_flat.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save as CSV
    with open("data/compliance_flat.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print("✅ Generated compliance_flat.json and compliance_flat.csv")
