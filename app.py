from flask import Flask,send_from_directory, sessions,render_template, request, redirect, session, url_for, flash, send_file
import os
import io
import random
import string
import ssl
import smtplib
import tempfile
import csv
import pickle
# Custom modules
from datetime import datetime

from database import (
    init_db, save_media_file, get_all_media, get_media_file,
    create_user, verify_user, get_user_by_email, reset_password ,
    save_text_result, get_user_text_history  , get_all_users, get_all_text_history,
    delete_user, delete_text_record
)
from werkzeug.utils import secure_filename
import tensorflow as tf       
from image_detector import analyze_image
from video_detector import analyze_video

from scam_detector import detect_scam
from utils import get_awareness_message

# =====================================================
#               FLASK APPLICATION SETUP
# =====================================================

app = Flask(__name__)
app.secret_key = "ai_shield_secret_key_2026"

# Initialize Database
init_db()

# =====================================================
#                   LANDING PAGE
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================================
#                   AUTHENTICATION
# =====================================================

# ------------------ SIGNUP ------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        success = create_user(name, email, password)

        if success:
            flash("Signup successful! Please login.", "success")
            return redirect("/login")
        else:
            flash("Email already exists. Try logging in.", "danger")
            return redirect("/signup")

    return render_template("signup.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = verify_user(email, password)

        if user:
            session["user_email"] = user["email"]
            session["is_admin"] = user["is_admin"]

            flash("Login successful!", "success")

            # ADMIN CHECK
            if user["is_admin"] == 1:
                return redirect("/admin")
            else:
                return redirect("/dashboard")

        else:
            flash("Invalid email or password.", "danger")
            return redirect("/login")

    return render_template("login.html")



# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    # Clear session if you’re using login sessions
    session.clear()
    # Redirect to the index page
    return redirect(url_for('index'))


# ------------------ FORGOT PASSWORD ------------------

def send_email(to_email, temp_password):
    smtp_server = "smtp.gmail.com"
    port = 465

    sender_email = "yourgmail@gmail.com"      # CHANGE THIS
    sender_password = "yourapppassword"       # CHANGE THIS

    message = f"""
Subject: AI Shield Password Reset

Your temporary password is: {temp_password}

Please login and change your password immediately.
"""

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        user = get_user_by_email(email)

        if user:
            temp_password = ''.join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

            reset_password(email, temp_password)

            try:
                send_email(email, temp_password)
                flash("Temporary password sent to your email!", "success")
            except:
                flash("Email sending failed. Configure SMTP settings.", "danger")

            return redirect("/login")

        else:
            flash("Email not registered.", "danger")

    return render_template("forgot_password.html")

# =====================================================
#                   ADMIN PANEL
# =====================================================

@app.route("/admin")
def admin_dashboard():
    if "user_email" not in session:
        return redirect("/login")

    if session.get("is_admin") != 1:
        return render_template("access_denied.html")

    print("Admin accessed dashboard:", session.get("user_email"))

    users = get_all_users()
    text_history = get_all_text_history()   # without real messages
    media = get_all_media()

    return render_template(
        "admin_dashboard.html",
        users=users,
        text_history=text_history,
        media=media
    )


# =====================================================
#                   USER DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        flash("Please login first.", "warning")
        return redirect("/login")

    return render_template("dashboard.html")

# ---------------------------------------------------
model = pickle.load(open('models/text_model.pkl', 'rb'))
vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))

# =====================================================
#               TEXT SCAM DETECTION
# =====================================================
def detect_scam(text):
    data = vectorizer.transform([text])
    prediction = model.predict(data)[0]

    return {
        "input": text,
        "verdict": prediction
    }
def get_awareness_message(verdict):
    if verdict.lower() in ["scam", "spam", "1"]:
        return "This message looks suspicious. Do not share personal details or click unknown links."
    else:
        return "This message seems safe. But always stay cautious online."


@app.route("/text", methods=["GET", "POST"])
def text_page():

    if "user_email" not in session:
        flash("Login required to access modules.", "warning")
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_text = request.form.get("message")

        if user_text:
            result = detect_scam(user_text)
            result["awareness"] = get_awareness_message(result["verdict"])
            # Save scan result in database
            save_text_result(session["user_email"], user_text, result["verdict"])

    return render_template("text.html", result=result)

# ====================================================
# TEXT HISTORY
# ====================================================
@app.route("/text_history")
def text_history():

    if "user_email" not in session:
        flash("Please login first.", "warning")
        return redirect("/login")

    history = get_user_text_history(session["user_email"])

    return render_template("text_history.html", history=history)

