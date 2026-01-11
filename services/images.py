# services/images.py
import os, uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "static/img/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def save_image(file_storage):
    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError("Недопустиме розширення файлу")

    ext = filename.rsplit(".", 1)[1].lower()
    unique = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = ensure_upload_dir()
    original_path = os.path.join(upload_dir, secure_filename(unique))
    file_storage.save(original_path)

    # Створити прев’ю 200x200
    preview_name = f"preview_{unique}"
    preview_path = os.path.join(upload_dir, preview_name)
    with Image.open(original_path) as img:
        img = img.convert("RGB") if ext in ("jpg", "jpeg", "webp") else img
        img.thumbnail((200, 200))
        img.save(preview_path)

    return unique, preview_name