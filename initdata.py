from pathlib import Path
from datetime import datetime

from app import create_app
from app.extensions import db
from app.models.admin import AdminTodo
from app.utils.db_snapshot import import_database_snapshot

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = BASE_DIR / 'data' / 'local_snapshot.json'


def seed_default_admin_todos():
    """Seed default todos if the table is empty."""
    if AdminTodo.query.first() is not None:
        return  # Table already has data

    defaults = [
        AdminTodo(
            title='Kiểm tra tồn kho nguyên liệu đầu ca',
            priority='high',
            is_done=False,
        ),
        AdminTodo(
            title='Xác nhận lịch giao hàng đơn quan trọng',
            priority='medium',
            is_done=False,
        ),
        AdminTodo(
            title='Tổng vệ sinh khu vực đóng gói',
            priority='low',
            is_done=True,
            completed_at=datetime.utcnow(),
        ),
    ]
    db.session.add_all(defaults)
    db.session.commit()


def main():
    app = create_app('development')
    with app.app_context():
        success = import_database_snapshot(SNAPSHOT_PATH)

    if success:
        print(f'Imported snapshot: {SNAPSHOT_PATH}')
    else:
        print(f'Snapshot not found or import failed: {SNAPSHOT_PATH}')

    # Seed default todos once after database initialization
    with app.app_context():
        seed_default_admin_todos()
        print('Default admin todos seeded.')


if __name__ == '__main__':
    main()
