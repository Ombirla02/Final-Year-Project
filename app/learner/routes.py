from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user
from bson import ObjectId
from app.learner import learner_bp
from config.dbconnect import DatabaseConnection
db = DatabaseConnection().connection


@learner_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("learner_dashboard.html")

@learner_bp.route("/internship")
@login_required
def internship():
    return render_template("internship.html")

@learner_bp.route("/courses")
@login_required
def courses():
    all_courses = list(db.courses.find({}))

    user_data = db.users.find_one({"email": current_user.get_id()})
    enrolled_courses = []
    if user_data:
        enrolled_course_ids = user_data.get("enrolled_courses", [])
        enrolled_courses = [course for course in all_courses if str(course["_id"]) in enrolled_course_ids]

    return render_template("courses.html", all_courses=all_courses, enrolled_courses=enrolled_courses)


@learner_bp.route("/courses/enroll/<course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    # Ensure course_id is a valid ObjectId ( NO wow )
    try:
        course_id = course_id
    except:
        flash("Invalid course ID!", "error")
        return redirect(url_for("learner.courses"))

    # Find user by email (since email is used as the unique identifier)
    user = db.users.find_one({"email": current_user.get_id()})
    if not user:
        flash("User not found!", "error")
        return redirect(url_for("auth.login"))

    db.users.update_one({"email": current_user.get_id()}, {"$addToSet": {"enrolled_courses": course_id}})
    flash("Successfully enrolled!", "success")
    return redirect(url_for("learner.courses"))

@learner_bp.route("/course/<course_id>")
@login_required
def course_detail(course_id):
    try:
        course_id = ObjectId(course_id)
    except:
        flash("Invalid course ID!", "danger")
        return redirect(url_for("learner.dashboard"))

    course = db.courses.find_one({"_id": course_id})
    if not course:
        flash("Course not found!", "danger")
        return redirect(url_for("learner.dashboard"))

    # Fetching modules related to this course and sorting by order
    module_ids = [ObjectId(module_id) for module_id in course.get("modules", [])]
    modules = list(db.modules.find({"_id": {"$in": module_ids}}).sort("order", 1))

    return render_template("course.html", course=course, modules=modules)

@learner_bp.route("/module/<module_id>")
@login_required
def module_detail(module_id):
    try:
        module_id = ObjectId(module_id)
    except:
        flash("Invalid module ID!", "danger")
        return redirect(url_for("learner.dashboard"))

    module = db.modules.find_one({"_id": module_id})
    if not module:
        flash("Module not found!", "danger")
        return redirect(url_for("learner.dashboard"))

    return render_template("module.html", module=module)

@learner_bp.route("/profile")
@login_required
def profile():
    user_data = {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "certifications": db.certifications.find({"user_id": current_user.id})  # Fetch user's certifications
    }
    return render_template("profile.html", user=user_data)
