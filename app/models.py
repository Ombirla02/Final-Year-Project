from flask_login import UserMixin
from config.dbconnect import DatabaseConnection
db = DatabaseConnection().connection
class User(UserMixin):
    def __init__(self, username, email, password, role, enrolled_courses=None, certifications=None):
        self.username = username
        self.email = email
        self.password = password
        self.role = role  # Can be "learner", "industry_professional", or "supervisor"
        self.enrolled_courses = enrolled_courses if enrolled_courses is not None else []
        self.certifications = certifications if certifications is not None else []

    def get_id(self):
        return str(self.email)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "enrolled_courses": self.enrolled_courses,
            "certifications": self.certifications,
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            role=data["role"],
            enrolled_courses=data.get("enrolled_courses", []),
            certifications=data.get("certifications", []),
        )

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, role={self.role})"