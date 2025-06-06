import json
import logging
from datetime  import datetime
from functools import wraps

logging.basicConfig (
    filename = 'applicant_app.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)

logging = logging.getLogger(__name__)

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
def print_applicants(applicants):
    if not applicants:
        print("No applicants found.")
        return
    for idx, applicant in enumerate(applicants, 1):
        print(f"\nApplicant #{idx}")
        print(f"Name: {applicant.name}")
        print(f"Email: {applicant.email}")
        print(f"Role: {applicant.role}")
        print(f"Location: {applicant.location}")
        print(f"Skills: {', '.join(applicant.skills)}")
        print(f"Experience: {applicant.experience} years")
        print(f"Expected Salary: ₹{applicant.expected_salary}")
        print(f"Status: {applicant.status}")
    
    
def view_applicant(applicants, identifier):
    identifier = identifier.lower()
    for applicant in applicants:
        if applicant.email.lower() == identifier or applicant.name.lower() == identifier:
            return applicant
    return None
 
def filter_by_location(applicants, location):
    return [a for a in applicants if a.location.lower() == location.lower()]
 
def count_by_attribute(applicants, attribute_name):
    counts = {}
    for applicant in applicants:
        attr_value = getattr(applicant, attribute_name)
        if isinstance(attr_value, list):  # for skills
            for item in attr_value:
                counts[item] = counts.get(item, 0) + 1
        else:
            counts[attr_value] = counts.get(attr_value, 0) + 1
    return counts
 
def average_by_role(applicants, attribute_name):
    total_per_role = {}
    count_per_role = {}
    for applicant in applicants:
        role = applicant.role
        value = getattr(applicant, attribute_name)
        total_per_role[role] = total_per_role.get(role, 0) + value
        count_per_role[role] = count_per_role.get(role, 0) + 1
    return {role: total_per_role[role]/count_per_role[role] for role in total_per_role}
 
def showcli():
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


        choice = input("Please Select an Option : ")

        if choice == '2':
            identifier = input("Enter applicant's Email or Name: ").strip()
            applicant = view_applicant(applicants, identifier)
            if applicant:
                print_applicants([applicant])
            else:
                print("Applicant not found.")
 
        elif choice == '6':
            location = input("Enter location to filter by: ").strip()
            filtered = filter_by_location(applicants, location)
            print_applicants(filtered)
 
        elif choice == '13':
            counts = count_by_attribute(applicants, "skills")
            print("Applicants count per Skill:")
            for skill, count in counts.items():
                print(f"{skill}: {count}")
 
        elif choice == '14':
            averages = average_by_role(applicants, "experience")
            print("Average Experience per Role:")
            for role, avg in averages.items():
                print(f"{role}: {avg:.2f} years")
 
        elif choice == '16':
            print("Exiting... Bye!")
            break
 
        else:
            print("  Invalid choice. Try again.")
 

if __name__ == "__main__":
    filepath = "job_applicants.json"
    applicants = load_applicants(filepath=filepath)

    if applicants:
        showcli()
    else:
        print ("No Applicants found or file is missing")
