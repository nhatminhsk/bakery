import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import Date, DateTime

from app.extensions import db


# NOTE: admin_todos are now stored in the database (admin_todos table),
# so we no longer export/import them from JSON files.
PRODUCT_REVIEWS_PATH = Path('data/product_reviews.json')
ADMIN_SETTINGS_PATH = Path('data/admin_settings.json')


def _serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _deserialize_value(column_type, value):
    if value is None:
        return None

    if isinstance(column_type, DateTime) and isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return value

    if isinstance(column_type, Date) and isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return value

    return value


def export_database_snapshot(snapshot_path):
    """Xuất toàn bộ dữ liệu từ tất cả bảng sang file JSON."""
    target = Path(snapshot_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    tables_payload = {}
    table_names = []

    with db.engine.connect() as conn:
        for table in db.metadata.sorted_tables:
            table_names.append(table.name)
            result = conn.execute(table.select())
            rows = []

            for row in result.mappings():
                row_data = {
                    key: _serialize_value(value)
                    for key, value in row.items()
                }
                rows.append(row_data)

            tables_payload[table.name] = rows

    payload = {
        'meta': {
            'generated_at': datetime.utcnow().isoformat(),
            'table_names': table_names,
        },
        'tables': tables_payload,
        'local_files': {},
    }

    # Keep product_reviews local storage in sync with DB snapshot lifecycle.
    if PRODUCT_REVIEWS_PATH.exists():
        try:
            reviews_payload = json.loads(PRODUCT_REVIEWS_PATH.read_text(encoding='utf-8'))
            payload['local_files']['product_reviews'] = reviews_payload
        except Exception:
            payload['local_files']['product_reviews'] = []

    if ADMIN_SETTINGS_PATH.exists():
        try:
            settings_payload = json.loads(ADMIN_SETTINGS_PATH.read_text(encoding='utf-8'))
            payload['local_files']['admin_settings'] = settings_payload
        except Exception:
            payload['local_files']['admin_settings'] = {}

    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def import_database_snapshot(snapshot_path):
    """Nạp dữ liệu JSON vào DB local bằng cách replace toàn bộ dữ liệu bảng."""
    source = Path(snapshot_path)
    if not source.exists():
        return False

    payload = json.loads(source.read_text(encoding='utf-8'))
    tables_payload = payload.get('tables', {})
    local_files_payload = payload.get('local_files', {})

    with db.engine.begin() as conn:
        is_sqlite = db.engine.dialect.name == 'sqlite'
        if is_sqlite:
            conn.exec_driver_sql('PRAGMA foreign_keys = OFF')

        for table in reversed(db.metadata.sorted_tables):
            if table.name in tables_payload:
                conn.execute(table.delete())

        for table in db.metadata.sorted_tables:
            rows = tables_payload.get(table.name, [])
            if not rows:
                continue

            normalized_rows = []
            for row in rows:
                normalized = {}
                for column in table.columns:
                    if column.name in row:
                        normalized[column.name] = _deserialize_value(column.type, row[column.name])
                normalized_rows.append(normalized)

            if normalized_rows:
                conn.execute(table.insert(), normalized_rows)

        if is_sqlite:
            conn.exec_driver_sql('PRAGMA foreign_keys = ON')

    # Restore product_reviews from local files only
    # (admin_todos are now part of the database tables)
    if 'product_reviews' in local_files_payload:
        PRODUCT_REVIEWS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRODUCT_REVIEWS_PATH.write_text(
            json.dumps(local_files_payload.get('product_reviews') or [], ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    if 'admin_settings' in local_files_payload:
        ADMIN_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        ADMIN_SETTINGS_PATH.write_text(
            json.dumps(local_files_payload.get('admin_settings') or {}, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    return True