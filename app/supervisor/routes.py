from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import cv2
import os
from bson import ObjectId
from flask_login import login_required
from app.auth.decorators import role_required
from app.supervisor import supervisor_bp
from config.dbconnect import DatabaseConnection
db = DatabaseConnection().connection
users_collection = db.users

def generate_certificates(name, course_id):
    base_dir = current_app.root_path
    template_path = os.path.join(base_dir, "static", "images", "certificate-template.jpg")
    output_dir = os.path.join(base_dir, "static", "generated-certificates")
    
    os.makedirs(output_dir, exist_ok=True)

    certificate_template_image = cv2.imread(template_path)
    if certificate_template_image is None:
        raise FileNotFoundError("Template image not found at path: " + template_path)

    cv2.putText(certificate_template_image, name.strip(), (815, 1500),
                cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 250), 5, cv2.LINE_AA)

    output_filename = f"{name.strip()}_{course_id.strip()}.jpg"
    output_path = os.path.join(output_dir, output_filename)
    cv2.imwrite(output_path, certificate_template_image)


@supervisor_bp.route("/dashboard")
@login_required
@role_required(["supervisor"])
def dashboard():
    return render_template("supervisor_dashboard.html")

@supervisor_bp.route("/certificate/approval", methods=["GET", "POST"])
@login_required
@role_required(["supervisor"])
def certificate_approval():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        course_id = request.form.get("course_id")

        if user_id and course_id:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"certifications": course_id}}
            )
            generate_certificates(request.form.get("username"), course_id)
            flash("Certificate granted successfully!", "success")
        return redirect(url_for("supervisor.certificate_approval"))
    
    course_docs = db.courses.find({}, {"_id": 1, "title": 1})
    course_map = {str(course["_id"]): course["title"] for course in course_docs}

    eligible_users = list(users_collection.aggregate([
        {
            "$match": {
                "course_progress": {
                    "$elemMatch": {
                        "completed": True,
                        "requested_certificate": True
                    }
                }
            }
        },
        {
            "$project": {
                "username": 1,
                "email": 1,
                "matching_courses": {
                    "$filter": {
                        "input": "$course_progress",
                        "as": "course",
                        "cond": {
                            "$and": [
                                { "$eq": ["$$course.completed", True] },
                                { "$eq": ["$$course.requested_certificate", True] }
                            ]
                        }
                    }
                }
            }
        },
        {
            "$unwind": "$matching_courses"
        },
        {
            "$project": {
                "user_id": "$_id",
                "username": 1,
                "email": 1,
                "course_id": "$matching_courses.course_id"
            }
        }
    ]))

    for entry in eligible_users:
        course_id = entry["course_id"]
        entry["course_title"] = course_map.get(course_id, "Unknown Title")


    return render_template("certificate_approval.html", eligible_entries=eligible_users)


