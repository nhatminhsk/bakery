"""add product batches and reviews

Revision ID: b7c9a8d4e2f1
Revises: 8c572639720b
Create Date: 2026-04-07 15:30:00.000000

"""
from datetime import datetime, timedelta
import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c9a8d4e2f1'
down_revision = '8c572639720b'
branch_labels = None
depends_on = None


def _safe_parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return None
    return None


def _import_legacy_reviews(bind):
    project_root = Path(__file__).resolve().parents[2]
    legacy_path = project_root / 'data' / 'product_reviews.json'

    if not legacy_path.exists():
        return

    try:
        payload = json.loads(legacy_path.read_text(encoding='utf-8'))
    except Exception:
        return

    if not isinstance(payload, list) or not payload:
        return

    existing_count = bind.execute(sa.text('SELECT COUNT(1) FROM product_reviews')).scalar() or 0
    if existing_count > 0:
        return

    valid_user_ids = {
        row[0] for row in bind.execute(sa.text('SELECT id FROM users')).fetchall()
    }
    valid_product_ids = {
        row[0] for row in bind.execute(sa.text('SELECT id FROM products')).fetchall()
    }
    valid_order_ids = {
        row[0] for row in bind.execute(sa.text('SELECT id FROM orders')).fetchall()
    }

    insert_sql = sa.text(
        """
        INSERT INTO product_reviews (
            order_id, user_id, product_id, rating, comment,
            admin_reply, admin_reply_at, created_at, updated_at
        )
        VALUES (
            :order_id, :user_id, :product_id, :rating, :comment,
            :admin_reply, :admin_reply_at, :created_at, :updated_at
        )
        """
    )

    for item in payload:
        if not isinstance(item, dict):
            continue

        try:
            order_id = int(item.get('order_id'))
            user_id = int(item.get('user_id'))
            product_id = int(item.get('product_id'))
            rating = int(item.get('rating'))
        except (TypeError, ValueError):
            continue

        if order_id not in valid_order_ids:
            continue
        if user_id not in valid_user_ids:
            continue
        if product_id not in valid_product_ids:
            continue

        rating = max(1, min(5, rating))
        created_at = _safe_parse_datetime(item.get('created_at')) or datetime.utcnow()
        admin_reply_at = _safe_parse_datetime(item.get('admin_reply_at'))

        bind.execute(
            insert_sql,
            {
                'order_id': order_id,
                'user_id': user_id,
                'product_id': product_id,
                'rating': rating,
                'comment': (item.get('comment') or '').strip(),
                'admin_reply': (item.get('admin_reply') or '').strip() or None,
                'admin_reply_at': admin_reply_at,
                'created_at': created_at,
                'updated_at': created_at,
            }
        )


def _backfill_product_batches(bind):
    rows = bind.execute(
        sa.text(
            """
            SELECT id, COALESCE(in_stock, 0), COALESCE(cost_price, 0), created_at
            FROM products
            """
        )
    ).fetchall()

    if not rows:
        return

    has_batch_sql = sa.text(
        'SELECT COUNT(1) FROM product_batches WHERE product_id = :product_id'
    )
    insert_sql = sa.text(
        """
        INSERT INTO product_batches (product_id, quantity, cost_price, expiry_date, imported_at)
        VALUES (:product_id, :quantity, :cost_price, :expiry_date, :imported_at)
        """
    )

    default_expiry = (datetime.utcnow() + timedelta(days=30)).date()
    now = datetime.utcnow()

    for product_id, in_stock, cost_price, created_at in rows:
        quantity = int(in_stock or 0)
        if quantity <= 0:
            continue

        has_batch = bind.execute(has_batch_sql, {'product_id': product_id}).scalar() or 0
        if has_batch > 0:
            continue

        imported_at = _safe_parse_datetime(created_at) or now
        bind.execute(
            insert_sql,
            {
                'product_id': product_id,
                'quantity': quantity,
                'cost_price': int(cost_price or 0),
                'expiry_date': default_expiry,
                'imported_at': imported_at,
            }
        )


def _sync_product_ratings(bind):
    bind.execute(sa.text('UPDATE products SET rating = 0'))

    rows = bind.execute(
        sa.text(
            """
            SELECT product_id, AVG(rating) AS avg_rating
            FROM product_reviews
            GROUP BY product_id
            """
        )
    ).fetchall()

    update_sql = sa.text('UPDATE products SET rating = :rating WHERE id = :product_id')
    for product_id, avg_rating in rows:
        bind.execute(
            update_sql,
            {
                'rating': round(float(avg_rating or 0), 1),
                'product_id': product_id,
            }
        )


def upgrade():
    op.create_table(
        'product_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('cost_price', sa.Integer(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('imported_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_product_batches_product_id', 'product_batches', ['product_id'])
    op.create_index('ix_product_batches_expiry_date', 'product_batches', ['expiry_date'])

    op.create_table(
        'product_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('admin_reply', sa.Text(), nullable=True),
        sa.Column('admin_reply_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id', 'user_id', 'product_id', name='uq_review_order_user_product'),
    )
    op.create_index('ix_product_reviews_product_id', 'product_reviews', ['product_id'])
    op.create_index('ix_product_reviews_user_id', 'product_reviews', ['user_id'])

    bind = op.get_bind()
    _backfill_product_batches(bind)
    _import_legacy_reviews(bind)
    _sync_product_ratings(bind)


def downgrade():
    op.drop_index('ix_product_reviews_user_id', table_name='product_reviews')
    op.drop_index('ix_product_reviews_product_id', table_name='product_reviews')
    op.drop_table('product_reviews')

    op.drop_index('ix_product_batches_expiry_date', table_name='product_batches')
    op.drop_index('ix_product_batches_product_id', table_name='product_batches')
    op.drop_table('product_batches')
