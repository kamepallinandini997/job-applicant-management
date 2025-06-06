import json
import logging
from datetime import datetime
from functools import wraps
from collections import Counter, defaultdict

# ===== Logging Setup
logging.basicConfig(
    filename='applicant_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging = logging.getLogger(__name__)

# ===== Exception Handler Decorator
def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info(f"Executing: {func.__name__}")
            return func(*args, **kwargs)  # <--- You need this!
        except Exception as e:
            logging.exception(f"Error while executing: {func.__name__} : {e}")
            return None  # Optional: make failure explicit
    return wrapper


# ===== Models
class Project:
    def __init__(self, email, name, status):
        self.email = email
        self.name = name
        self.status = status

class Applicant:
    def __init__(self, name, email, role, location, skills, experience, expected_salary, status):
        self.name = name
        self.email = email
        self.role = role
        self.location = location
        self.skills = skills
        self.experience = experience
        self.expected_salary = expected_salary
        self.status = status

# ===== Helper Methods
@handle_exceptions
def load_applicants(filepath):
    with open(filepath, 'r') as f:
        applicants = json.load(f)
        return [Applicant(**a) for a in applicants]

@handle_exceptions
def save_applicants(filepath, applicants):
    with open(filepath, 'w') as f:
        json.dump([a.__dict__ for a in applicants], f, indent=2)

def view_applicant(applicants, identifier):
    identifier = identifier.lower()
    for a in applicants:
        if a.email.lower() == identifier or a.name.lower() == identifier:
            return a
    return None
 
def update_status(applicants):
    identifier = input("Enter applicant's Email or Name: ").strip()
    applicant = view_applicant(applicants, identifier)
    if applicant:
        new_status = input(f"Enter new status for {applicant.name} (current: {applicant.status}): ").strip()
        applicant.status = new_status
        print(" Status updated.")
    else:
        print("Applicant not found.")
 
def filter_by_experience(applicants):
    try:
        min_exp = int(input("Min Experience: ").strip())
        max_exp = int(input("Max Experience: ").strip())
    except ValueError:
        print("Invalid experience input.")
        return
    filtered = [a for a in applicants if min_exp <= a.experience <= max_exp]
    print_applicants(filtered)
 
def count_by_location(applicants):
    location_counts = {}
    for a in applicants:
        location_counts[a.location] = location_counts.get(a.location, 0) + 1
    print("\nApplicant Count by Location:")
    for loc, count in location_counts.items():
        print(f"{loc}: {count}")
 
def avg_salary_by_role(applicants):
    total_salary = {}
    count = {}
    for a in applicants:
        total_salary[a.role] = total_salary.get(a.role, 0) + a.expected_salary
        count[a.role] = count.get(a.role, 0) + 1
    print("\n Average Expected Salary per Role:")
    for role in total_salary:
        avg = total_salary[role] / count[role]
        print(f"{role}: ₹{avg:.2f}")
 
def print_applicants(applicants):
    if not applicants:
        print("No matching applicants.")
        return
    for a in applicants:
        print(f"\nName: {a.name}, Email: {a.email}")
        print(f"Role: {a.role}, Location: {a.location}")
        print(f"Skills: {', '.join(a.skills)}")
        print(f"Experience: {a.experience} yrs, Salary: ₹{a.expected_salary}, Status: {a.status}")



# ===== CLI Interface
def showcli(applicants, filepath):
    while True:
        print("\n=== Job Applicant CLI ===")
        print("1. Add New Applicant")
        print("2. View Applicant by Email/Name")
        print("3. Update Applicant Status")
        print("4. Delete Applicant")
        print("5. Filter Applicant by Role")
        print("6. Filter Applicant by Location")
        print("7. Filter Applicant by Skill")
        print("8. Filter Applicant by Experience Range")
        print("9. Filter Applicant by Expected Salary Range")
        print("10. Filter Applicant by Application Status")
        print("11. Count Applicants per Role")
        print("12. Count Applicants per Location")
        print("13. Count Applicants per Skill")
        print("14. Avg Experience per Role")
        print("15. Avg Expected Salary per Role")
        print("16. Exit")

        choice = input("Please Select an Option: ")


        if choice == '3':
            update_status(applicants)
            save_applicants(filepath, applicants)
 
        elif choice == '8':
            filter_by_experience(applicants)
 
        elif choice == '12':
            count_by_location(applicants)
 
        elif choice == '15':
            avg_salary_by_role(applicants)
 
        elif choice == '16':
            print("Exiting... Bye!")
            break
        

# ===== Entry Point
if __name__ == "__main__":
    filepath = "job_applicants.json"
    applicants = load_applicants(filepath=filepath)

    if applicants:
        showcli(applicants, filepath)
    else:
        print("No applicants found or file is missing.")
