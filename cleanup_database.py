"""
Clean script: Delete all products from stores 2-5 (keep only 36 original from store 1)
"""
from app import create_app
from app.models.product import Product, ProductBatch
from app.models.order import Order, OrderItem
from app.extensions import db

def cleanup_database():
    app = create_app('development')
    
    with app.app_context():
        print("🗑️ Cleaning database...\n")
        
        # Get all products from stores 2-5
        products_to_delete = Product.query.filter(Product.store_id.in_([2, 3, 4, 5])).all()
        print(f"Found {len(products_to_delete)} products from stores 2-5 to delete\n")
        
        deleted_products = 0
        deleted_batches = 0
        deleted_order_items = 0
        deleted_orders = 0
        
        for product in products_to_delete:
            # Delete related OrderItems first
            order_items = OrderItem.query.filter_by(product_id=product.id).all()
            for item in order_items:
                db.session.delete(item)
                deleted_order_items += 1
            
            # Delete related ProductBatches
            batches = ProductBatch.query.filter_by(product_id=product.id).all()
            for batch in batches:
                db.session.delete(batch)
                deleted_batches += 1
            
            # Delete the product
            db.session.delete(product)
            deleted_products += 1
            print(f"✓ Deleted: {product.name} (store_id={product.store_id})")
        
        # Delete orders from stores 2-5
        orders_to_delete = Order.query.filter(Order.store_id.in_([2, 3, 4, 5])).all()
        for order in orders_to_delete:
            # Delete order items first
            for item in order.items:
                db.session.delete(item)
                deleted_order_items += 1
            db.session.delete(order)
            deleted_orders += 1
        
        db.session.commit()
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Deleted {deleted_products} products")
        print(f"   Deleted {deleted_batches} batches")
        print(f"   Deleted {deleted_orders} orders")
        print(f"   Deleted {deleted_order_items} order items")
        
        print(f"\n📊 Database now has:")
        print(f"   Products: {Product.query.count()}")
        print(f"   From store 1: {Product.query.filter_by(store_id=1).count()}")
        print(f"   ProductBatches: {ProductBatch.query.count()}")
        print(f"   Orders: {Order.query.count()}")

if __name__ == '__main__':
    cleanup_database()
