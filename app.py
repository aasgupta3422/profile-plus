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

# Create the SQLite tables when the app starts under Gunicorn/Render.
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
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_email"] = user["email"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session.get("user_name"))

@app.route("/resume", methods=["GET", "POST"])
def resume():
    if not login_required():
        return redirect(url_for("login"))
    selected = "classic"
    data = {}
    preview = False
    if request.method == "POST":
        data = clean_resume_form(request.form)
        selected = request.form.get("template", "classic")
        if selected not in TEMPLATES:
            selected = "classic"
        preview = request.form.get("action") == "preview"
    return render_template(
        "resume.html", data=data, preview=preview,
        templates=TEMPLATES, selected_template=selected
    )

@app.route("/resume/pdf", methods=["POST"])
def resume_pdf():
    if not login_required():
        return redirect(url_for("login"))
    data = clean_resume_form(request.form)
    template_key = request.form.get("template", "classic")
    if template_key not in TEMPLATES:
        template_key = "classic"
    accent = colors.HexColor(TEMPLATES[template_key]["color"])

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=42, leftMargin=42,
        topMargin=40, bottomMargin=40
    )
    base = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "ResumeName", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=27, textColor=accent, spaceAfter=5
    )
    role_style = ParagraphStyle(
        "ResumeRole", parent=base["Normal"], fontSize=11,
        leading=15, textColor=colors.HexColor("#4B5563"), spaceAfter=7
    )
    heading_style = ParagraphStyle(
        "ResumeHeading", parent=base["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, textColor=accent, spaceBefore=12, spaceAfter=4
    )
    body_style = ParagraphStyle(
        "ResumeBody", parent=base["BodyText"], fontSize=9.5,
        leading=13, spaceAfter=3
    )
    story = []
    story.append(Paragraph(escape(data["name"] or "Your Name"), name_style))
    if data["profession"]:
        story.append(Paragraph(escape(data["profession"]), role_style))
    contact = " | ".join(x for x in [
        data["email"], data["phone"], data["location"], data["linkedin"],
        data["github"], data["website"]
    ] if x)
    if contact:
        story.append(Paragraph(escape(contact), body_style))
    if data["summary"]:
        story.append(Paragraph("PROFILE", heading_style))
        story.append(Paragraph(escape(data["summary"]).replace("\n", "<br/>"), body_style))
    for label, key in [
        ("EDUCATION", "education"), ("SKILLS", "skills"),
        ("PROJECTS", "projects"), ("EXPERIENCE", "experience"),
        ("CERTIFICATIONS", "certifications"), ("LANGUAGES", "languages")
    ]:
        value = data.get(key, "")
        if value:
            story.append(Paragraph(label, heading_style))
            story.append(Paragraph(escape(value).replace("\n", "<br/>"), body_style))
    doc.build(story)
    buffer.seek(0)
    filename = (data["name"].strip().replace(" ", "_") or "resume") + "_resume.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

@app.route("/career")
def career():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("career.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
