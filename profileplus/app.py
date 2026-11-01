import os
import sqlite3
from io import BytesIO
from xml.sax.saxutils import escape

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")
DB = os.environ.get("DATABASE_PATH", "resume_builder.db")

TEMPLATES = {
    "classic": {"name": "Classic Professional", "color": "#23466b"},
    "sidebar": {"name": "Modern Sidebar", "color": "#176b65"},
    "technical": {"name": "Technical Projects", "color": "#2457a7"},
    "minimal": {"name": "Elegant Minimal", "color": "#555555"},
    "bold": {"name": "Bold Accent", "color": "#9b3d28"},
}

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize database for both local execution and Gunicorn/Render startup.
init_db()

def login_required():
    return "user_email" in session

def clean_resume_form(form):
    fields = [
        "name", "profession", "email", "phone", "location", "linkedin",
        "github", "website", "summary", "education", "skills", "projects",
        "experience", "certifications", "languages"
    ]
    return {field: form.get(field, "").strip() for field in fields}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("Please fill all fields.")
            return redirect(url_for("signup"))
        conn = db()
        try:
            conn.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Email already registered.")
            return redirect(url_for("signup"))
        conn.close()
        session["user_email"] = email
        session["user_name"] = name
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_email"] = user["email"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")
