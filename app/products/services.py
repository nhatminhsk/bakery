from app.models.product import Product, Category


def get_all_products(category=None, exclude_id=None, limit=None):
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if exclude_id:
        query = query.filter(Product.id != exclude_id)
    if limit:
        query = query.limit(limit)
    return query.all()


def get_product_by_id(product_id):
    return Product.query.get(product_id)


def search_products(keyword):
    pattern = f'%{keyword}%'
    return Product.query.filter(
        Product.name.ilike(pattern) | Product.description.ilike(pattern)
    ).order_by(Product.name).all()


def get_categories():
    return Category.query.order_by(Category.name).all()
