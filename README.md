# Saifur Rahman — Portfolio

A Flask and SQLite portfolio website with a private admin studio and an
interactive 3D experience.

## Run locally

### Windows

1. Open the `portfolio-app` folder.
2. Double-click `START.bat`.
3. Open the local URL printed in the terminal.

The launcher creates a local virtual environment, installs the pinned
dependencies, and selects an available port between 5000 and 5010.

### Manual startup

From the repository root, run:

```powershell
cd portfolio-app
.\.venv\Scripts\python.exe app.py
```

The app uses port 5000 by default. Set the `PORT` environment variable first
to choose another port.

## Admin studio

Open `/studio` at the local URL. On first launch, create the private admin
account with an email address and a password of at least 12 characters.

## Project structure

- `portfolio-app/app.py` — Flask application entry point
- `portfolio-app/portfolio/` — application routes, database, and admin logic
- `portfolio-app/templates/` — public and admin HTML templates
- `portfolio-app/static/` — styles, scripts, and site assets
- `portfolio-app/requirements.txt` — pinned Python dependencies
- `portfolio-app/START.bat` — Windows startup launcher

The SQLite database, uploads, virtual environment, and generated secrets are
local-only and excluded from version control.
