from pathlib import Path
from uuid import UUID,uuid4
from typing import Literal
from fastapi import APIRouter,Depends
from fastapi.responses import FileResponse
from pydantic import Field,model_validator
from psycopg.types.json import Jsonb
from app.ai.contracts import Contract
from app.config import settings
from app.security import authenticate,admin,DomainError
from app.knowledge.store import connection
from app.knowledge.service import enqueue,retrieve,KnowledgeQuery,overlapping_prices,validate_metadata
from app.knowledge.crawler import validate_url
from app.knowledge.transform import publication,chunks
from app.knowledge.embedding import embed,literal

router=APIRouter(prefix='/api/admin/knowledge',tags=['knowledge'])

def require_admin(auth=Depends(authenticate)):
    admin(auth)
    return auth[0].id

router.dependencies=[Depends(require_admin)]

class SourceInput(Contract):
    name: str = Field(min_length=3,max_length=200)
    domains: list[str] = Field(min_length=1,max_length=5)
    seeds: list[str] = Field(min_length=1,max_length=10)
    topic: Literal['PRICES','GUIDANCE','REGULATIONS']
    enabled: bool = True
    seed_mode: Literal['LISTING','DOCUMENT'] = 'LISTING'
    utility: Literal['ELECTRICITY','WATER'] | None = None
    service_area: str | None = Field(default=None,max_length=100)
    @model_validator(mode='after')
    def boundaries(self):
        import re
        if any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}',d) for d in self.domains):
            raise ValueError('Tên miền không hợp lệ.')
        try:
            for url in self.seeds: validate_url(url,self.domains)
        except (ValueError,OSError): raise ValueError('URL không thuộc miền công khai được cho phép.') from None
        return self

class SourceState(Contract):
    enabled: bool

class ReviewInput(Contract):
    status: Literal['PUBLISHED','BLOCKED']
    topic: Literal['PRICES','GUIDANCE','REGULATIONS','OTHER'] | None = None
    effective_from: str | None = Field(default=None,pattern=r'^\d{4}-\d{2}-\d{2}$')
    effective_to: str | None = Field(default=None,pattern=r'^\d{4}-\d{2}-\d{2}$')
    effective_quote: str | None = Field(default=None,max_length=3000)
    scope: str | None = Field(default=None,max_length=100)
    scope_quote: str | None = Field(default=None,max_length=3000)

class SearchInput(Contract):
    query: str = Field(min_length=2,max_length=1000)
    utility: Literal['ELECTRICITY','WATER'] | None = None
    location: str | None = Field(default=None,max_length=100)
    as_of: str | None = None
    current_price: bool = False

@router.get('/sources')
def sources():
    with connection() as db: return db.execute('SELECT * FROM sources ORDER BY created_at').fetchall()

@router.post('/sources',status_code=201)
def create_source(data:SourceInput):
    with connection() as db:
        return db.execute('INSERT INTO sources(id,name,domains,seeds,topic,enabled,interval_hours,seed_mode,utility,service_area) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *',
            (uuid4(),data.name,Jsonb(data.domains),Jsonb(data.seeds),data.topic,data.enabled,6 if data.topic=='PRICES' else 24,data.seed_mode,data.utility,data.service_area)).fetchone()

@router.patch('/sources/{id}')
def source_state(id:UUID,data:SourceState|SourceInput):
    with connection() as db:
        if isinstance(data,SourceInput):
            row=db.execute('UPDATE sources SET name=%s,domains=%s,seeds=%s,topic=%s,enabled=%s,interval_hours=%s,seed_mode=%s,utility=%s,service_area=%s WHERE id=%s RETURNING *',
                (data.name,Jsonb(data.domains),Jsonb(data.seeds),data.topic,data.enabled,6 if data.topic=='PRICES' else 24,data.seed_mode,data.utility,data.service_area,id)).fetchone()
        else: row=db.execute('UPDATE sources SET enabled=%s WHERE id=%s RETURNING *',(data.enabled,id)).fetchone()
        if not row: raise DomainError('NOT_FOUND','Không tìm thấy nguồn.',404)
        return row

@router.post('/sources/{id}/crawl',status_code=202)
def crawl(id:UUID): return enqueue(id)

@router.get('/runs')
def runs():
    with connection() as db: return db.execute('SELECT * FROM crawl_runs ORDER BY created_at DESC LIMIT 100').fetchall()

@router.get('/documents')
def documents():
    with connection() as db:
        return db.execute('SELECT d.*,v.id AS version_id,v.status,v.metadata,v.created_at,v.embedding_model FROM documents d JOIN versions v ON v.document_id=d.id ORDER BY v.created_at DESC LIMIT 200').fetchall()

