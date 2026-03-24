from app import create_app
from app.utils.db_snapshot import export_database_snapshot

SNAPSHOT_PATH = 'data/local_snapshot.json'


def main():
    app = create_app('development')
    with app.app_context():
        export_database_snapshot(SNAPSHOT_PATH)

    print(f'Updated snapshot: {SNAPSHOT_PATH}')


if __name__ == '__main__':
    main()
