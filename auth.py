
import os
import hmac
import hashlib
import secrets
import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "faculty_users.db"

DATA_DIR.mkdir(exist_ok=True)

# Password hashing configuration
ITERATIONS = 310000


def get_connection():
    """Create a connection to the faculty database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the faculty and admin tables."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id TEXT PRIMARY KEY,
                faculty_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)


def hash_password(password, salt=None):
    """Generate a secure salted password hash."""
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        ITERATIONS
    ).hex()

    return password_hash, salt


def verify_password(password, stored_hash, salt):
    """Verify a password against its stored hash."""
    calculated_hash, _ = hash_password(password, salt)

    return hmac.compare_digest(calculated_hash, stored_hash)


def create_admin(admin_id, password):
    """Create the initial administrator account."""
    initialize_database()

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT admin_id FROM admins WHERE admin_id = ?",
            (admin_id,)
        ).fetchone()

        if existing:
            return False, "Administrator already exists."

        password_hash, salt = hash_password(password)

        conn.execute("""
            INSERT INTO admins (admin_id, password_hash, salt)
            VALUES (?, ?, ?)
        """, (admin_id, password_hash, salt))

    return True, "Administrator account created successfully."


def verify_admin(admin_id, password):
    """Verify administrator login."""
    initialize_database()

    with get_connection() as conn:
        admin = conn.execute("""
            SELECT password_hash, salt
            FROM admins
            WHERE admin_id = ?
        """, (admin_id,)).fetchone()

    if not admin:
        return False

    return verify_password(password, admin[0], admin[1])


def create_faculty(faculty_id, faculty_name, password):
    """Create an individual faculty account."""
    initialize_database()

    faculty_id = faculty_id.strip()
    faculty_name = faculty_name.strip()

    if not faculty_id or not faculty_name or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT faculty_id FROM faculty WHERE faculty_id = ?",
            (faculty_id,)
        ).fetchone()

        if existing:
            return False, "Faculty ID already exists."

        password_hash, salt = hash_password(password)

        conn.execute("""
            INSERT INTO faculty (
                faculty_id, faculty_name, password_hash, salt
            )
            VALUES (?, ?, ?, ?)
        """, (faculty_id, faculty_name, password_hash, salt))

    return True, "Faculty account created successfully."


def verify_faculty(faculty_id, password):
    """Verify faculty login and return faculty details."""
    initialize_database()

    with get_connection() as conn:
        faculty = conn.execute("""
            SELECT faculty_id, faculty_name, password_hash, salt
            FROM faculty
            WHERE faculty_id = ? AND is_active = 1
        """, (faculty_id.strip(),)).fetchone()

    if not faculty:
        return None

    if verify_password(password, faculty[2], faculty[3]):
        return {
            "faculty_id": faculty[0],
            "faculty_name": faculty[1]
        }

    return None


def get_all_faculty():
    """Return all faculty accounts without password information."""
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT faculty_id, faculty_name, created_at, is_active
            FROM faculty
            ORDER BY faculty_name
        """).fetchall()

    return rows


def deactivate_faculty(faculty_id):
    """Deactivate a faculty account."""
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE faculty
            SET is_active = 0
            WHERE faculty_id = ?
        """, (faculty_id,))

    return cursor.rowcount > 0


def reset_faculty_password(faculty_id, new_password):
    """Reset a faculty member's password."""
    if len(new_password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash, salt = hash_password(new_password)

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE faculty
            SET password_hash = ?, salt = ?, is_active = 1
            WHERE faculty_id = ?
        """, (password_hash, salt, faculty_id))

    if cursor.rowcount == 0:
        return False, "Faculty account not found."

    return True, "Password reset successfully."


if __name__ == "__main__":
    initialize_database()
    print("Faculty database initialized successfully.")
    print(f"Database location: {DB_PATH}")
