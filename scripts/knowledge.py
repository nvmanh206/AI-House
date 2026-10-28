"""RAG operations; all commands leave the business database unchanged."""
import argparse
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4
from dotenv import dotenv_values

def set_key(filename,key,value):
    # Preserve unrelated settings; avoid Windows tempfile permission loops.
    path=Path(filename)
    lines=path.read_text(encoding='utf-8').splitlines()
    replacement=key+'='+str(value).replace('\\','/')
    found=False
    for i,line in enumerate(lines):
        if line.startswith(key+'='): lines[i]=replacement; found=True
    if not found: lines.append(replacement)
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

ROOT=Path(__file__).resolve().parents[1]
backend=ROOT/'backend'
sys.path.insert(0,str(backend))
parser=argparse.ArgumentParser()
parser.add_argument('command',choices=['prepare','migrate','seed','preflight','tick','worker','status','crawl','reindex','enable','disable'])
args=parser.parse_args()

if args.command=='prepare':
    local=ROOT/'.local'; local.mkdir(exist_ok=True)
    import tempfile
    tempfile.tempdir=str(local)
    secret=local/'knowledge-password'
    if not secret.exists(): secret.write_text(secrets.token_urlsafe(36),encoding='utf-8')
    env=backend/'.env'
    set_key(str(env),'KNOWLEDGE_DATABASE_URL','postgresql+psycopg://knowledge:'+secret.read_text().strip()+'@127.0.0.1:5435/knowledge')
    set_key(str(env),'KNOWLEDGE_ARCHIVE_PATH',str(local/'knowledge'))
    set_key(str(env),'KNOWLEDGE_EMBEDDING_MODEL','gemini-embedding-2')
    # Activation is a separate deployment step after live acceptance.
    if not dotenv_values(env).get('KNOWLEDGE_RAG_ENABLED'): set_key(str(env),'KNOWLEDGE_RAG_ENABLED','false')
    (local/'knowledge-backend.env').write_text('KNOWLEDGE_DATABASE_URL=postgresql+psycopg://knowledge:'+secret.read_text().strip()+'@knowledge-postgres:5432/knowledge\nKNOWLEDGE_ARCHIVE_PATH=/data/knowledge\nKNOWLEDGE_RAG_ENABLED='+dotenv_values(env)['KNOWLEDGE_RAG_ENABLED']+'\n',encoding='utf-8')
    servers=local/'pgadmin.servers.json'
    registry=json.loads(servers.read_text(encoding='utf-8')) if servers.exists() else {'Servers':{}}
    registry['Servers']['2']={'Name':'Nha Minh - public RAG PostgreSQL','Group':'Nha Minh','Host':'host.docker.internal',
        'Port':5435,'MaintenanceDB':'knowledge','Username':'knowledge',
        'ConnectionParameters':{'sslmode':'prefer','connect_timeout':10,'passfile':'.pgpass'}}
    servers.write_text(json.dumps(registry,indent=2),encoding='utf-8')
    pgpass=local/'pgadmin.pgpass'
    lines=[line for line in (pgpass.read_text(encoding='utf-8').splitlines() if pgpass.exists() else []) if not line.startswith('host.docker.internal:5435:')]
    lines.append('host.docker.internal:5435:*:knowledge:'+secret.read_text().strip())
    pgpass.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Prepared isolated knowledge credentials and pgAdmin registration; secrets not printed.')
    raise SystemExit()

for key,value in dotenv_values(backend/'.env').items():
    if value is not None: os.environ.setdefault(key,value)
os.chdir(backend)
from app.knowledge.store import connection,migrate
from app.knowledge.service import tick

if args.command in ('enable','disable'):
    if args.command=='enable':
        from app.knowledge.embedding import embed
        with connection() as db:
            if not db.execute("SELECT 1 FROM versions WHERE status='PUBLISHED' LIMIT 1").fetchone():
                raise SystemExit('No published documents; refusing activation.')
        embed('Kiểm tra truy xuất tri thức điện nước',query=True)
    value='true' if args.command=='enable' else 'false'
    set_key(str(backend/'.env'),'KNOWLEDGE_RAG_ENABLED',value)
    set_key(str(ROOT/'.local/knowledge-backend.env'),'KNOWLEDGE_RAG_ENABLED',value)
    print('RAG flag set to '+value+'; restart API/worker to apply.')
