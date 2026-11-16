import csv
import hashlib
import hmac
import re
import uuid
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_CATEGORIES = ["Harassment", "Unsafe Area", "Stalking", "General Safety Concern"]
URGENCY_LEVELS = ["Low", "Moderate", "High"]
PASSWORD_LENGTH = 8
MAX_CONTACTS = 3
ACCOUNT_FIELDS = ["id", "email", "name", "phone", "salt", "password_hash"]
CONTACT_FIELDS = ["id", "user_id", "name", "phone"]
REPORT_FIELDS = [
    "id",
    "category",
    "location",
    "description",
    "urgency",
    "date",
    "created_at",
]


def _csv_path(file_name):
    return DATA_DIR / file_name


def _read_csv(file_name, fieldnames):
    path = _csv_path(file_name)
    try:
        with path.open(newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or not set(fieldnames).issubset(reader.fieldnames):
                raise ValueError(f"{file_name} has an invalid header.")
            return [
                {field: row.get(field, "") or "" for field in fieldnames}
                for row in reader
            ]
    except csv.Error as error:
        raise ValueError(f"{file_name} is not a valid CSV file.") from error


def _write_csv(file_name, fieldnames, rows):
    path = _csv_path(file_name)
    try:
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except csv.Error as error:
        raise ValueError(f"{file_name} could not be written.") from error


def _append_csv(file_name, fieldnames, row):
    path = _csv_path(file_name)
    if not path.exists():
        _write_csv(file_name, fieldnames, [])
    else:
        _read_csv(file_name, fieldnames)
    try:
        with path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow(row)
    except csv.Error as error:
        raise ValueError(f"{file_name} could not be written.") from error


def initialize_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for file_name, fieldnames in (
        ("accounts.csv", ACCOUNT_FIELDS),
        ("contacts.csv", CONTACT_FIELDS),
        ("community_reports.csv", REPORT_FIELDS),
    ):
        if not _csv_path(file_name).exists():
            _write_csv(file_name, fieldnames, [])


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
    accounts = _read_csv("accounts.csv", ACCOUNT_FIELDS)
    if any(account["email"].strip().lower() == email for account in accounts):
        return None

    salt = uuid.uuid4().hex
    account = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "phone": phone,
        "salt": salt,
        "password_hash": _password_hash(password, salt),
    }
    _append_csv("accounts.csv", ACCOUNT_FIELDS, account)
    return public_account(account)


def authenticate(email, password):
    normalized_email = email.strip().lower()
    accounts = _read_csv("accounts.csv", ACCOUNT_FIELDS)
    account = next(
        (
            account
            for account in accounts
            if account["email"].strip().lower() == normalized_email
        ),
        None,
    )
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
    accounts = _read_csv("accounts.csv", ACCOUNT_FIELDS)
    for account in accounts:
        if account["id"] == account_id:
            account["name"] = name
            account["phone"] = phone
            _write_csv("accounts.csv", ACCOUNT_FIELDS, accounts)
            return public_account(account)
    return None


def load_reports():
    reports = _read_csv("community_reports.csv", REPORT_FIELDS)
    reports.sort(
        key=lambda report: (report["date"], report["created_at"]),
        reverse=True,
    )
    return [
        {field: report[field] for field in REPORT_FIELDS if field != "created_at"}
        for report in reports
    ]


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
        "created_at": datetime.now().isoformat(timespec="microseconds"),
    }
    _append_csv("community_reports.csv", REPORT_FIELDS, report)
    return {field: report[field] for field in REPORT_FIELDS if field != "created_at"}


def load_contacts(user_id):
    contacts = _read_csv("contacts.csv", CONTACT_FIELDS)
    return [
        {"id": contact["id"], "name": contact["name"], "phone": contact["phone"]}
        for contact in contacts
        if contact["user_id"] == user_id
    ]


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
    accounts = _read_csv("accounts.csv", ACCOUNT_FIELDS)
    if not any(account["id"] == user_id for account in accounts):
        raise ValueError("The account could not be found.")

    saved = [
        {"id": str(uuid.uuid4()), "name": contact["name"], "phone": contact["phone"]}
        for contact in normalized
    ]
    contacts = _read_csv("contacts.csv", CONTACT_FIELDS)
    other_contacts = [
        contact for contact in contacts if contact["user_id"] != user_id
    ]
    new_contacts = [
        {"id": contact["id"], "user_id": user_id, "name": contact["name"], "phone": contact["phone"]}
        for contact in saved
    ]
    _write_csv("contacts.csv", CONTACT_FIELDS, other_contacts + new_contacts)
    return saved


def render_page_sidebar():
    import streamlit as st

    account = st.session_state.get("current_user")
    with st.sidebar:
        st.markdown("### 🛡️ SHEild AI")
        st.caption("Safety planning and community information")
        if account:
            st.caption(f"Signed in as {account['name']}")
            if st.button("🚪 Sign out", key="page_sign_out"):
                st.session_state.pop("current_user", None)
                st.rerun()
    return account


def require_account():
    import streamlit as st

    account = render_page_sidebar()
    if not account:
        st.warning("Sign in to manage your contacts and profile.")
        st.page_link("pages/login.py", label="🔐 Login")
        st.stop()
    return account
