# blueprints/shop/__init__.py
from flask import Blueprint

# Створюємо блупринт "shop"
bp = Blueprint("shop", __name__, template_folder="templates")

# Імпортуємо маршрути (routes.py), щоб вони зареєструвалися у Flask
from . import routes