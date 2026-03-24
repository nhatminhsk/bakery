from app import create_app
from flask_migrate import upgrade


def main():
    app = create_app('development')
    with app.app_context():
        upgrade(directory='migrations')

    print('Database upgraded to latest migration.')


if __name__ == '__main__':
    main()
