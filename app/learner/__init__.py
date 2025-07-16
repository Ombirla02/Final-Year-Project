from flask import Blueprint

learner_bp = Blueprint('learner', __name__)

from . import routes