import json
from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from db import db, Course, User, Assignment

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def course_stub(course):
    """
    Return a minimal representation of a course.
    """
    return {"id": course.id, "code": course.code, "name": course.name}


def format_assignment(assignment):
    """
    Return a serialized assignment with its course stub.
    """
    return {
        "id": assignment.id,
        "title": assignment.title,
        "due_date": assignment.due_date,
        "course": course_stub(assignment.course) if assignment.course else None,
    }


def format_course(course):
    """
    Return a serialized course with instructors, students, and assignments.
    """
    return {
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "instructors": [u.simple_serialize() for u in course.instructors],
        "students": [u.simple_serialize() for u in course.students],
        "assignments": [format_assignment(a) for a in course.assignments],
    }


def format_user(user):
    """
    Return a serialized user with enrolled and instructed courses.
    """
    courses = [c.simple_serialize() for c in user.student_courses] + [c.simple_serialize() for c in user.instructor_courses]
    return {"id": user.id, "name": user.name, "netid": user.netid, "courses": courses}

@app.route("/api/", methods=["GET"])
def hello():
    """
    Return a simple hello message.
    """
    return json.dumps({"message": "Hello world"}), 200, {"Content-Type": "application/json"}

@app.route("/api/courses/", methods=["GET"])
def get_all_courses():
    """
    Retrieve and return all courses.
    """
    return json.dumps({"courses": [format_course(c) for c in Course.query.all()]}), 200, {"Content-Type": "application/json"}

@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Create a new course with given code and name.
    """
    data = request.get_json(force=True) or {}
    code, name = data.get("code"), data.get("name")
    if not code or not name:
        return json.dumps({"error": "Course 'code' and 'name' are required."}), 400, {"Content-Type": "application/json"}

    course = Course(code=code, name=name)
    db.session.add(course)
    db.session.commit()
    return json.dumps(format_course(course)), 201, {"Content-Type": "application/json"}

@app.route("/api/courses/<int:course_id>/", methods=["GET"])
def get_course(course_id):
    """
    Retrieve and return a course by its ID.
    """
    course = Course.query.get(course_id)
    if not course:
        return json.dumps({"error": "Course not found."}), 404, {"Content-Type": "application/json"}
    return json.dumps(format_course(course)), 200, {"Content-Type": "application/json"}

@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Delete a course by its ID and return it.
    """
    course = Course.query.get(course_id)
    if not course:
        return json.dumps({"error": "Course not found."}), 404, {"Content-Type": "application/json"}
    db.session.delete(course)
    db.session.commit()
    return json.dumps(format_course(course)), 200, {"Content-Type": "application/json"}

@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    """
    Add a user as student or instructor to a course.
    """
    data = request.get_json(force=True) or {}
    if "user_id" not in data or "type" not in data:
        return json.dumps({"error": "Both 'user_id' and 'type' are required."}), 400, {"Content-Type": "application/json"}

    course = Course.query.get(course_id)
    if not course:
        return json.dumps({"error": "Course not found."}), 404, {"Content-Type": "application/json"}

    user = User.query.get(data["user_id"])
    if not user:
        return json.dumps({"error": "User not found."}), 404, {"Content-Type": "application/json"}

    role = data["type"]
    if role not in {"student", "instructor"}:
        return json.dumps({"error": "Type must be either 'student' or 'instructor'."}), 400, {"Content-Type": "application/json"}

    collection = course.students if role == "student" else course.instructors
    if user not in collection:
        collection.append(user)
        db.session.commit()

    return json.dumps(format_course(course)), 200, {"Content-Type": "application/json"}

@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Create an assignment for a specific course.
    """
    data = request.get_json(force=True) or {}
    title, due_date = data.get("title"), data.get("due_date")
    if not title or due_date is None:
        return json.dumps({"error": "Both 'title' and 'due_date' are required."}), 400, {"Content-Type": "application/json"}

    course = Course.query.get(course_id)
    if not course:
        return json.dumps({"error": "Course not found."}), 404, {"Content-Type": "application/json"}

    assignment = Assignment(title=title, due_date=due_date, course_id=course.id)
    db.session.add(assignment)
    db.session.commit()
    return json.dumps(format_assignment(assignment)), 201, {"Content-Type": "application/json"}

@app.route("/api/users/", methods=["GET"])
def list_users():
    """
    Retrieve and return all users.
    """
    return json.dumps({"users": [u.simple_serialize() for u in User.query.all()]}), 200, {"Content-Type": "application/json"}

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Create a new user with given name and netid.
    """
    data = request.get_json(force=True) or {}
    name, netid = data.get("name"), data.get("netid")
    if not name or not netid:
        return json.dumps({"error": "User 'name' and 'netid' are required."}), 400, {"Content-Type": "application/json"}

    user = User(name=name, netid=netid)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        existing = User.query.filter_by(netid=netid).first()
        if existing:
            return json.dumps(existing.simple_serialize()), 201, {"Content-Type": "application/json"}
        return json.dumps({"error": "User 'netid' must be unique."}), 400, {"Content-Type": "application/json"}

    return json.dumps(user.simple_serialize()), 201, {"Content-Type": "application/json"}

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Retrieve and return a user by its ID.
    """
    user = User.query.get(user_id)
    if not user:
        return json.dumps({"error": "User not found."}), 404, {"Content-Type": "application/json"}
    return json.dumps(format_user(user)), 200, {"Content-Type": "application/json"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
