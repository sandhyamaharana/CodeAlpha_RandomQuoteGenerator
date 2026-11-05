# CodeAlpha Random Quote Generator

A separate Python Flask web app. Generate non-repeating quotes, copy them, and save favorites.

## Run on Windows

`powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
`

Open http://127.0.0.1:5002 in your browser. The app stores its data in a local SQLite database beside pp.py.
