"""
Seed fake orders and product reviews for stores 2-5 (HCMC, Da Nang, Can Tho, Hai Phong).
Creates diverse order data with different statuses, times, and customer reviews.
"""
import os
import sys
from random import choice, randint, sample
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User
from app.models.product import Product, ProductReview
from app.models.order import Order, OrderItem
from app.models.store import Store

# Vietnamese customer names
FIRST_NAMES = ['Nguyễn', 'Trần', 'Phạm', 'Hoàng', 'Võ', 'Bùi', 'Đặng', 'Dương', 'Lý', 'Phan']
LAST_NAMES = ['Anh', 'Bình', 'Cường', 'Dũng', 'Hà', 'Hưng', 'Khánh', 'Linh', 'Minh', 'Nam',
              'Phong', 'Quân', 'Rồng', 'Sơn', 'Tâm', 'Uyên', 'Vân', 'Xuân', 'Yến', 'Thanh']

# Vietnamese review comments
POSITIVE_REVIEWS = [
    "Sản phẩm rất tươi, ngon lắm! 😍",
    "Chất lượng tốt, giao hàng nhanh chóng",
    "Rất hài lòng với đơn hàng này",
    "Bánh rất ngon, sẽ mua lại",
    "Phục vụ tốt, giá hợp lý",
    "Sản phẩm giống hình, recommend 👍",
    "Tươi, ngon, giá cả phải chăng",
    "Giao đúng giờ, sản phẩm đẹp lắm",
]

NEUTRAL_REVIEWS = [
    "Sản phẩm bình thường, nhưng vẫn ổn",
    "Được, nhưng hơi tắt so với kỳ vọng",
    "Chất lượng trung bình",
    "Tạm được, giá hợp lý",
    "Không tệ, nhưng có thể tốt hơn",
]

NEGATIVE_REVIEWS = [
    "Sản phẩm không tươi như kỳ vọng",
    "Giao hàng chậm, sản phẩm kém",
    "Không bằng lần trước",
    "Chất lượng giảm sút",
]

ORDER_STATUSES = ['pending', 'confirmed', 'processing', 'delivered', 'cancelled']

def create_fake_customers(count=50):
    """Create fake customer accounts."""
    print(f"👥 Creating {count} fake customers...")
    existing_users = User.query.filter_by(role='customer').count()
    
    created = 0
    for i in range(count):
        username = f'customer_{existing_users + i + 1}'
        email = f'customer_{existing_users + i + 1}@bakery.local'
        
        # Check if already exists
        if User.query.filter_by(username=username).first():
            continue
        
        user = User(
            username=username,
            email=email,
            role='customer',
            is_active=True,
            phone=f'090{randint(10000000, 99999999)}',
            points=randint(0, 1000),
            rank=choice(['bronze', 'silver', 'gold', 'diamond'])
        )
        user.set_password('password123')
        db.session.add(user)
        created += 1
    
    db.session.commit()
    print(f"   ✅ Created {created} new customers (total: {existing_users + created})")
    return User.query.filter_by(role='customer').all()

def create_orders_for_store(store_id, num_orders=50):
    """Create fake orders for a store."""
    store = Store.query.get(store_id)
    print(f"\n📦 Creating {num_orders} orders for {store.name}...")
    
    customers = User.query.filter_by(role='customer').all()
    products = Product.query.filter_by(store_id=store_id).all()
    
    if not products:
        print(f"   ❌ No products found for store {store_id}")
        return
    
    created = 0
    for i in range(num_orders):
        # Random order time in past 90 days
        days_ago = randint(1, 90)
        order_time = datetime.utcnow() - timedelta(days=days_ago)
        
        customer = choice(customers)
        status = choice(ORDER_STATUSES)
        
        # Random 1-4 items per order
        order_items = sample(products, min(randint(1, 4), len(products)))
        
        total = 0
        order = Order(
            user_id=customer.id,
            store_id=store_id,
            status=status,
            shipping_fee=30000 if randint(0, 1) else 0,
            payment_method=choice(['cod', 'transfer', 'card']),
            created_at=order_time,
            updated_at=order_time,
        )
        
        # Add items to order
        for product in order_items:
            quantity = randint(1, 3)
            item_total = product.price * quantity
            total += item_total
            
            order_item = OrderItem(
                product_id=product.id,
                name=product.name,
                price=product.price,
                quantity=quantity,
                image_url=product.image_url,
            )
            order.items.append(order_item)
        
        order.total = total
        
        # Some delivered orders have paid_at
        if status == 'delivered' and randint(0, 1):
            order.paid_at = order_time + timedelta(hours=randint(1, 48))
        
        db.session.add(order)
        created += 1
    
    db.session.commit()
    print(f"   ✅ Created {created} orders for {store.name}")

