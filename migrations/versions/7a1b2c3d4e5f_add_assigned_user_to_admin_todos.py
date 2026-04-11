"""add assigned user to admin todos

Revision ID: 7a1b2c3d4e5f
Revises: 29cc73ef274d
Create Date: 2026-04-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a1b2c3d4e5f'
down_revision = '29cc73ef274d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('admin_todos') as batch_op:
        batch_op.add_column(sa.Column('assigned_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_admin_todos_assigned_user_id_users',
            'users',
            ['assigned_user_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('admin_todos') as batch_op:
        batch_op.drop_constraint('fk_admin_todos_assigned_user_id_users', type_='foreignkey')
        batch_op.drop_column('assigned_user_id')
