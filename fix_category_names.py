"""
Fix Vietnamese diacritics in category names.
Update "Banh kem" -> "Bánh kem", "Banh ngot" -> "Bánh ngọt"
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.product import Category

def fix_categories():
    """Fix Vietnamese category names."""
    app = create_app('development')
    
    with app.app_context():
        print("🔧 Fixing category names...\n")
        
        # Mapping of old names to new names
        replacements = {
            'Banh kem': 'Bánh kem',
            'Banh ngot': 'Bánh ngọt',
        }
        
        for old_name, new_name in replacements.items():
            category = Category.query.filter_by(name=old_name).first()
            if category:
                print(f"   ✓ '{old_name}' → '{new_name}'")
                category.name = new_name
            else:
                print(f"   ✗ '{old_name}' not found")
        
        db.session.commit()
        print("\n✅ Category names fixed!")
        
        # Verify
        print("\n📊 All categories:")
        categories = Category.query.order_by(Category.name).all()
        for cat in categories:
            print(f"   - {cat.name}")

if __name__ == '__main__':
    fix_categories()
