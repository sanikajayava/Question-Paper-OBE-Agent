
from getpass import getpass
from auth import hash_password, initialize_database, get_connection

initialize_database()

password = getpass("Enter a new admin password: ")
confirm = getpass("Confirm new admin password: ")

if password != confirm:
    print("Passwords do not match.")
elif len(password) < 12:
    print("Use at least 12 characters.")
else:
    password_hash, salt = hash_password(password)

    with get_connection() as conn:
        conn.execute("""
            UPDATE admins
            SET password_hash = ?, salt = ?
            WHERE admin_id = ?
        """, (password_hash, salt, "admin"))

    print("Administrator password updated successfully.")
