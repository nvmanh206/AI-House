"""Prepare ignored local pgAdmin credentials and register the app's real database.

Run with backend/.venv/Scripts/python.exe. Does not change PostgreSQL data.
"""
import json
import secrets
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

root = Path(__file__).resolve().parents[1]
local = root / '.local'
local.mkdir(exist_ok=True)
url = make_url(dotenv_values(root / 'backend' / '.env')['DATABASE_URL'])
if url.get_backend_name() != 'postgresql':
    raise SystemExit('The application must be configured for PostgreSQL first.')
host = 'host.docker.internal' if url.host in ('localhost', '127.0.0.1', '::1') else url.host
if not host or not url.username or not url.password or not url.database:
    raise SystemExit('The application database configuration is incomplete.')

password_file = local / 'pgadmin-admin-password'
if not password_file.exists():
    password_file.write_text(secrets.token_urlsafe(32), encoding='utf-8')

def escape_pgpass(value):
    return str(value).replace('\\', '\\\\').replace(':', '\\:')

pgpass = ':'.join(map(escape_pgpass, (host, url.port or 5432, '*', url.username, url.password)))
(local / 'pgadmin.pgpass').write_text(pgpass + '\n', encoding='utf-8')
server = {
    'Name': 'Nha Minh - application PostgreSQL',
    'Group': 'Nha Minh',
    'Host': host,
    'Port': url.port or 5432,
    'MaintenanceDB': url.database,
    'Username': url.username,
    'ConnectionParameters': {'sslmode': 'prefer', 'connect_timeout': 10, 'passfile': '.pgpass'},
}
(local / 'pgadmin.servers.json').write_text(json.dumps({'Servers': {'1': server}}, indent=2), encoding='utf-8')
(local / 'pgadmin-access.txt').write_text(
    'URL: http://127.0.0.1:5050\nEmail: admin@example.com\nPassword: '
    + password_file.read_text(encoding='utf-8').strip() + '\n', encoding='utf-8')
print('Prepared pgAdmin configuration; access details: .local/pgadmin-access.txt (not printed).')
print('Database credentials were read from backend/.env; no database data was changed.')
