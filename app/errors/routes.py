from flask import Flask, render_template
from app.errors import error_bp

@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@error_bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template("403.html"), 403