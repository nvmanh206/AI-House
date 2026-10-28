"""Run backend tests in an empty PostgreSQL database separate from app data."""
import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

root = Path(__file__).resolve().parents[1]
backend = root / 'backend'
url = make_url(dotenv_values(backend / '.env')['DATABASE_URL'])
if url.get_backend_name() != 'postgresql':
    raise SystemExit('Application must be configured for PostgreSQL; SQLite fallback is not allowed.')
test_name = url.database + '_test'
if len(test_name) > 63 or test_name == url.database:
    raise SystemExit('Invalid isolated test database name.')
test_url = url.set(database=test_name)
admin = create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT')
with admin.connect() as connection:
    exists = connection.execute(text('SELECT 1 FROM pg_database WHERE datname=:name'), {'name': test_name}).scalar()
    if not exists:
        identifier = connection.dialect.identifier_preparer.quote(test_name)
        connection.execute(text('CREATE DATABASE ' + identifier))
admin.dispose()
engine = create_engine(test_url)
with engine.connect() as connection:
    for name in inspect(connection).get_table_names():
        if name == 'alembic_version':
            continue
        identifier = connection.dialect.identifier_preparer.quote(name)
        if connection.execute(text('SELECT EXISTS (SELECT 1 FROM ' + identifier + ' LIMIT 1)')).scalar():
            raise SystemExit('Test database contains committed records. Refusing to run; no cleanup performed.')
engine.dispose()
environment = {**os.environ, 'TEST_DATABASE_URL': test_url.render_as_string(hide_password=False),
               'GEMINI_API_KEY': '', 'LLM_API_KEY': '', 'KNOWLEDGE_RAG_ENABLED':'false'}
knowledge_url=dotenv_values(backend/'.env').get('KNOWLEDGE_DATABASE_URL')
if knowledge_url:
    knowledge_url=make_url(knowledge_url)
    knowledge_test=knowledge_url.set(database=knowledge_url.database+'_test')
    knowledge_admin=create_engine(knowledge_url.set(database='postgres'),isolation_level='AUTOCOMMIT')
    with knowledge_admin.connect() as c:
        if not c.execute(text('SELECT 1 FROM pg_database WHERE datname=:n'),{'n':knowledge_test.database}).scalar():
            c.execute(text('CREATE DATABASE '+c.dialect.identifier_preparer.quote(knowledge_test.database)))
    knowledge_admin.dispose()
    environment['KNOWLEDGE_TEST_DATABASE_URL']=knowledge_test.render_as_string(hide_password=False)
print(f'Running against PostgreSQL {url.host}:{url.port}/{test_name}; application DB untouched.', flush=True)
raise SystemExit(subprocess.call([sys.executable, '-m', 'pytest', '-q', '--tb=short',
                                 '-p', 'no:cacheprovider', *sys.argv[1:]], cwd=backend, env=environment))
