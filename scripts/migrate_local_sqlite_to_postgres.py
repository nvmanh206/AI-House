"""Copy the configured SQLite database to an EMPTY, separate local PostgreSQL DB.

Preserves the SQLite source and existing utility PostgreSQL database. Updates
backend/.env only after per-table content verification succeeds. No demo seed.
"""
import hashlib
import argparse
import json
import os
import sqlite3
import socket
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from dotenv import dotenv_values, set_key
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import URL, make_url

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--offline', action='store_true', help='Confirm backend, scheduler and every SQLite writer are stopped.')
args = parser.parse_args()
if not args.offline:
    raise SystemExit('Stop backend/scheduler/all SQLite writers, then pass --offline. No changes performed.')
with socket.socket() as probe:
    probe.settimeout(1)
    if probe.connect_ex(('127.0.0.1', 8000)) == 0:
        raise SystemExit('Backend port 8000 is active. Stop writers before offline migration.')
backend = root / 'backend'
local = root / '.local'
local.mkdir(exist_ok=True)
config_path = backend / '.env'
config = dotenv_values(config_path)
source_url = make_url(config['DATABASE_URL'])
if source_url.get_backend_name() != 'sqlite':
    raise SystemExit('Source is not SQLite; no migration or config change performed.')
source_path = (backend / source_url.database).resolve()
if not source_path.is_file():
    raise SystemExit('Configured SQLite source does not exist.')

target_url = URL.create('postgresql+psycopg', username='utility',
    password=dotenv_values(root / '.env')['POSTGRES_PASSWORD'],
    host='127.0.0.1', port=5433, database='utility_app')
admin = create_engine(target_url.set(database='postgres'), isolation_level='AUTOCOMMIT')
with admin.connect() as connection:
    exists = connection.execute(text('SELECT 1 FROM pg_database WHERE datname=:name'), {'name': target_url.database}).scalar()
    if not exists:
        connection.execute(text('CREATE DATABASE utility_app'))
admin.dispose()

target = create_engine(target_url)
with target.connect() as connection:
    for name in inspect(connection).get_table_names():
        if name != 'alembic_version' and connection.execute(text('SELECT EXISTS (SELECT 1 FROM "' + name.replace('"', '""') + '" LIMIT 1)')).scalar():
            raise SystemExit('Target contains data. Refusing to merge or overwrite; source/config untouched.')

stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup = local / f'pre-postgres-{stamp}.sqlite3'
with sqlite3.connect(source_path.as_uri() + '?mode=ro', uri=True) as source:
    with sqlite3.connect(backup) as destination:
        source.backup(destination)
config_backup = local / f'backend-env-before-postgres-{stamp}'
config_backup.write_bytes(config_path.read_bytes())
# Reserve the source against concurrent writes. The snapshot is checked again
# under this lock; an old backend must stay stopped through the config cutover.
source_lock = sqlite3.connect(source_path)
source_lock.execute('BEGIN IMMEDIATE')

os.environ['DATABASE_URL'] = target_url.render_as_string(hide_password=False)
os.environ['JWT_SECRET'] = config['JWT_SECRET']
sys.path.insert(0, str(backend))
from alembic import command
from alembic.config import Config
from app.db import Base
from app import models  # register tables

alembic_config = Config(str(backend / 'alembic.ini'))
alembic_config.set_main_option('script_location', str(backend / 'alembic'))
command.upgrade(alembic_config, 'head')

def canonical(value):
    if isinstance(value, Decimal):
        return str(value.normalize())
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(type(value).__name__)

def digest(rows):
    content = json.dumps(sorted((dict(row) for row in rows), key=lambda row: row['id']),
                         ensure_ascii=False, sort_keys=True, default=canonical)
    return hashlib.sha256(content.encode()).hexdigest()

snapshot = create_engine(URL.create('sqlite', database=str(backup)))
live_source = create_engine(URL.create('sqlite', database=str(source_path)))
report = {'source_backup': str(backup.relative_to(root)),
          'config_backup': str(config_backup.relative_to(root)),
          'target': '127.0.0.1:5433/utility_app', 'tables': {},
          'timezone_rule': 'Existing naive application timestamps interpreted as UTC.'}
with snapshot.connect() as source, live_source.connect() as live, target.begin() as destination:
    for table in Base.metadata.sorted_tables:
        source_columns = {column['name'] for column in inspect(source).get_columns(table.name)}
        if source_columns != set(table.columns.keys()):
            raise RuntimeError(f'Schema mismatch for {table.name}; aborting without switching config.')
        rows = [
            {key: value.replace(tzinfo=timezone.utc)
             if isinstance(value, datetime) and value.tzinfo is None else value
             for key, value in row.items()}
            for row in source.execute(select(table)).mappings()
        ]
        if digest(rows) != digest(live.execute(select(table)).mappings().all()):
            raise RuntimeError(f'Source changed after snapshot: {table.name}; aborting migration.')
        if rows:
            destination.execute(table.insert(), [dict(row) for row in rows])
        copied = destination.execute(select(table)).mappings().all()
        expected, actual = digest(rows), digest(copied)
        if len(rows) != len(copied) or expected != actual:
            raise RuntimeError(f'Content verification failed: {table.name}; transaction rolled back.')
        report['tables'][table.name] = {'rows': len(rows), 'sha256': actual}
snapshot.dispose()
live_source.dispose()
target.dispose()
report_path = local / f'postgres-migration-{stamp}.json'
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
set_key(str(config_path), 'DATABASE_URL', target_url.render_as_string(hide_password=False))
source_lock.rollback()
source_lock.close()
print('Migration verified; backend/.env now points to PostgreSQL utility_app on 127.0.0.1:5433.')
print('Original SQLite and previous PostgreSQL utility database preserved.')
print('Verification report:', report_path.relative_to(root))
for name, details in report['tables'].items():
    print(name, details['rows'], 'rows verified')
