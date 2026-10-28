"""Pharmacy prescription and stock tracker.

Records medicine stock and expiry dates, looks up patients and their
allergies in a small SQLite database, dispenses prescriptions and
exports them to a JSON file.
"""

import json
import sqlite3
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


def parse_date(text):
    """Convert a YYYY-MM-DD string into a datetime object."""
    return datetime.strptime(text, DATE_FORMAT)


class Pharmacy:
    """Holds the patient database, medicine stock and prescriptions."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.stock = {}
        self.prescriptions = []
        self.batch_log = []

    def setup_database(self):
        """Create the patients table and insert sample patients."""
        patients = [
            ("P1", "Kavya", "penicillin"),
            ("P2", "Arjun", "none"),
            ("P3", "Meena", "ibuprofen"),
        ]
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE patients (id TEXT, name TEXT, allergy TEXT)"
        )
        cur.executemany("INSERT INTO patients VALUES (?, ?, ?)", patients)
        self.conn.commit()

    def find_patient(self, name):
        """Return (id, allergy) rows for a patient using a safe query."""
        cur = self.conn.cursor()
        query = "SELECT id, allergy FROM patients WHERE name = ?"
        return cur.execute(query, (name,)).fetchall()

    def add_stock(self, drug, units, expiry, batch_log=None):
        """Add units of a drug to stock and record the batch."""
        if batch_log is None:
            batch_log = self.batch_log
        if units <= 0:
            raise ValueError(f"units must be positive, got {units}")
        parse_date(expiry)  # raises ValueError if the date is invalid
        drug = drug.strip().title()
        current = self.stock.get(drug, {}).get("units", 0)
        self.stock[drug] = {"units": current + units, "expiry": expiry}
        batch_log.append((drug, units))
        return len(batch_log)

    def stock_problem(self, drug, units):
        """Return why a drug cannot be dispensed, or None if it can."""
        item = self.stock.get(drug)
        if item is None:
            return "not in stock"
        if units <= 0:
            return "invalid quantity"
        if item["units"] < units:
            return f"only {item['units']} units left"
        if parse_date(item["expiry"]) < datetime.now():
            return "batch has expired"
        return None

    def dispense(self, patient_name, drug, units):
        """Dispense a drug to a patient after allergy and stock checks."""
        rows = self.find_patient(patient_name)
        if not rows:
            print(f"Cannot dispense: unknown patient {patient_name}")
            return False
        patient_id, allergy = rows[0]
        drug = drug.strip().title()
        if allergy.lower() == drug.lower():
            print(f"Allergy warning for {patient_name}: {drug}")
            return False
        problem = self.stock_problem(drug, units)
        if problem:
            print(f"Cannot dispense {drug} to {patient_name}: {problem}")
            return False
        self.stock[drug]["units"] -= units
        self.prescriptions.append({
            "patient": patient_id,
            "drug": drug,
            "units": units,
            "time": datetime.now().isoformat(),
        })
        return True

    def expiring_soon(self, days=30):
        """Return drugs that expire within the given number of days."""
        now = datetime.now()
        return [
            drug for drug, item in self.stock.items()
            if (parse_date(item["expiry"]) - now).days < days
        ]

    def export_prescriptions(self, file="prescriptions.json"):
        """Write all prescriptions to a JSON file."""
        with open(file, "w", encoding="utf-8") as handle:
            json.dump(self.prescriptions, handle, indent=2)

    def load_stock(self, file="stock.json"):
        """Load stock from a JSON file if one exists."""
        try:
            with open(file, encoding="utf-8") as handle:
                self.stock = json.load(handle)
        except FileNotFoundError:
            print(f"No saved stock file ({file}); starting empty.")
        except json.JSONDecodeError as err:
            print(f"Could not read {file}: {err}")

    def print_stock(self):
        """Print every drug with its units and expiry date."""
        print("Pharmacy Stock")
        for drug, item in self.stock.items():
            print(drug, "->", item["units"], "units, expires",
                  item["expiry"])

    def close(self):
        """Close the database connection."""
        self.conn.close()


def main():
    """Run a short demo of the pharmacy system."""
    pharmacy = Pharmacy()
    pharmacy.setup_database()
    pharmacy.load_stock()

    deliveries = [
        ("Paracetamol", 100, "2027-03-01"),
        ("Amoxicillin", 20, "2025-12-31"),
        ("Penicillin", 50, "2027-01-15"),
        ("Ibuprofen", -15, "2026-11-30"),
    ]
    for drug, units, expiry in deliveries:
        try:
            pharmacy.add_stock(drug, units, expiry)
        except ValueError as err:
            print(f"Rejected {drug} delivery: {err}")

    print("Arjun gets Amoxicillin:",
          pharmacy.dispense("Arjun", "Amoxicillin", 30))
    print("Kavya gets Penicillin:",
          pharmacy.dispense("Kavya", "Penicillin", 10))
    print("Meena gets ibuprofen:",
          pharmacy.dispense("Meena", "ibuprofen", 2))
    print("Arjun gets Paracetamol:",
          pharmacy.dispense("Arjun", "Paracetamol", 10))
    print("Unknown patient:",
          pharmacy.dispense("Ghost", "Paracetamol", 5))

    name = input("Patient name to look up (Enter for Arjun): ").strip()
    print("Lookup result:", pharmacy.find_patient(name or "Arjun"))
    print("Expiring within 30 days:", pharmacy.expiring_soon())
    pharmacy.export_prescriptions()
    pharmacy.print_stock()
    pharmacy.close()


if __name__ == "__main__":
    main()