from flask import Blueprint

industry_bp = Blueprint('industry', __name__)

from . import routes