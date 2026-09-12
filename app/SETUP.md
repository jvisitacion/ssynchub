# Sync Hub — Installation & Setup Guide

This guide walks you through installing and running Sync Hub from scratch.

## Setup overview

```mermaid
flowchart TD
    install Python
    install Postgres
    create database: sync-hub
    copy .env.example to .env
    pip install requirements.txt
    run app: Main.py
```

---

## What is Sync Hub?

Sync Hub is a central place for developers to store and organize technical information and daily work notes. It keeps system flows, frontend, backend, database details, debugging ideas, and meeting notes in one place. This helps developers avoid forgetting tasks, reduces confusion, and makes it easier to turn ideas into working code.

---

## What you need first

- **Python 3.10 or newer**
- **PostgreSQL** (the Windows installer that includes pgAdmin works well)

---

## Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest Python 3 installer for Windows.
2. Run the installer.
3. **Important:** On the first screen, check **“Add Python to PATH”** before clicking Install. This lets you run Python from PowerShell.
4. When the install finishes, open **PowerShell** and verify:

   ```powershell
   python --version
   ```

   You should see something like `Python 3.12.x`. If you get an error that `python` is not found, reinstall Python with “Add to PATH” checked.

---

## Step 2: Install PostgreSQL

1. Download PostgreSQL for Windows from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/). The installer includes **pgAdmin**, a tool for managing your database.
2. Run the installer and follow the prompts.
3. When asked, set a password for the `postgres` user. **Write this down** — you will need it later in your `.env` file.

**In simple terms:**

- **PostgreSQL** — the program that stores your Sync Hub data on your computer.
- **pgAdmin** — the app you use to create databases and check that PostgreSQL is working.

After installation, PostgreSQL usually runs as a Windows service and starts automatically when you boot your PC.

---

## Step 3: Create the database in pgAdmin

1. Open **pgAdmin** from the Start menu.
2. In the left panel, expand **Servers** and connect to your local server (you may be asked for the `postgres` password you set during install).
3. Right-click **Databases** → **Create** → **Database…**
4. Set **Database** name to: `sync-hub`  
   This must match the name in `.env.example`.
5. Click **Save**.

You do **not** need to create tables by hand. On first launch, the app runs `db/schema.sql` automatically to set up everything it needs.

---

## Step 4: Set up the app folder

1. Open **PowerShell**.
2. Go to the `app` folder (adjust the path if your project lives somewhere else):

   ```powershell
   cd d:\myProjects\system-sync-hub\app
   ```

3. Install the Python packages the app needs:

   ```powershell
   pip install -r requirements.txt
   ```

   This installs the libraries listed in `requirements.txt` (database driver and environment file support).

---

## Step 5: Create your `.env` file

A **`.env` file** is a small text file that holds settings the app reads at startup (like your database password). It stays on your computer only.

1. In the `app` folder, copy `.env.example` to a new file named `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Open `.env` in any text editor (Notepad is fine).
3. Change `DB_PASSWORD` from `your_password_here` to the password you chose when installing PostgreSQL.
4. Leave the other values as they are unless you know you need to change them:

| Setting | What it means |
|---------|----------------|
| `DB_HOST` | Where the database lives (`localhost` = this PC) |
| `DB_PORT` | Door number PostgreSQL uses (`5432`) |
| `DB_DATABASE` | Database name (`sync-hub`) |
| `DB_USERNAME` | Login name (usually `postgres`) |
| `DB_PASSWORD` | Password you chose when installing PostgreSQL |
| `APP_THEME` | Starting theme (`dark` or `light`) |

**Security note:** Never share your `.env` file or commit it to git. It is already listed in `.gitignore` so it will not be uploaded by accident.

---

## Step 6: Run the app

From the `app` folder in PowerShell:

```powershell
python Main.py
```

`Main.py` is the entry point — it launches the Sync Hub window (`ui/app.py`).

If everything is configured correctly, the app window opens and connects to your `sync-hub` database.

---
