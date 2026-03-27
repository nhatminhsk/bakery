from datetime import datetime

from app.extensions import db


class AdminTodo(db.Model):
    __tablename__ = 'admin_todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='medium')  # 'high', 'medium', 'low'
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'priority': self.priority,
            'is_done': self.is_done,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
