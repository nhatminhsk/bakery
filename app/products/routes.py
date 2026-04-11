from flask import Blueprint, render_template, request
from app.products.services import (
    get_all_products,
    get_categories,
    get_product_by_id,
    get_product_reviews,
    search_products,
)

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def index():
    selected_category = request.args.get('category', '').strip()
    products = get_all_products(category=selected_category)
    categories = get_categories()

    return render_template('index.html',
                           products=products,
                           categories=categories,
                           selected_category=selected_category)


@products_bp.route('/products')
def product_list():
    return index()


@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return render_template('404.html'), 404

    related = get_all_products(category=product.category, exclude_id=product_id, limit=4)
    product_reviews = get_product_reviews(product_id)
    return render_template(
        'product_detail.html',
        product=product,
        related_products=related,
        product_reviews=product_reviews,
    )


@products_bp.route('/search')
def search():
    query   = request.args.get('q', '').strip()
    results = search_products(query) if query else []
    return render_template('search.html', query=query, results=results)
