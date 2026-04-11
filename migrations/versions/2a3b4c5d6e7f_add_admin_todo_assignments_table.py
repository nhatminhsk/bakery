"""Add admin_todo_assignments table for many-to-many staff assignments.

Revision ID: 2a3b4c5d6e7f
Revises: f1c2d3e4f5a6
Create Date: 2026-04-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = 'f1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    # Create the admin_todo_assignments junction table
    op.create_table(
        'admin_todo_assignments',
        sa.Column('admin_todo_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['admin_todo_id'], ['admin_todos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('admin_todo_id', 'user_id'),
    )
    
    # Migrate existing assigned_user_id to the new many-to-many table
    # For each todo with assigned_user_id, insert into admin_todo_assignments
    connection = op.get_bind()
    
    # Get all todos with assigned_user_id
    todos_with_assignment = connection.execute(
        sa.text("SELECT id, assigned_user_id FROM admin_todos WHERE assigned_user_id IS NOT NULL")
    ).fetchall()
    
    # Insert into junction table
    for todo_id, user_id in todos_with_assignment:
        connection.execute(
            sa.text(
                "INSERT INTO admin_todo_assignments (admin_todo_id, user_id) "
                "VALUES (:todo_id, :user_id)"
            ),
            {"todo_id": todo_id, "user_id": user_id}
        )


def downgrade():
    # Before dropping the junction table, migrate data back to assigned_user_id
    connection = op.get_bind()
    
    # For each assignment, update the first one back to assigned_user_id (limit to one per todo)
    connection.execute(
        sa.text(
            """
            UPDATE admin_todos 
            SET assigned_user_id = (
                SELECT user_id FROM admin_todo_assignments 
                WHERE admin_todo_id = admin_todos.id 
                LIMIT 1
            )
            WHERE id IN (SELECT admin_todo_id FROM admin_todo_assignments)
            """
        )
    )
    
    # Drop the junction table
    op.drop_table('admin_todo_assignments')
