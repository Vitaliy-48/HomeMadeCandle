# blueprints/public/__init__.py
from flask import Blueprint


bp = Blueprint("public", __name__, template_folder='templates')
print(bp)
from . import routes