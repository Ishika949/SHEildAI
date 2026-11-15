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
- **Learning:** Contains guidance about safety planning, basic rights, unsafe situations, and emergency help.
- **Login and Sign Up:** Create an account and sign in. Passwords must be at least eight characters.
- **Profile:** Requires an account and lets the signed-in user update their name and phone number.

## Data storage

On first run, the app creates `data/sheild.sqlite3` and its database tables. It does not load sample records or import the legacy CSV files. The database contains account, contact, and report data; it is excluded from Git by `.gitignore`.

To use a different SQLite file, set `SHEILD_DB_PATH` before starting the app:

```powershell
$env:SHEILD_DB_PATH = "C:\path\to\sheild.sqlite3"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

For hosting, point `SHEILD_DB_PATH` to persistent storage. The app uses SQLite and should run as a single instance; data on an ephemeral filesystem may be lost when the host restarts.

## Project files

```text
app.py                    App setup and navigation
pages/                    App, account, dashboard, report, learning, and chat pages
guidance.py               Learning content and local guidance search
utils.py                  Account, contact, report, and SQLite operations
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
