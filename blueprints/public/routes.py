# blueprints/public/routes.py
from flask import render_template
from models import Product, Composition
from blueprints.public import bp


@bp.route("/")
def index():
    compositions = Composition.query.filter_by(is_active=True).order_by(Composition.created_at.desc()).all()
    return render_template("public/index.html", compositions=compositions)


@bp.route("/compositions")
def compositions():
    compositions = Composition.query.filter_by(is_active=True).order_by(Composition.created_at.desc()).all()
    return render_template("public/compositions.html", compositions=compositions)

@bp.route("/faq")
def faq():
    return render_template("public/faq.html")

@bp.route("/catalog")
def catalog():
    products = Product.query.filter_by(is_active=True).all()
    return render_template("public/catalog.html", products=products)

@bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    colors = [c.to_dict() for c in product.colors]
    return render_template("public/product_detail.html", product=product, colors=colors)