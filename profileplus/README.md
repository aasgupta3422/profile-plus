# Profile+ — Resume Builder & Career Assistance

A Flask-based student project with account registration/login, a dashboard, a five-template resume builder, resume preview, PDF export, and a career assistance demo page.

## Resume builder
1. Sign up or log in.
2. Open **Resume Builder** from the dashboard.
3. Select one of five designs: Classic Professional, Modern Sidebar, Technical Projects, Elegant Minimal, or Bold Accent.
4. Enter the person's name, profession/target role, contact details, education, skills, projects, experience, certifications, and languages.
5. Select **Preview selected template**.
6. Review the resume and select **Download PDF**.

The preview applies the selected design in the browser. PDF export uses ReportLab and applies the selected design's accent color and a structured resume layout.

## Run locally (Windows)
1. Install Python 3.
2. Open this folder in VS Code.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000

## Deploy on Render
- Root directory: `profileplus` (if the repository contains this folder)
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Set a strong `SECRET_KEY` environment variable. Do not use the development fallback for production.
- Configure persistent storage/database hosting before relying on SQLite user accounts in production. The local SQLite file may not survive all redeploys or instance replacements.

## Current limitations
- Resume content is generated from the submitted form; resume details are not currently saved as user-owned records in the database.
- Career assistance is currently a demo page; no AI API or live job API is integrated.
- PDF output uses a clean ReportLab layout with a template-specific accent color. The browser preview carries the fuller visual styling.
