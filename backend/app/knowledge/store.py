"""Independent connection pool boundary: application tables are never imported."""
from contextlib import contextmanager
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from sqlalchemy.engine import make_url
from app.config import settings
from app.security import DomainError

@contextmanager
def connection():
    if not settings.knowledge_database_url:
        raise DomainError('KNOWLEDGE_NOT_CONFIGURED','Kho tri thức chưa được cấu hình.',503)
    url=make_url(settings.knowledge_database_url)
    try:
        with psycopg.connect(host=url.host,port=url.port or 5432,dbname=url.database,user=url.username,
                              password=url.password,connect_timeout=5,row_factory=dict_row) as db:
            yield db
    except psycopg.OperationalError:
        raise DomainError('KNOWLEDGE_UNAVAILABLE','Chưa kết nối được kho tri thức.',503) from None

def migrate():
    with connection() as db:
        for migration in sorted(Path(__file__).with_name('migrations').glob('*.sql')):
            db.execute(migration.read_text(encoding='utf-8'))
