from app import create_app
from app.utils.db_snapshot import import_database_snapshot

app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        import_database_snapshot('data/local_snapshot.json')
    app.run(debug=True)
