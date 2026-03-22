import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import Date, DateTime

from app.extensions import db


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
    }

    target.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def import_database_snapshot(snapshot_path):
    """Nạp dữ liệu JSON vào DB local bằng cách replace toàn bộ dữ liệu bảng."""
    source = Path(snapshot_path)
    if not source.exists():
        return False

    payload = json.loads(source.read_text(encoding='utf-8'))
    tables_payload = payload.get('tables', {})

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

    return True