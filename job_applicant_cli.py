import json
import logging
from datetime  import datetime
from functools import wraps

logging.basicConfig (
    filename = 'applicant_app.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def handle_exceptions(func):
    @wraps(func)
    def wrapper (*args, **kwargs):
        try:
            logging.info(f"Executing: {func.__name__}")
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Error while Executing: {func.__name__} : {e}")
    return wrapper
class Project:
    def __init__(self, email, name,status):
        self.email = email
        self.name = name
        self.status = status

class Applicant:
    def __init__(self, name, email, role, location, skills, experience, expected_salary, status):
        self.name =  name
        self.email = email
        self.role = role
        self.location = location
        self.skills =  skills
        self.experience = experience
        self.expected_salary = expected_salary
        self.status = status
    
  
# ***** Helper Methods
@handle_exceptions
def load_applicants(filepath):
    try:
        with open (filepath, 'r') as f:
            applicants  = json.load(f)
            return [Applicant(**a) for a in  applicants]
    except FileNotFoundError:
        return [] 
@handle_exceptions
def save_applicants(filepath, applicants):
    with open(filepath, 'w') as f:
        json.dump([a.__dict__ for a in applicants], f, indent=4)

def add_applicant(applicants,filepath):
    name = input("Enter Name: ").strip()
    email = input("Enter Email: ").strip()
    role = input("Enter Role: ").strip()
    location = input("Enter Location: ").strip()
    skills_input = input("Enter Skills (comma-separated): ").strip()
    skills = [s.strip() for s in skills_input.split(",") if s.strip()]
    try:
        experience = int(input("Enter Experience (years): ").strip())
        expected_salary = int(input("Enter Expected Salary: ").strip())
    except ValueError:
        print("Invalid numeric input.")
        return
    status = input("Enter Application Status: ").strip()

    if any(app.email.lower() == email.lower() for app in applicants):
        print(" Applicant with this email already exists.")
        return

    applicant = Applicant(name, email, role, location, skills, experience, expected_salary, status)
    applicants.append(applicant)
    save_applicants(applicants, filepath)
    print("Applicant added successfully.")

def filter_applicants_by_skill(applicants, skill):
    return [a for a in applicants if skill.lower() in map(str.lower, a.skills)]

def filter_applicants_by_salary_range(applicants, min_salary, max_salary):
    return [a for a in applicants if min_salary <= a.expected_salary <= max_salary]

def count_applicants_by_role(applicants):
    role_counts = {}
    for app in applicants:
        role_counts[app.role] = role_counts.get(app.role, 0) + 1
    return role_counts

def display_applicants(applicants):
    if not applicants:
        print("No applicants found.")
        return
    for a in applicants:
        print(f"\nName: {a.name} Email: {a.email} Experience: {a.experience} yrs Status: {a.status}")
        
def showcli():
    while True:
        print("\n=== Job Applicant CLI ===")
        print("1. Add New Applicant")
        print("2. View Applicant by Email/Name")
        print("3. Update Applicant Status")
        print("4. Delete Applicant")
        print("5. Find all Applicants by Role")
        print("6. Find all Applicants by Location")
        print("7. Find all Applicants by Skill")
        print("8. Find all Applicants by Experience Range")
        print("9. Find all Applicants by Expected Salary Range")
        print("10. Find all Applicants by Application Status")
        print("11. Count Applicants per Role")
        print("12. Count Applicants per Location")
        print("13. Count Applicants per Skill")
        print("14. Avg Experience per Role")
        print("15. Avg Expected Salary per Role")
        print("16. Exit")


        choice = input("Please Select an Option : ")

        if choice == '1':
            add_applicant(applicants,filepath)
            save_applicants(filepath, applicants)

        elif choice == '7':
            skill = input("Enter Skill to Filter: ").strip()
            result = filter_applicants_by_skill(applicants, skill)
            display_applicants(result)

        elif choice == '9':
            try:
                min_salary = int(input("Enter Min Salary: ").strip())
                max_salary = int(input("Enter Max Salary: ").strip())
            except ValueError:
                print("Invalid salary input.")
                continue
            result = filter_applicants_by_salary_range(applicants, min_salary, max_salary)
            display_applicants(result)

        elif choice == '11':
            role_counts = count_applicants_by_role(applicants)
            print("\n  Applicant Count by Role:")
            for role, count in role_counts.items():
                print(f"{role}: {count}")

        elif choice == "16": # Exit
            print ("Exititng Application. See you later.....")
            break

        else:
            print ("Invalid Choice, please ennter number between 1 to 13")



if __name__ == "__main__":
    filepath = "job_applicants.json"
    applicants = load_applicants(filepath=filepath)

    if applicants:
        showcli()
    else:
        print ("No Applicants found or file is missing")
