"""stage a add user points and new fks

Revision ID: 4a8d9f0b1c2d
Revises: dad8872442e5
Create Date: 2026-03-24 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a8d9f0b1c2d'
down_revision = 'dad8872442e5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('points', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('rank', sa.String(length=20), nullable=True, server_default='bronze'))

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('promotion_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_orders_promotion_id', 'promotions', ['promotion_id'], ['id'])

    with op.batch_alter_table('point_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_point_history_user_id', 'users', ['user_id'], ['id'])

    conn = op.get_bind()

    # Backfill orders.promotion_id from order_promotions (choose one promotion per order by smallest relation id)
    conn.execute(sa.text("""
        UPDATE orders
        SET promotion_id = (
            SELECT opx.promotion_id
            FROM order_promotions opx
            WHERE opx.order_id = orders.id
            ORDER BY opx.id ASC
            LIMIT 1
        )
        WHERE promotion_id IS NULL
    """))

    # Backfill point_history.user_id from linked order when available
    conn.execute(sa.text("""
        UPDATE point_history
        SET user_id = (
            SELECT o.user_id
            FROM orders o
            WHERE o.id = point_history.order_id
            LIMIT 1
        )
        WHERE user_id IS NULL
          AND order_id IS NOT NULL
    """))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('points', server_default=None)
        batch_op.alter_column('rank', server_default=None)


def downgrade():
    with op.batch_alter_table('point_history', schema=None, recreate='always') as batch_op:
        batch_op.drop_column('user_id')

    with op.batch_alter_table('orders', schema=None, recreate='always') as batch_op:
        batch_op.drop_column('promotion_id')

    with op.batch_alter_table('users', schema=None, recreate='always') as batch_op:
        batch_op.drop_column('rank')
        batch_op.drop_column('points')
