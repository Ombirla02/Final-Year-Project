# app.py (or wherever your main Flask app creation file is)

import os
from flask import Flask
from flask_login import LoginManager, UserMixin
from dotenv import load_dotenv
from pymongo import MongoClient # Assuming DatabaseConnection uses PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
# This should be called at the very beginning to ensure variables are available
load_dotenv()

# --- Database Connection ---
# It's assumed that config.dbconnect.DatabaseConnection handles the actual
# connection logic to MongoDB using pymongo.
# The 'connection' attribute should return a PyMongo database object (e.g., client.mydatabase).
try:
    # Attempt to establish the database connection globally.
    # If MongoDB is not running, this line will raise the ECONNREFUSED error.
    # Ensure your MongoDB server is running before starting the Flask app.
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/your_database_name"))
    db = client.get_database() # Get the default database from the URI or specify one
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    print("Please ensure your MongoDB server is running and accessible.")
    # Depending on your deployment strategy, you might want to exit here
    # or handle the error more gracefully (e.g., retry logic).
    db = None # Set db to None if connection fails

# --- Flask-Login Manager ---
login_manager = LoginManager()
# Set the view name for the login page. Flask-Login will redirect here
# if an unauthenticated user tries to access a protected page.
login_manager.login_view = "auth.login"

# --- Secret Key for Flask Session Management ---
# It's crucial for security; load it from environment variables.
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("SECRET_KEY environment variable not set. Please set it for security.")

# --- User Model (Example - you would have this in app/models.py) ---
# This is a placeholder for your User model, which Flask-Login needs.
# It should inherit from UserMixin.
class User(UserMixin):
    def __init__(self, id, email, password_hash, role):
        self.id = str(id)  # MongoDB _id is ObjectId, convert to string for Flask-Login
        self.email = email
        self.password_hash = password_hash
        self.role = role # e.g., 'learner', 'supervisor', 'industry'

    def get_id(self):
        """Return the user ID for Flask-Login."""
        return self.id

    @staticmethod
    def from_dict(data):
        """Create a User instance from a dictionary (MongoDB document)."""
        if data:
            return User(
                id=data.get('_id'),
                email=data.get('email'),
                password_hash=data.get('password_hash'),
                role=data.get('role')
            )
        return None

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


# --- Flask Application Factory Function ---
def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, template_folder='templates')
    # Configure the secret key for session management.
    app.config['SECRET_KEY'] = secret_key

    # Initialize Flask-Login with the Flask app instance.
    login_manager.init_app(app)

    # --- User Loader for Flask-Login ---
    # This function tells Flask-Login how to load a user from the user ID
    # stored in the session.
    @login_manager.user_loader
    def load_user(user_id):
        """
        Loads a user object from the database based on their user_id.

        Args:
            user_id (str): The ID of the user to load.

        Returns:
            User: The User object if found, otherwise None.
        """
        # Ensure db connection is available before querying
        if db:
            # MongoDB's _id is often an ObjectId, so we need to import it
            # if we're querying by ObjectId. Assuming user_id is a string
            # representation of the ObjectId.
            from bson.objectid import ObjectId
            try:
                user_data = db.users.find_one({"_id": ObjectId(user_id)})
                if user_data:
                    return User.from_dict(user_data)
            except Exception as e:
                print(f"Error loading user {user_id}: {e}")
        return None

    # --- Import and Register Blueprints ---
    # Blueprints organize your application into smaller, reusable components.
    from app.home import home_bp
    from app.auth import auth
    from app.learner import learner_bp
    from app.supervisor import supervisor_bp
    from app.industry import industry_bp
    from app.errors import error_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(learner_bp, url_prefix='/learner')
    app.register_blueprint(supervisor_bp, url_prefix='/supervisor')
    app.register_blueprint(industry_bp, url_prefix='/industry')
    app.register_blueprint(error_bp)

    return app

# Example of how to run the app (typically in run.py or wsgi.py)
if __name__ == '__main__':
    # This block is for development purposes.
    # In production, use a WSGI server like Gunicorn or uWSGI.
    app = create_app()
    app.run(debug=True) # debug=True enables reloader and debugger