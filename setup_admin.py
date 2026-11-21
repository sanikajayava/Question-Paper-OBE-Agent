
from getpass import getpass
from auth import create_admin

print("=== OBE Administrator Setup ===")

admin_id = input("Enter Admin ID: ").strip()
password = getpass("Enter a new strong admin password: ")
confirm_password = getpass("Confirm admin password: ")

if password != confirm_password:
    print("Passwords do not match.")
elif len(password) < 8:
    print("Password must contain at least 8 characters.")
else:
    success, message = create_admin(admin_id, password)
    print(message)
