import hashlib
import hmac
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_CATEGORIES = ["Harassment", "Unsafe Area", "Stalking", "General Safety Concern"]
URGENCY_LEVELS = ["Low", "Moderate", "High"]
PASSWORD_LENGTH = 8
MAX_CONTACTS = 3


def database_path():
    configured_path = os.environ.get("SHEILD_DB_PATH")
    return Path(configured_path).expanduser() if configured_path else DATA_DIR / "sheild.sqlite3"


@contextmanager
def _database():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_data():
    with _database() as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL DEFAULT '',
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS contacts_user_id_idx ON contacts(user_id);
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                urgency TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS reports_date_idx ON reports(date DESC);
            """
        )


def public_account(account):
    return {
        "id": account["id"],
        "email": account["email"],
        "name": account["name"],
        "phone": account["phone"],
    }


def _validate_account_input(email, name, phone, password):
    email = email.strip().lower()
    name = name.strip()
    phone = phone.strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")
    if not name or len(name) > 80:
        raise ValueError("Enter a name between 1 and 80 characters.")
    if len(phone) > 32:
        raise ValueError("Phone number must be 32 characters or fewer.")
    if len(password) < PASSWORD_LENGTH:
        raise ValueError("Use a password with at least 8 characters.")
    return email, name, phone


def _password_hash(password, salt):
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt.encode("utf-8"),
        n=16384,
        r=8,
        p=1,
        dklen=64,
    ).hex()


def create_account(email, name, phone, password):
    email, name, phone = _validate_account_input(email, name, phone, password)
    salt = uuid.uuid4().hex
    account = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "phone": phone,
        "salt": salt,
        "password_hash": _password_hash(password, salt),
    }
    try:
        with _database() as connection:
            connection.execute(
                """
                INSERT INTO accounts (id, email, name, phone, salt, password_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    account["id"],
                    account["email"],
                    account["name"],
                    account["phone"],
                    account["salt"],
                    account["password_hash"],
                ),
            )
    except sqlite3.IntegrityError as error:
        if "accounts.email" in str(error):
            return None
        raise
    return public_account(account)


def authenticate(email, password):
    normalized_email = email.strip().lower()
    with _database() as connection:
        account = connection.execute(
            "SELECT id, email, name, phone, salt, password_hash FROM accounts WHERE email = ?",
            (normalized_email,),
        ).fetchone()
    if account is None or not account["salt"] or not account["password_hash"]:
        return None
    try:
        stored_hash = bytes.fromhex(account["password_hash"])
    except ValueError as error:
        raise ValueError("This account record is invalid. Create a new account.") from error
    submitted_hash = bytes.fromhex(_password_hash(password, account["salt"]))
    if len(stored_hash) != len(submitted_hash) or not hmac.compare_digest(stored_hash, submitted_hash):
        return None
    return public_account(account)


def update_account(account_id, name, phone):
    name = name.strip()
    phone = phone.strip()
    if not name or len(name) > 80:
        raise ValueError("Enter a name between 1 and 80 characters.")
    if len(phone) > 32:
        raise ValueError("Phone number must be 32 characters or fewer.")
    with _database() as connection:
        connection.execute(
            "UPDATE accounts SET name = ?, phone = ? WHERE id = ?",
            (name, phone, account_id),
        )
        account = connection.execute(
            "SELECT id, email, name, phone FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
    return public_account(account) if account else None


def load_reports():
    with _database() as connection:
        reports = connection.execute(
            """
            SELECT id, category, location, description, urgency, date
            FROM reports
            ORDER BY date DESC, created_at DESC
            """
        ).fetchall()
    return [dict(report) for report in reports]


def save_report(category, location, urgency, description):
    category = category.strip()
    location = location.strip()
    description = description.strip()
    if category not in REPORT_CATEGORIES:
        raise ValueError("Choose a valid concern type.")
    if urgency not in URGENCY_LEVELS:
        raise ValueError("Choose a valid urgency level.")
    if not location or len(location) > 120:
        raise ValueError("Add an area or landmark under 120 characters.")
    if not description or len(description) > 1000:
        raise ValueError("Add a description under 1,000 characters.")
    report = {
        "id": str(uuid.uuid4()),
        "category": category,
        "location": location,
        "description": description,
        "urgency": urgency,
        "date": date.today().isoformat(),
    }
    with _database() as connection:
        connection.execute(
            """
            INSERT INTO reports (id, category, location, description, urgency, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                report["id"],
                report["category"],
                report["location"],
                report["description"],
                report["urgency"],
                report["date"],
            ),
        )
    return report


def load_contacts(user_id):
    with _database() as connection:
        contacts = connection.execute(
            "SELECT id, name, phone FROM contacts WHERE user_id = ? ORDER BY rowid",
            (user_id,),
        ).fetchall()
    return [dict(contact) for contact in contacts]


def save_contacts(user_id, contacts):
    normalized = []
    for contact in contacts:
        name = contact.get("name", "").strip()
        phone = contact.get("phone", "").strip()
        if not name and not phone:
            continue
        if not name or not phone:
            raise ValueError("Add both a name and a phone number for each contact.")
        if len(name) > 80 or len(phone) > 32:
            raise ValueError("Contact names must be at most 80 characters and phone numbers at most 32.")
        normalized.append({"name": name, "phone": phone})
    if len(normalized) > MAX_CONTACTS:
        raise ValueError("Save no more than three trusted contacts.")
    saved = [
        {"id": str(uuid.uuid4()), "name": contact["name"], "phone": contact["phone"]}
        for contact in normalized
    ]
    with _database() as connection:
        connection.execute("DELETE FROM contacts WHERE user_id = ?", (user_id,))
        connection.executemany(
            "INSERT INTO contacts (id, user_id, name, phone) VALUES (?, ?, ?, ?)",
            [
                (contact["id"], user_id, contact["name"], contact["phone"])
                for contact in saved
            ],
        )
    return saved


def render_page_sidebar():
    import streamlit as st

    account = st.session_state.get("current_user")
    with st.sidebar:
        st.markdown("### SHEild AI")
        st.caption("Safety planning and community information")
        if account:
            st.caption(f"Signed in as {account['name']}")
            if st.button("Sign out", key="page_sign_out"):
                st.session_state.pop("current_user", None)
                st.rerun()
    return account


def require_account():
    import streamlit as st

    account = render_page_sidebar()
    if not account:
        st.warning("Sign in to manage your contacts and profile.")
        st.page_link("pages/login.py", label="Login")
        st.stop()
    return account
