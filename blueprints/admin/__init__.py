# blueprints/admin/__init__.py
from flask import Blueprint

# Створюємо блупринт "admin", всі маршрути цього блупринта будуть починатися з /admin
bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

# Імпортуємо маршрути (routes.py), щоб вони зареєструвалися у Flask
from . import routes