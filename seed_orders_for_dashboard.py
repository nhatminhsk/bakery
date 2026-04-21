"""
Seed script: Create fake orders for stores 2, 3, 4, 5
- Create 50-60 customers
- Create 50-80 orders per store (stores 2, 3, 4, 5)
- Each order has 1-5 items
- Random statuses: pending, confirmed, processing, delivered, cancelled
- created_at: random dates in April 2026
"""
from datetime import datetime, timedelta, timezone
from app import create_app
from app.models.user import User
from app.models.store import Store
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.extensions import db, bcrypt
import random

# UTC+7 timezone
LOCAL_TIMEZONE = timezone(timedelta(hours=7))

def seed_orders():
    app = create_app('development')
    
    with app.app_context():
        print("🌱 Creating fake orders for dashboard...\n")
        
        # Create customers (users with role='customer')
        print("👥 Creating customers...")
        customer_names = [
            'Nguyễn Văn A', 'Trần Thị B', 'Phạm Minh C', 'Hoàng Hồng D', 'Bùi Tấn E',
            'Đặng Huy F', 'Vũ Linh G', 'Tô Quý H', 'Dương Kiều I', 'Lê Tuấn J',
            'Nông Tú K', 'Lâm Khánh L', 'Trương Thiên M', 'Hứa Minh N', 'Quách Anh O',
            'Công Khôi P', 'Lã Đức Q', 'Từ Hiệu R', 'Thiều Tuân S', 'Phùng Phương T',
            'Vương Tuấn U', 'Hạnh Hạ V', 'Diệu Minh W', 'Kiều Trang X', 'Thảo Vân Y',
            'Hương Chi Z', 'Mai Linh AA', 'Thu Hương AB', 'Như Quỳnh AC', 'Xuân Hoa AD',
            'Hoa Cúc AE', 'Mỹ Linh AF', 'Thanh Hoa AG', 'Quỳnh Giang AH', 'Anh Tuấn AI',
            'Bình Minh AJ', 'Chí Thành AK', 'Danh Thắng AL', 'Elong AM', 'Fung Chi AN',
            'Gia Hân AO', 'Hoàng Nam AP', 'Ích Đức AQ', 'Jughead AR', 'Khanyi AS',
            'Linh Chi AT', 'Mạnh Tuấn AU', 'Ngọc Bảo AV', 'Oanh Yến AW', 'Phương Anh AX',
            'Quân Lực AY', 'Rồng Anh AZ', 'Sơn Tùng BA', 'Tâm Giang BB', 'Uyên Vy BC',
        ]
        
        customers = []
        for i, name in enumerate(customer_names[:50]):
            username = f'customer_{i+1:02d}'
            email = f'customer{i+1}@example.com'
            
            # Check if customer exists
            existing = User.query.filter_by(username=username).first()
            if existing:
                customers.append(existing)
            else:
                user = User(
                    username=username,
                    email=email,
                    role='customer',
                    is_active=True,
                    phone=f'090{random.randint(10000000, 99999999)}',
                    points=random.randint(0, 5000),
                    rank=random.choice(['bronze', 'silver', 'gold', 'diamond'])
                )
                user.set_password('password')
                db.session.add(user)
                customers.append(user)
        
        db.session.commit()
        print(f"   ✓ {len(customers)} customers ready\n")
        
        # Create orders for stores 2, 3, 4, 5
        statuses = ['pending', 'confirmed', 'processing', 'delivered', 'cancelled']
        payment_methods = ['cod', 'bank_transfer', 'credit_card', 'momo']
        
        total_orders = 0
        
        for store in Store.query.filter(Store.id.in_([2, 3, 4, 5])).all():
            print(f"📦 Creating orders for {store.name}...")
            
            # Get products for this store
            products = Product.query.filter_by(store_id=store.id).all()
            if not products:
                print(f"   ❌ No products for {store.name}")
                continue
            
            # Create 50-80 orders
            num_orders = random.randint(50, 80)
            
            for order_num in range(num_orders):
                # Random date in April 2026
                day = random.randint(1, 30)
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                
                created_at = datetime(2026, 4, day, hour, minute, 0, tzinfo=LOCAL_TIMEZONE)
                
                # Random customer
                customer = random.choice(customers)
                
                # Create order
                order = Order(
                    user_id=customer.id,
                    store_id=store.id,
                    status=random.choice(statuses),
                    shipping_fee=random.choice([0, 25000, 35000, 50000]),
                    payment_method=random.choice(payment_methods),
                    created_at=created_at,
                    updated_at=created_at,
                )
                
                # Add 1-5 items to order
                num_items = random.randint(1, 5)
                selected_products = random.sample(products, min(num_items, len(products)))
                
                order_total = 0
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    price = product.price
                    
                    item = OrderItem(
                        product_id=product.id,
                        name=product.name,
                        price=price,
                        quantity=quantity,
                        image_url=product.image_url,
                    )
                    order.items.append(item)
                    order_total += price * quantity
                
                order.total = order_total
                
                # Mark as paid if delivered or confirmed
                if order.status in ['delivered', 'confirmed']:
                    order.paid_at = created_at
                
                db.session.add(order)
                total_orders += 1
                
                if (order_num + 1) % 20 == 0:
                    print(f"   ✓ {order_num + 1}/{num_orders} orders created")
            
            print(f"   ✓ {num_orders} orders for {store.name}\n")
        
        db.session.commit()
        
        print(f"✅ Successfully created {total_orders} orders!")
        print("\n📊 Orders by store:")
        for store in Store.query.filter(Store.id.in_([2, 3, 4, 5])).all():
            count = Order.query.filter_by(store_id=store.id).count()
            total = sum(o.total for o in Order.query.filter_by(store_id=store.id).all())
            print(f"   {store.name}: {count} orders, {total:,} VND total")

if __name__ == '__main__':
    seed_orders()
