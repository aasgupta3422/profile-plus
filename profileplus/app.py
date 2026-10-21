from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-only-change-me")
DB = os.environ.get("DATABASE_PATH", "resume_builder.db")

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

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

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
        email = request.form["email"].strip().lower()
        password = request.form["password"]

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

def login_required():
    return "user_email" in session

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session.get("user_name"))

@app.route("/resume", methods=["GET", "POST"])
def resume():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name", ""),
            "email": request.form.get("email", ""),
            "phone": request.form.get("phone", ""),
            "education": request.form.get("education", ""),
            "skills": request.form.get("skills", ""),
            "projects": request.form.get("projects", ""),
            "experience": request.form.get("experience", ""),
            "certifications": request.form.get("certifications", "")
        }
        return render_template("resume.html", data=data, preview=True)

    return render_template("resume.html", data={}, preview=False)

@app.route("/resume/pdf", methods=["POST"])
def resume_pdf():
    if not login_required():
        return redirect(url_for("login"))

    data = request.form
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(data.get("name", "Resume"), styles["Title"]))
    story.append(Paragraph(
        f'{data.get("email","")} | {data.get("phone","")}',
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    sections = [
        ("Education", data.get("education", "")),
        ("Skills", data.get("skills", "")),
        ("Projects", data.get("projects", "")),
        ("Experience", data.get("experience", "")),
        ("Certifications", data.get("certifications", "")),
    ]
    for title, value in sections:
        if value.strip():
            story.append(Paragraph(title, styles["Heading2"]))
            story.append(Paragraph(value.replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="resume.pdf", mimetype="application/pdf")

@app.route("/career")
def career():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("career.html")

# Initialize the database when the app module loads (needed by production WSGI servers).
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