@router.get('/versions/{id}')
def version(id:UUID):
    with connection() as db:
        row=db.execute('SELECT v.*,d.url,d.title FROM versions v JOIN documents d ON d.id=v.document_id WHERE v.id=%s',(id,)).fetchone()
        if not row: raise DomainError('NOT_FOUND','Không tìm thấy phiên bản.',404)
        row.pop('raw_path',None)
        metadata=validate_metadata(dict(row['metadata']),row['content'])
        missing=[]
        if len(row['content'].strip())<100: missing.append('READABLE_TEXT')
        topic=metadata.get('topic')
        if topic not in ('PRICES','GUIDANCE','REGULATIONS'): missing.append('CLASSIFICATION')
        if topic=='PRICES':
            if not metadata.get('effective_from'): missing.append('EFFECTIVE_DATE')
            if not metadata.get('scope'): missing.append('SCOPE')
        if metadata.get('conflicts'): missing.append('CONFLICTS')
        row['readiness']={'can_publish':not missing and publication(topic,metadata,row['content'])=='PUBLISHED','missing':missing}
        return row

@router.get('/versions/{id}/original')
def original(id:UUID):
    with connection() as db: row=db.execute('SELECT raw_path FROM versions WHERE id=%s',(id,)).fetchone()
    root=Path(settings.knowledge_archive_path).resolve()
    path=(root/row['raw_path']).resolve() if row else root
    if root not in path.parents or not path.is_file(): raise DomainError('NOT_FOUND','Không tìm thấy bản gốc.',404)
    # Download only: never execute untrusted archived HTML under the application origin.
    return FileResponse(path,media_type='application/octet-stream',filename=path.name)

@router.patch('/versions/{id}')
def review(id:UUID,data:ReviewInput,actor=Depends(require_admin)):
    with connection() as db:
        row=db.execute('SELECT v.*,s.topic,d.title FROM versions v JOIN documents d ON d.id=v.document_id JOIN sources s ON s.id=d.source_id WHERE v.id=%s',(id,)).fetchone()
    if not row: raise DomainError('NOT_FOUND','Không tìm thấy phiên bản.',404)
    if (row['topic']=='PRICES' or row['metadata'].get('topic')=='PRICES') and data.topic not in (None,'PRICES'):
        raise DomainError('PRICE_CLASSIFICATION','Không thể đổi tài liệu giá thành hướng dẫn để bỏ qua kiểm tra.',422)
    row['metadata']={**row['metadata'],**data.model_dump(exclude={'status'},exclude_unset=True)}
    row['metadata']=validate_metadata(row['metadata'],row['content'])
    # Re-evaluate overlap against current published versions; other conflicts remain.
    if not overlapping_prices_for_review(row):
        row['metadata']['conflicts']=[c for c in row['metadata'].get('conflicts',[]) if c not in ('OVERLAPPING_PRICE_DOCUMENTS','CONFIRMED_PRICE_CONFLICT')]
    parts=[]; vectors=[]
    if data.status=='PUBLISHED':
        pub = publication(row['metadata'].get('topic',row['topic']),row['metadata'],row['content'])
        if pub != 'PUBLISHED' and not (row['metadata'].get('effective_from') and row['metadata'].get('scope')):
            raise DomainError('DOCUMENT_UNVERIFIED','Thiếu căn cứ hiệu lực/phạm vi hoặc có mâu thuẫn; chưa thể công bố.',422)
        parts=chunks([row['content']]); vectors=[embed(row['title']+'\n'+p) for p in parts]
    with connection() as db:
        db.execute('SELECT pg_advisory_xact_lock(7410832)')
        doc=db.execute('SELECT * FROM documents WHERE id=%s FOR UPDATE',(row['document_id'],)).fetchone()
        if data.status=='PUBLISHED':
            if overlapping_prices(db,doc['id'],row['metadata']):
                raise DomainError('PRICE_CONFLICT','Có tài liệu giá cùng phạm vi và thời gian. Xử lý phiên bản mâu thuẫn trước.',422)
            db.execute('DELETE FROM chunks WHERE version_id=%s',(id,))
            for i,(part,vector) in enumerate(zip(parts,vectors)):
                db.execute("INSERT INTO chunks(id,version_id,position,content,search,embedding) VALUES(%s,%s,%s,%s,to_tsvector('simple',unaccent(%s)),%s::vector)",
                    (uuid4(),id,i,part,row['title']+' '+part,literal(vector)))
            db.execute("UPDATE versions SET status='SUPERSEDED' WHERE document_id=%s AND status='PUBLISHED' AND id<>%s",(doc['id'],id))
            db.execute('UPDATE documents SET active_version=%s WHERE id=%s',(id,doc['id']))
        elif doc['active_version']==id: db.execute('UPDATE documents SET active_version=NULL WHERE id=%s',(doc['id'],))
        db.execute('UPDATE versions SET status=%s,embedding_model=%s,metadata=%s WHERE id=%s',(data.status,settings.knowledge_embedding_model,Jsonb(row['metadata']),id))
        db.execute('INSERT INTO review_events(id,version_id,actor_id,status,metadata) VALUES(%s,%s,%s,%s,%s)',
            (uuid4(),id,actor,data.status,Jsonb(row['metadata'])))
    return {'id':id,'status':data.status}

def overlapping_prices_for_review(row):
    with connection() as db: return overlapping_prices(db,row['document_id'],row['metadata'])

@router.post('/retrieve')
def search(data:SearchInput):
    return retrieve(KnowledgeQuery(needs_public_knowledge=True,**data.model_dump()))
