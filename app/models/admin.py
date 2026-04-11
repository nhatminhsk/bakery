from datetime import datetime

from app.extensions import db


# Many-to-many association table for task assignments
admin_todo_assignments = db.Table(
    'admin_todo_assignments',
    db.Column('admin_todo_id', db.Integer, db.ForeignKey('admin_todos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)


class AdminTodo(db.Model):
    __tablename__ = 'admin_todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='medium')  # 'high', 'medium', 'low'
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id])
    # New many-to-many relationship: one task can have many staff
    assigned_staff = db.relationship(
        'User',
        secondary=admin_todo_assignments,
        backref='assigned_todos',
        cascade='all, delete',
        lazy='joined',  # Eager load by default
    )

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        staff_assignments = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
            for user in (self.assigned_staff or [])
        ]
        
        return {
            'id': self.id,
            'title': self.title,
            'priority': self.priority,
            'assigned_user_id': self.assigned_user_id,
            'assigned_username': self.assigned_user.username if self.assigned_user else None,
            'assigned_user_role': self.assigned_user.role if self.assigned_user else None,
            'assigned_staff': staff_assignments,  # List of all assigned staff
            'is_done': self.is_done,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
