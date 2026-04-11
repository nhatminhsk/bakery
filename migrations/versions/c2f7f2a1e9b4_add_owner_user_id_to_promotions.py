"""add owner_user_id to promotions

Revision ID: c2f7f2a1e9b4
Revises: 2a3b4c5d6e7f
Create Date: 2026-04-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2f7f2a1e9b4'
down_revision = '2a3b4c5d6e7f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_promotions_owner_user_id_users', 'users', ['owner_user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_promotions_owner_user_id_users', type_='foreignkey')
        batch_op.drop_column('owner_user_id')