def create_reviews_for_store(store_id):
    """Create product reviews for delivered orders in a store."""
    store = Store.query.get(store_id)
    print(f"\n⭐ Creating reviews for {store.name}...")
    
    # Get all delivered orders for this store
    delivered_orders = Order.query.filter_by(store_id=store_id, status='delivered').all()
    print(f"   Found {len(delivered_orders)} delivered orders")
    
    review_count = 0
    for order in delivered_orders:
        # 60% of delivered orders get reviewed
        if randint(0, 100) > 60:
            continue
        
        # Review 50-100% of items in the order
        items_to_review = sample(order.items, max(1, int(len(order.items) * randint(50, 100) / 100)))
        
        for item in items_to_review:
            # Check if review already exists
            existing = ProductReview.query.filter_by(
                order_id=order.id,
                user_id=order.user_id,
                product_id=item.product_id
            ).first()
            
            if existing:
                continue
            
            # Random rating: 70% high (4-5), 20% medium (3), 10% low (1-2)
            rand = randint(0, 100)
            if rand < 70:
                rating = randint(4, 5)
                comment = choice(POSITIVE_REVIEWS)
            elif rand < 90:
                rating = 3
                comment = choice(NEUTRAL_REVIEWS)
            else:
                rating = randint(1, 2)
                comment = choice(NEGATIVE_REVIEWS)
            
            review = ProductReview(
                order_id=order.id,
                user_id=order.user_id,
                product_id=item.product_id,
                rating=rating,
                comment=comment,
                created_at=order.updated_at + timedelta(hours=randint(2, 72))
            )
            db.session.add(review)
            review_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {review_count} reviews")

def seed_all():
    """Main seeding function."""
    app = create_app('development')
    
    with app.app_context():
        print("🌱 Seeding orders and reviews for stores 2-5...\n")
        
        # Create fake customers first
        customers = create_fake_customers(50)
        print(f"   Total customers: {len(customers)}")
        
        # Create orders for stores 2-5
        target_stores = [2, 3, 4, 5]
        for store_id in target_stores:
            store = Store.query.get(store_id)
            if not store:
                print(f"❌ Store {store_id} not found!")
                continue
            
            create_orders_for_store(store_id, num_orders=50)
        
        # Create reviews for delivered orders
        print("\n📊 Creating reviews for delivered orders...")
        for store_id in target_stores:
            create_reviews_for_store(store_id)
        
        # Verify
        print("\n✅ Verification:")
        for store_id in target_stores:
            orders_count = Order.query.filter_by(store_id=store_id).count()
            reviews_count = db.session.query(ProductReview).join(
                Order, Order.id == ProductReview.order_id
            ).filter(Order.store_id == store_id).count()
            store = Store.query.get(store_id)
            print(f"   {store.name}: {orders_count} orders, {reviews_count} reviews")
        
        total_orders = Order.query.filter(Order.store_id.in_(target_stores)).count()
        total_reviews = db.session.query(ProductReview).join(
            Order, Order.id == ProductReview.order_id
        ).filter(Order.store_id.in_(target_stores)).count()
        
        print(f"\n📈 Total for stores 2-5:")
        print(f"   Orders: {total_orders}")
        print(f"   Reviews: {total_reviews}")
        print(f"\n✨ Seeding completed successfully!")

if __name__ == '__main__':
    seed_all()
