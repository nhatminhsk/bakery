"""
Seed script: Assign placeholder images to products without images
"""
from app import create_app
from app.models.product import Product
from app.extensions import db

def seed_product_images():
    app = create_app('development')
    
    with app.app_context():
        # List of free placeholder image URLs
        placeholder_images = [
            'https://via.placeholder.com/400x300?text=Bánh+1',
            'https://via.placeholder.com/400x300?text=Bánh+2',
            'https://via.placeholder.com/400x300?text=Bánh+3',
            'https://via.placeholder.com/400x300?text=Bánh+4',
            'https://via.placeholder.com/400x300?text=Bánh+5',
            'https://via.placeholder.com/400x300?text=Bánh+6',
            'https://via.placeholder.com/400x300?text=Bánh+7',
            'https://via.placeholder.com/400x300?text=Bánh+8',
            'https://via.placeholder.com/400x300?text=Bánh+9',
            'https://via.placeholder.com/400x300?text=Bánh+10',
        ]
        
        print("🌱 Assigning placeholder images to products...\n")
        
        products_without_images = Product.query.filter(
            (Product.image_url == None) | (Product.image_url == '')
        ).all()
        
        print(f"Found {len(products_without_images)} products without images\n")
        
        updated_count = 0
        for i, product in enumerate(products_without_images):
            # Use rotating placeholder image
            placeholder = placeholder_images[i % len(placeholder_images)]
            product.image_url = placeholder
            updated_count += 1
            
            print(f"✓ {product.name}: assigned placeholder")
        
        db.session.commit()
        
        print(f"\n✅ Updated {updated_count} products with placeholder images!")
        
        # Verify
        with_image = Product.query.filter(
            (Product.image_url != None) & (Product.image_url != '')
        ).count()
        
        print(f"\n📊 Total products with images: {with_image}/{Product.query.count()}")

if __name__ == '__main__':
    seed_product_images()
