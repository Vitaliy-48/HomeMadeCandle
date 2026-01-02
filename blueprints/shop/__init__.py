# blueprints/shop/__init__.py
from flask import Blueprint

bp = Blueprint(
    "shop",
    __name__,
    template_folder="templates"
)