# =====================================================
#               IMAGE DETECTION MODULE
# =====================================================
@app.route("/image", methods=["GET", "POST"])
def image_page():

    if "user_email" not in session:
        flash("Login required to access modules.", "warning")
        return redirect("/login")

    result = None

    if request.method == "POST":

        if "image" not in request.files:
            flash("No file part", "danger")
            return redirect("/image")

        file = request.files["image"]

        if file.filename == "":
            flash("Please select an image", "danger")
            return redirect("/image")

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # ✅ Analyze image
        result = analyze_image(file_path, file.filename)
        result["image_path"] = file_path

        # ✅ Read file bytes
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # ✅ Save to database
        save_media_file(
            filename=file.filename,
            file_type="image",
            file_bytes=file_bytes,
            verdict=result.get("verdict", "Unknown"),
            fake_score=result.get("fake_percent", result.get("fake_score", 0)),
            real_score=result.get("real_percent", result.get("real_score", 0)),
            uploaded_by=session["user_email"]
        )

    return render_template("image.html", result=result)



# =====================================================
#               VIDEO DETECTION
# =====================================================
# @app.route("/video", methods=["GET", "POST"])
# def video_page():
#     if "user_email" not in session:
#         flash("Login required", "warning")
#         return redirect("/login")

#     result = None
#     temp_video_path = None

#     if request.method == "POST":
#         if "video" not in request.files:
#             flash("No file part", "danger")
#             return redirect("/video")

#         file = request.files["video"]

#         if file.filename == "":
#             flash("Please select a video", "danger")
#             return redirect("/video")

    
#         temp_dir = tempfile.gettempdir()
#         temp_video_path = os.path.join(temp_dir, file.filename)
#         file.save(temp_video_path)

#         analysis = analyze_video(temp_video_path)
#         analysis["video_filename"] = file.filename

#         result = analysis

#     return render_template("video.html", result=result, temp_video_path=temp_video_path)

# ---------------------------------------------------
# import base64

# @app.route("/video", methods=["GET", "POST"])
# def video_page():
#     if "user_email" not in session:
#         flash("Login required", "warning")
#         return redirect("/login")

#     result = None

#     if request.method == "POST":
#         file = request.files.get("video")
#         if not file or file.filename == "":
#             flash("Please select a video", "danger")
#             return redirect("/video")

#         import tempfile
#         tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
#         file.save(tmp_file.name)
#         tmp_path = tmp_file.name
#         tmp_file.close()
#         analysis = analyze_video(tmp_path)

#         with open(tmp_path, "rb") as f:
#             video_bytes = f.read()
#         video_base64 = base64.b64encode(video_bytes).decode("utf-8")
#         analysis["video_data"] = video_base64

#         os.remove(tmp_path)

#         result = analysis

#     return render_template("video.html", result=result)


# @app.route("/video", methods=["GET", "POST"])
# def video_page():
#     if "user_email" not in session:
#         flash("Login required", "warning")
#         return redirect("/login")

#     result = None

#     if request.method == "POST":
#         if "video" not in request.files:
#             flash("No file part", "danger")
#             return redirect("/video")

#         file = request.files["video"]
#         if file.filename == "":
#             flash("Please select a video", "danger")
#             return redirect("/video")

#         upload_folder = os.path.join("static", "uploads", "videos")
#         os.makedirs(upload_folder, exist_ok=True)
#         save_path = os.path.join(upload_folder, file.filename)
#         file.save(save_path)
#         analysis = analyze_video(save_path)

#         analysis["video_filename"] = file.filename
#         result = analysis

#     return render_template("video.html", result=result)

@app.route("/video", methods=["GET", "POST"])
def video_page():
    if "user_email" not in session:
        flash("Login required", "warning")
        return redirect("/login")

    result = None

    if request.method == "POST":

        if "video" not in request.files:
            flash("No file part", "danger")
            return redirect("/video")

        file = request.files["video"]

        if file.filename == "":
            flash("Please select a video", "danger")
            return redirect("/video")

        # Replace spaces to avoid URL issues
        filename = file.filename.replace(" ", "_")

        # Save uploaded video
        upload_folder = os.path.join("static", "uploads", "videos")
        os.makedirs(upload_folder, exist_ok=True)

        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)

        # ✅ Analyze video
        analysis = analyze_video(save_path)
        analysis["video_filename"] = filename
        result = analysis

        # ✅ Read video bytes
        with open(save_path, "rb") as f:
            file_bytes = f.read()

        # ✅ Save to database safely
        save_media_file(
            filename=filename,
            file_type="video",
            file_bytes=file_bytes,
            verdict=analysis.get("verdict", "Unknown"),
            fake_score=analysis.get("fake_percent", analysis.get("fake_score", 0)),
            real_score=analysis.get("real_percent", analysis.get("real_score", 0)),
            uploaded_by=session["user_email"]
        )

    return render_template("video.html", result=result)

# =================================================
#              HISTORY PAGE
# =====================================================

@app.route("/history")
def history():

    if "user_email" not in session:
        flash("Login required to view history.", "warning")
        return redirect("/login")

    media = get_all_media()
    return render_template("history.html", media=media)


# =====================================================
#                  RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
