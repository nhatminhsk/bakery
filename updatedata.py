from pathlib import Path

from app import create_app
from app.utils.db_snapshot import export_database_snapshot

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = BASE_DIR / 'data' / 'local_snapshot.json'


def main():
    app = create_app('development')
    with app.app_context():
        export_database_snapshot(SNAPSHOT_PATH)

    print(f'Updated snapshot: {SNAPSHOT_PATH}')


if __name__ == '__main__':
    main()
