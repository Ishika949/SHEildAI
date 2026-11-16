# SHEild AI

SHEild AI is a Streamlit student safety-planning and community information app. It stores accounts, trusted contacts, and community reports in SQLite.

## Requirements

- Python 3.10 or newer
- pip

## Install on Windows

Open PowerShell in the project folder and create a virtual environment:

```powershell
py -m venv .venv
```

Install the project dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

From the project folder:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open `http://localhost:8501` in a browser. Stop the app with `Ctrl+C` in PowerShell.

## Pages and features

- **App:** Links to the main sections and shows the safety notice.
- **Dashboard:** Requires an account. Saves up to three trusted contacts and plays the local 15-second SOS sound. The SMS preview is displayed in the app; no text message is sent.
- **AI Chat:** Matches questions to safety guidance in Learning. It does not connect to an external AI service.
- **Community Report:** Shows the public report feed and accepts reports with a concern type, location, urgency, and description. An account is not required.
- **Learning:** Covers women's safety, legal rights in India, constitutional rights, and what to do in an unsafe situation.
- **Login and Sign Up:** Create an account and sign in. Passwords must be at least eight characters.
- **Profile:** Requires an account and lets the signed-in user update their name and phone number.

## Data files

The app saves account details in `data/accounts.csv`, trusted contacts in
`data/contacts.csv`, and community reports in `data/community_reports.csv`.
Passwords are saved as salted hashes, not as plain text. These files are
excluded from Git.

This simple file storage is intended for a student demo. Do not use real
passwords, phone numbers, or safety reports. On Streamlit hosting, local files
may be lost when the app restarts, and simultaneous edits can overwrite each
other.

## Project files

```text
app.py                    App setup and navigation
pages/                    App, account, dashboard, report, learning, and chat pages
guidance.py               Learning content and local guidance search
utils.py                  Account, contact, report, and CSV file operations
.streamlit/config.toml    Streamlit theme
assets/                   Page images, favicon, and SOS audio
data/                     Local SQLite database
tests/                    Unit and Streamlit page tests
requirements.txt          Python dependencies
```

## Run tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
