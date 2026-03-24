"""stage c drop customer and order promotions

Revision ID: 8c9d0e1f2a3b
Revises: 6b1e2f3a4d5c
Create Date: 2026-03-24 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c9d0e1f2a3b'
down_revision = '6b1e2f3a4d5c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('order_promotions')
    op.drop_table('customers')


def downgrade():
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=120), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('rank', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
    )

    op.create_table(
        'order_promotions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('promotion_id', sa.Integer(), nullable=False),
        sa.Column('discount', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id']),
        sa.PrimaryKeyConstraint('id'),
    )