elif args.command=='migrate': migrate(); print('Knowledge schema migrated.')
elif args.command=='preflight':
    from app.knowledge.embedding import embed
    print('Embedding preflight dimensions:',len(embed('Đơn vị điện năng kWh là gì?',query=True)))
elif args.command=='seed':
    from psycopg.types.json import Jsonb
    from app.ai.get_new_evn_data import SOURCES
    with connection() as db:
        for name,topic,seed in [('EVN · Giá điện','PRICES',SOURCES['prices']),('EVN · Hướng dẫn và tin tức','GUIDANCE',SOURCES['news'])]:
            if not db.execute('SELECT id FROM sources WHERE name=%s',(name,)).fetchone():
                db.execute('INSERT INTO sources(id,name,domains,seeds,topic,interval_hours) VALUES(%s,%s,%s,%s,%s,%s)',
                    (uuid4(),name,Jsonb(['evn.com.vn']),Jsonb([seed]),topic,6 if topic=='PRICES' else 24))
        for name,topic,seed in [
            ('SAWACO · Dịch vụ cấp nước','GUIDANCE','https://sawaco.com.vn/post-detail/ung-dung-cong-nghe-giup-sawaco-co-nhung-buoc-tien-vuot-bac-trong-phuc-vu-khach-hang-231101233346'),
            ('SAWACO · Giá nước và hỏi đáp','PRICES','https://cskh.sawaco.com.vn/ho_tro/hoi_dap')]:
            if not db.execute('SELECT id FROM sources WHERE name=%s',(name,)).fetchone():
                db.execute("INSERT INTO sources(id,name,domains,seeds,topic,interval_hours,seed_mode,utility,service_area) VALUES(%s,%s,%s,%s,%s,%s,'DOCUMENT','WATER',%s)",
                    (uuid4(),name,Jsonb(['sawaco.com.vn']),Jsonb([seed]),topic,6 if topic=='PRICES' else 24,'Hồ Chí Minh'))
    print('Registered official EVN and SAWACO source URLs; no tariffs or answers inserted.')
elif args.command=='reindex':
    from app.config import settings
    from app.knowledge.embedding import embed,literal
    with connection() as db:
        versions=db.execute("SELECT v.id,d.title,v.metadata FROM versions v JOIN documents d ON d.id=v.document_id WHERE v.status IN ('PUBLISHED','SUPERSEDED') ORDER BY v.created_at").fetchall()
    for version in versions:
        with connection() as db: parts=db.execute('SELECT id,content FROM chunks WHERE version_id=%s ORDER BY position',(version['id'],)).fetchall()
        vectors=[embed(version['title']+'\n'+json.dumps(version['metadata'],ensure_ascii=False)+'\n'+p['content']) for p in parts]
        with connection() as db:
            db.execute('SELECT id FROM versions WHERE id=%s FOR UPDATE',(version['id'],))
            for part,vector in zip(parts,vectors): db.execute('UPDATE chunks SET embedding=%s::vector WHERE id=%s',(literal(vector),part['id']))
            db.execute('UPDATE versions SET embedding_model=%s WHERE id=%s',(settings.knowledge_embedding_model,version['id']))
    print('Reindexed published/historical versions with configured model; no mixed vectors within a version.')
elif args.command=='crawl':
    from app.knowledge.service import enqueue,process_one
    with connection() as db: sources=db.execute('SELECT id FROM sources WHERE enabled').fetchall()
    for source in sources: enqueue(source['id'])
    for source in sources: process_one()
    print('Processed all enabled sources.')
elif args.command=='tick': tick(); print('Processed one ingestion tick.')
elif args.command=='worker':
    from apscheduler.schedulers.blocking import BlockingScheduler
    worker=BlockingScheduler(timezone='Asia/Ho_Chi_Minh')
    worker.add_job(tick,'interval',minutes=1,max_instances=1,coalesce=True)
    tick(); worker.start()
else:
    with connection() as db:
        for table in ('sources','crawl_runs','documents','versions','chunks'):
            print(table,db.execute('SELECT count(*) AS n FROM '+table).fetchone()['n'])
