from flask import render_template, request, jsonify
import time
from flask_login import login_required
from app.home import home_bp
from app.auth.decorators import role_required

@home_bp.route("/", methods=["GET"])
@home_bp.route("/index", methods=["GET"])
def index():
    return render_template("index.html")

@home_bp.route("/lab", methods=["GET"])
def lab():
    return render_template("lab.html") 

request_counter = 0
current_time = time.time()
total_count = 0
@home_bp.route("/counter", methods=["GET"])
def counter():
    global request_counter, current_time, total_count
    now = time.time()
    elapsed = now - current_time
    current_time = now

    if elapsed > 0:
        rps = request_counter / elapsed
    else:
        rps = 0

    total_count += request_counter
    request_counter = 0

    return jsonify({"rps": round(rps, 2), "total_count": total_count})


@home_bp.route("/test", methods=["GET"])
def test():
    try:
        global request_counter
        request_counter += 1
        p1 = request.args.get("p1")

        return jsonify({"p1": p1})
    except Exception as e:
        return jsonify({"p1": p1})