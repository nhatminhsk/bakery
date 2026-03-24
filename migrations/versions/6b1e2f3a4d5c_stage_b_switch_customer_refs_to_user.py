"""stage b switch customer refs to user

Revision ID: 6b1e2f3a4d5c
Revises: 4a8d9f0b1c2d
Create Date: 2026-03-24 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b1e2f3a4d5c'
down_revision = '4a8d9f0b1c2d'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    null_user_refs = conn.execute(sa.text("SELECT COUNT(*) FROM point_history WHERE user_id IS NULL")).scalar()
    if null_user_refs and int(null_user_refs) > 0:
        raise RuntimeError(
            'Cannot enforce point_history.user_id NOT NULL: remaining NULL rows exist. '
            'Please complete backfill for user_id before running this migration.'
        )

    with op.batch_alter_table('orders', schema=None, recreate='always') as batch_op:
        batch_op.drop_column('customer_id')

    with op.batch_alter_table('point_history', schema=None, recreate='always') as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('customer_id')


def downgrade():
    with op.batch_alter_table('orders', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('customer_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_orders_customer_id', 'customers', ['customer_id'], ['id'])

    with op.batch_alter_table('point_history', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('customer_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_point_history_customer_id', 'customers', ['customer_id'], ['id'])
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=True)
