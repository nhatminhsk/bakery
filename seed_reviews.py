"""
Seed product reviews with ratings and Vietnamese comments
"""
from datetime import datetime, timedelta, timezone
from app import create_app
from app.models.user import User
from app.models.order import Order
from app.models.product import Product, ProductReview
from app.extensions import db
import random

# Vietnam timezone (UTC+7)
VN_OFFSET = timezone(timedelta(hours=7))

# Vietnamese review comments by rating
REVIEWS_BY_RATING = {
    5: [
        'Tuyệt vời! Bánh rất ngon, tươi và không bị khô. Sẽ mua lại!',
        'Chất lượng xuất sắc, hương vị tuyệt hảo. Rất hài lòng!',
        'Bánh ngon, đóng gói cẩn thận. Giao hàng nhanh chóng!',
        'Ưng ý lắm! Bánh mềm, kem thơm, đúng chuẩn!',
        'Quá tuyệt vời, vị ngon tuyệt cú mèo! Sẽ mua tiếp!',
        'Hài lòng tuyệt đối! Chất lượng thực sự rất cao!',
        'Bánh siêu ngon, ăn rất thoả mãn! Mua lại ngay!',
    ],
    4: [
        'Rất ngon, chỉ tiếc là hơi hạn sử dụng sớm.',
        'Tốt lắm, kem mềm, hương vị chuẩn. Có thể nâng cấp một chút.',
        'Hầu như hoàn hảo, chỉ cần thêm một ít gì đó.',
        'Chất lượng tốt, bánh ngon. Giao hàng ổn định!',
        'Sản phẩm đạt tiêu chuẩn, rất hài lòng về chất lượng.',
        'Ngon, mềm, thơm. Có thể nâng cấp về phủ bên ngoài.',
    ],
    3: [
        'Bình thường, không quá đặc biệt nhưng cũng chấp nhận được.',
        'Có thể tốt hơn. Vị ok nhưng thiếu chút độ sánh ngoài.',
        'Trung bình thôi, không quá tuyệt vời cũng không tệ.',
        'Còn được, nhưng so với mức giá thì hơi mắc.',
        'Ổn thôi, bánh mềm nhưng kem hơi ngọt.',
        'Bình thường, có những sản phẩm khác tốt hơn.',
    ],
    2: [
        'Không tốt như kỳ vọng. Bánh hơi khô.',
        'Chất lượng thấp hơn lần trước. Không rất thích.',
        'Kem hơi ngứa, bánh không mềm lắm.',
        'Trừ một sao vì giao hàng bị chậm.',
        'Không đúng mong đợi, chất lượng có vấn đề.',
        'Hơi thất vọng. Sẽ thử sản phẩm khác lần tới.',
    ],
    1: [
        'Rất thất vọng! Bánh không ngon, kem bị chảy.',
        'Chất lượng kém, không đáng giá tiền.',
        'Không thích, bánh cũ, không tươi.',
        'Tệ! Giao hàng bị hỏng, bánh không ăn được.',
        'Rất thất vọng về chất lượng sản phẩm.',
        'Không thể chấp nhận được, đòi tiền lại!',
    ],
}

def seed_reviews():
    app = create_app('development')
    with app.app_context():
        print('🌱 Seeding product reviews...\n')
        
        # Get customer users
        customers = User.query.filter_by(role='customer').all()
        if not customers:
            print('❌ No customer users found')
            return
        
        print(f'Found {len(customers)} customers\n')
        
        # Get all orders
        orders = Order.query.all()
        if not orders:
            print('❌ No orders found')
            return
        
        print(f'Found {len(orders)} orders\n')
        
        # Get all products
        products = Product.query.all()
        if not products:
            print('❌ No products found')
            return
        
        print(f'Found {len(products)} products\n')
        
        total_reviews = 0
        reviews_by_store = {}
        
        # Create reviews for random products in orders
        for order in orders:
            # 40% chance to create a review for this order
            if random.random() > 0.4:
                continue
            
            # Get a random customer (usually the order creator)
            customer = random.choice(customers)
            
            # Get 1-3 random products to review
            num_products = random.randint(1, 3)
            selected_products = random.sample(products, min(num_products, len(products)))
            
            for product in selected_products:
                # Check if review already exists (unique constraint)
                existing = ProductReview.query.filter_by(
                    order_id=order.id,
                    user_id=customer.id,
                    product_id=product.id
                ).first()
                
                if existing:
                    continue
                
                # Random rating 1-5, weighted towards higher ratings
                rating = random.choices(
                    [5, 4, 3, 2, 1],
                    weights=[40, 30, 15, 10, 5]
                )[0]
                
                # Get comment for this rating
                comment = random.choice(REVIEWS_BY_RATING[rating])
                
                # Random review date (within 7 days after order)
                review_date = order.created_at + timedelta(days=random.randint(1, 7))
                
                review = ProductReview(
                    order_id=order.id,
                    user_id=customer.id,
                    product_id=product.id,
                    rating=rating,
                    comment=comment,
                    created_at=review_date,
                    updated_at=review_date,
                )
                db.session.add(review)
                total_reviews += 1
                
                # Track by store
                store_id = product.store_id
                if store_id not in reviews_by_store:
                    reviews_by_store[store_id] = 0
                reviews_by_store[store_id] += 1
        
        db.session.commit()
        
        # Update product ratings based on average of reviews
        print('📊 Updating product ratings...')
        
        products_updated = 0
        for product in products:
            reviews = ProductReview.query.filter_by(product_id=product.id).all()
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                product.rating = round(avg_rating, 1)
                products_updated += 1
        
        db.session.commit()
        
        # Summary
        print(f'\n✅ Seeding complete!')
        print(f'\n📈 Statistics:')
        print(f'  Total reviews created: {total_reviews}')
        print(f'  Products with reviews: {products_updated}')
        print(f'\n🏪 Reviews by store:')
        
        from app.models.store import Store
        for store_id, count in sorted(reviews_by_store.items()):
            store = Store.query.get(store_id)
            store_name = store.name if store else f'Store {store_id}'
            print(f'  - {store_name}: {count} reviews')
        
        print(f'\n⭐ Product ratings updated:')
        for product in products[:10]:
            if product.rating > 0:
                stars = '⭐' * int(product.rating) + '✨' * (5 - int(product.rating))
                print(f'  {product.name}: {product.rating}/5 {stars}')

if __name__ == '__main__':
    seed_reviews()
