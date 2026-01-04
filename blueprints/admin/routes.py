# blueprints/admin/routes.py
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import FileStorage
from extensions import db, login_manager
from models import Product, Color, ProductImage, Order, User, Composition
from services.images import save_image
from . import bp

# Головна сторінка адмінки
@bp.route("/")
@login_required
def admin_index():
  return render_template("admin/index.html")

# Завантаження користувача для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Авторизація (Login)
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("admin.admin_index"))
        flash("Невірний логін або пароль")
    return render_template("admin/login.html")

# Вихід із системи (Logout)
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))

# Список товарів
@bp.route("/products")
@login_required
def product_list():
    products = Product.query.order_by(Product.name).all()
    return render_template("admin/product_list.html", products=products)

# Створення нового товару
@bp.route("/products/new", methods=["GET", "POST"])
@login_required
def product_new():
    if request.method == "POST":
        p = Product(
            sku=request.form["sku"],
            name=request.form["name"],
            description=request.form.get("description"),
            wax_type=request.form.get("wax_type"),
            category=request.form.get("category"),
            width=float(request.form.get("width") or 0),
            height=float(request.form.get("height") or 0),
            depth=float(request.form.get("depth") or 0),
            weight=float(request.form.get("weight") or 0),
            price=float(request.form.get("price") or 0),
            is_active=True
        )
        db.session.add(p); db.session.flush()

        # Автоматичний білий колір за замовчуванням, якщо кольори не додані вручну
        default_white = Color(product_id=p.id, color_name="Білий", color_hex="#FFFFFF", is_default=True, price_modifier=0.0)
        db.session.add(default_white)
        db.session.commit()
        return redirect(url_for("admin.product_edit", product_id=p.id))
    return render_template("admin/product_form.html", product=None, colors=[], images=[])

# Редагування товару
@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        product.sku = request.form.get("sku", product.sku)
        product.name = request.form.get("name", product.name)
        product.description = request.form.get("description", product.description)
        product.wax_type = request.form.get("wax_type", product.wax_type)
        product.category = request.form.get("category", product.category)
        product.width = float(request.form.get("width") or product.width or 0)
        product.height = float(request.form.get("height") or product.height or 0)
        product.depth = float(request.form.get("depth") or product.depth or 0)
        product.weight = float(request.form.get("weight") or product.weight or 0)
        product.price = float(request.form.get("price") or product.price or 0)
        product.is_active = bool(request.form.get("is_active"))
        db.session.commit()
        flash("Збережено")
    colors = Color.query.filter_by(product_id=product.id).all()
    images = ProductImage.query.filter_by(product_id=product.id).order_by(ProductImage.sort_order).all()
    return render_template("admin/product_form.html", product=product, colors=colors, images=images)

# Додавання кольору до товару
@bp.route("/products/<int:product_id>/colors/add", methods=["POST"])
@login_required
def color_add(product_id):
    is_default = bool(request.form.get("is_default"))
    price_modifier = float(request.form.get("price_modifier") or 0.0)
    if is_default:
        Color.query.filter_by(product_id=product_id, is_default=True).update({"is_default": False})
    c = Color(
        product_id=product_id,
        color_name=request.form["color_name"],
        color_hex=request.form["color_hex"],
        is_default=is_default,
        price_modifier=price_modifier
    )
    db.session.add(c); db.session.commit()
    return redirect(url_for("admin.product_edit", product_id=product_id))

# Видалення кольору
@bp.route("/colors/<int:color_id>/delete", methods=["POST"])
@login_required
def color_delete(color_id):
    c = Color.query.get_or_404(color_id)
    pid = c.product_id
    db.session.delete(c); db.session.commit()
    return redirect(url_for("admin.product_edit", product_id=pid))

# Додавання зображення до товару
@bp.route("/products/<int:product_id>/images/add", methods=["POST"])
@login_required
def image_add(product_id):
    file: FileStorage = request.files.get("image")
    alt = request.form.get("alt_text")
    sort_order = int(request.form.get("sort_order") or 0)
    if not file or not file.filename:
        flash("Файл зображення не надано")
        return redirect(url_for("admin.product_edit", product_id=product_id))
    try:
        filename, preview = save_image(file)
    except Exception as e:
        flash(f"Помилка завантаження: {e}")
        return redirect(url_for("admin.product_edit", product_id=product_id))
    img = ProductImage(product_id=product_id, filename=filename, preview_filename=preview, alt_text=alt, sort_order=sort_order)
    db.session.add(img); db.session.commit()
    return redirect(url_for("admin.product_edit", product_id=product_id))

# Видалення зображення
@bp.route("/images/<int:image_id>/delete", methods=["POST"])
@login_required
def image_delete(image_id):
    img = ProductImage.query.get_or_404(image_id)
    pid = img.product_id
    db.session.delete(img); db.session.commit()
    return redirect(url_for("admin.product_edit", product_id=pid))

# Список замовлень
@bp.route("/orders")
@login_required
def order_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/order_list.html", orders=orders)

# CRUD для Composition
@bp.route("/compositions")
@login_required
def composition_list():
    compositions = Composition.query.order_by(Composition.created_at.desc()).all()
    return render_template("admin/composition_list.html", compositions=compositions)

@bp.route("/compositions/new", methods=["GET", "POST"])
@login_required
def composition_new():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        file = request.files.get("image")
        filename = None
        if file and file.filename:
            try:
                filename, preview = save_image(file)
            except Exception as e:
                flash(f"Помилка завантаження: {e}")
        comp = Composition(title=title, description=description, image=filename, is_active=bool(request.form.get("is_active")))
        db.session.add(comp); db.session.commit()
        return redirect(url_for("admin.composition_list"))
    return render_template("admin/composition_form.html", composition=None)

@bp.route("/compositions/<int:comp_id>/edit", methods=["GET", "POST"])
@login_required
def composition_edit(comp_id):
    comp = Composition.query.get_or_404(comp_id)
    if request.method == "POST":
        comp.title = request.form.get("title", comp.title)
        comp.description = request.form.get("description", comp.description)
        comp.is_active = bool(request.form.get("is_active"))
        file = request.files.get("image")
        if file and file.filename:
            try:
                filename, preview = save_image(file)
                comp.image = filename
            except Exception as e:
                flash(f"Помилка завантаження: {e}")
        db.session.commit()
        return redirect(url_for("admin.composition_list"))
    return render_template("admin/composition_form.html", composition=comp)

@bp.route("/compositions/<int:comp_id>/delete", methods=["POST"])
@login_required
def composition_delete(comp_id):
    comp = Composition.query.get_or_404(comp_id)
    db.session.delete(comp); db.session.commit()
    return redirect(url_for("admin.composition_list"))