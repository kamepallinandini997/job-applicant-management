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
    with open (filepath, 'r') as f:
        applicants  = json.load(f)
        return [Applicant(**a) for a in  applicants]
    
@handle_exceptions
def save_applicants(filepath, applicants):
    with open(filepath, 'w') as f:
        json.dump([a.__dict__ for a in applicants], f, indent=4)

# ----- Services -----------
@handle_exceptions
def delete_applicant(applicants, identifier):
    filtered = [a for a in applicants if a.email != identifier and a.name.lower() != identifier.lower()]
    if len(filtered) < len(applicants):
        print(f"Applicant '{identifier}' deleted.")
        return filtered
    else:
        print(f"No applicant found with email or name '{identifier}'.")
        return applicants

@handle_exceptions
def filter_by_role(applicants, role):
    filtered = [a for a in applicants if a.role.lower() == role.lower()]
    for a in filtered:
        print(f"{a.name} | {a.email} | {a.role} | {a.location} | {a.skills} | {a.experience} | {a.expected_salary} | {a.status}")
    return filtered

@handle_exceptions
def filter_by_status(applicants, status):
    filtered = [a for a in applicants if a.status.lower() == status.lower()]
    for a in filtered:
        print(f"{a.name} | {a.email} | {a.role} | {a.location} | {a.skills} | {a.experience} | {a.expected_salary} | {a.status}")
    return filtered


def showcli():
    while True:
        print("\n=== Job Applicant CLI ===")
        print("1. Add New Applicant")
        print("2. View Applicant by Email/Name")
        print("3. Update Applicant Status")
        print("4. Delete Applicant Email/Name")
        print("5. Filter Applicant by Role")
        print("6. Filter Applicant by Location")
        print("7. Filter Applicant by Skill")
        print("8. Filter Applicant by Experience Range")
        print("9. Filter Applicant by Expected Salary Range")
        print("10. Filter Applicant by Status")
        print("11. Count Applicants per Role")
        print("12. Count Applicants per Location")
        print("13. Count Applicants per Skill")
        print("14. Avg Experience per Role")
        print("15. Avg Expected Salary per Role")
        print("16. Exit")


        choice = input("Please Select an Option : ")

        if choice == "4":
            identifier = input("Enter applicant email or name to delete: ")
            filtered_applicants = delete_applicant(applicants, identifier)
            save_applicants(filepath, filtered_applicants)

        elif choice == "5":
            role = input("Enter role to filter by: ")
            filter_by_role(applicants, role)

        elif choice == "10":
            status = input("Enter application status to filter by: ")
            filter_by_status(applicants, status)

        elif choice == "16":
            print("Exiting Application. See you later....")
            break

        else:
            print("Invalid choice. Try again.")
            


if __name__ == "__main__":
    filepath = "job_applicants.json"
    applicants = load_applicants(filepath=filepath)

    if applicants:
        showcli()
    else:
        print ("No Applicants found or file is missing")
