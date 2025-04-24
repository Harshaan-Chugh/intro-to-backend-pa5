from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

instructors_table = db.Table(
    "course_instructors",
    db.Model.metadata, # not a model in the traditional sense, not an object, just like old tables
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True)
)

students_table = db.Table(
    "course_students",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True)
)

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    
    assignments = db.relationship("Assignment", cascade="delete", backref="course")

    instructors = db.relationship("User", secondary=instructors_table, back_populates="instructor_courses")
    students = db.relationship("User", secondary=students_table, back_populates="student_courses")

    def __init__(self, **kwargs):
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")

    def serialize(self):
        """
        Serializes a course object, including its assignments, instructors,
        and students.
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.serialize() for a in self.assignments],
            "instructors": [i.serialize() for i in self.instructors],
            "students": [s.serialize() for s in self.students]
        }

    def simple_serialize(self):
        """
        A simpler serialization of a course.
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }

class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")

    def serialize(self, include_course=True):
        """
        Serializes an assignment. If include_course is True, the course details
        (shallow version) are added; otherwise, they are omitted.
        """
        data = {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date
        }
        if include_course and self.course:
            data["course"] = {
                "id": self.course.id,
                "code": self.course.code,
                "name": self.course.name
            }
        return data

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False, unique=True)

    instructor_courses = db.relationship("Course", secondary=instructors_table, back_populates="instructors")
    student_courses = db.relationship("Course", secondary=students_table, back_populates="students")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")

    def serialize(self):
        """
        Serializes a user object.        
        """
        data = {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }
        return data
    
    def simple_serialize(self):
        """
        Serializes a user object without course details.
        """
        data = {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }
        return data