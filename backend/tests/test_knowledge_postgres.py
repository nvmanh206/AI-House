"""Real pgvector database, rolled back per case; zero production documents touched."""
import os
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import pytest
from psycopg.types.json import Jsonb
from app.config import settings
from app.knowledge import store,service
from app.knowledge.embedding import literal

@pytest.fixture
def corpus(monkeypatch,tmp_path):
    url=os.environ.get('KNOWLEDGE_TEST_DATABASE_URL')
    if not url: pytest.skip('Use scripts/test_postgres.py for isolated pgvector tests')
    assert url.rsplit('/',1)[-1].endswith('_test')
    monkeypatch.setattr(settings,'knowledge_database_url',url)
    store.migrate()
    with store.connection() as db:
        assert db.execute('SELECT count(*) AS n FROM documents').fetchone()['n']==0
        @contextmanager
        def transactional(): yield db
        monkeypatch.setattr(service,'connection',transactional)
        monkeypatch.setattr(settings,'knowledge_archive_path',str(tmp_path))
        monkeypatch.setattr(service,'embed',lambda *a,**k:[1.0]+[0.0]*767)
        yield db
        db.rollback()

def seed(db,*,scope='NATIONAL',effective='2026-01-01',status='PUBLISHED',age=0,topic='PRICES'):
    source,doc,version,chunk=[uuid4() for _ in range(4)]
    db.execute('INSERT INTO sources(id,name,domains,seeds,topic,interval_hours) VALUES(%s,%s,%s,%s,%s,6)',(source,'Fixture',Jsonb(['evn.com.vn']),Jsonb([]),topic))
    db.execute('INSERT INTO documents(id,source_id,url,title,active_version,checked_at) VALUES(%s,%s,%s,%s,%s,%s)',
        (doc,source,'https://www.evn.com.vn/'+str(doc),'Giá điện sinh hoạt',version,datetime.now(timezone.utc)-timedelta(days=age)))
    db.execute('INSERT INTO versions(id,document_id,content_hash,status,content,raw_path,metadata,embedding_model) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        (version,doc,str(version),status,'Fixture only','fixture',Jsonb({'scope':scope,'effective_from':effective,'utility':'ELECTRICITY','topic':topic,'price_category':'RESIDENTIAL'}),settings.knowledge_embedding_model))
    db.execute("INSERT INTO chunks(id,version_id,position,content,search,embedding) VALUES(%s,%s,0,%s,to_tsvector('simple',unaccent(%s)),%s::vector)",
        (chunk,version,'Giá điện sinh hoạt có ngày hiệu lực.','Giá điện sinh hoạt',literal([1]+[0]*767)))
    return source,doc,version,chunk

def query(**kwargs):
    return service.KnowledgeQuery(needs_public_knowledge=True,query='gia dien sinh hoat',utility='ELECTRICITY',location=None,as_of='2026-10-28',current_price=True,**kwargs)

def test_real_hybrid_and_explicit_keyword_degradation(corpus,monkeypatch):
    seed(corpus)
    result=service.retrieve(query())
    assert result['mode']=='HYBRID' and len(result['documents'])==1
    from app.security import DomainError
    def unavailable(*a,**k): raise DomainError('EMBEDDING_UNAVAILABLE','Unavailable',503)
    monkeypatch.setattr(service,'embed',unavailable)
    result=service.retrieve(query())
    assert result['mode']=='KEYWORD' and len(result['documents'])==1
    assert 'EMBEDDING_UNAVAILABLE' in result['warnings']

def test_shared_provider_window_and_cooldown_in_real_postgres(corpus,monkeypatch):
    from app.ai import quota
    from app.security import DomainError
    @contextmanager
    def transaction():yield corpus
    monkeypatch.setattr(quota,'connection',transaction)
    monkeypatch.setattr(settings,'gemini_quota_guard_enabled',True)
    monkeypatch.setattr(settings,'gemini_requests_per_minute',1)
    monkeypatch.setattr(settings,'gemini_api_key','isolated-test-only')
    quota.guard()
    with pytest.raises(DomainError) as rejected:quota.guard()
    assert rejected.value.code=='GEMINI_COOLDOWN' and 1<=rejected.value.retry_after<=60
    quota.guard(pause=120)
    with pytest.raises(DomainError) as paused:quota.guard()
    assert paused.value.retry_after>=119
    row=corpus.execute('SELECT state FROM provider_limits WHERE scope=%s',(quota.scope(),)).fetchone()
    assert len(row['state']['calls'])==1

def test_excludes_wrong_scope_future_pending_and_stale(corpus):
    seed(corpus,scope='Hà Nội');seed(corpus,effective='2027-01-01');seed(corpus,status='PENDING_REVIEW');seed(corpus,age=2)
    result=service.retrieve(query())
    assert not result['documents']
    assert 'PRICE_SOURCE_STALE' in result['warnings']

def test_overlap_alone_does_not_veto_existing_evidence(corpus):
    seed(corpus)
    _,_,version,_=seed(corpus,status='PENDING_REVIEW')
    corpus.execute("UPDATE versions SET metadata=metadata || %s WHERE id=%s",(Jsonb({'conflicts':['OVERLAPPING_PRICE_DOCUMENTS']}),version))
    assert service.retrieve(query())['documents']

def test_changed_pending_document_does_not_refresh_old_price(corpus,monkeypatch):
    source_id,doc_id,_,_=seed(corpus,age=2)
    source=corpus.execute('SELECT * FROM sources WHERE id=%s',(source_id,)).fetchone()
    doc=corpus.execute('SELECT * FROM documents WHERE id=%s',(doc_id,)).fetchone()
    monkeypatch.setattr(service,'metadata_for',lambda *_:{'topic':'PRICES','utility':'ELECTRICITY','scope':None,'effective_from':None,'conflicts':[]})
    body=b'<html><body><article><p>Updated electricity price document without a verifiable effective date or geographic scope for this fixture.</p></article></body></html>'
    service.ingest(source,doc['url'],'Changed price',body,'text/html')
    after=corpus.execute('SELECT checked_at FROM documents WHERE id=%s',(doc_id,)).fetchone()['checked_at']
    assert after==doc['checked_at']
    assert not service.retrieve(query())['documents']

def test_disabled_source_cannot_veto_enabled_price(corpus):
    seed(corpus)
    other,_,version,_=seed(corpus,status='PENDING_REVIEW')
    corpus.execute("UPDATE versions SET metadata=metadata || %s WHERE id=%s",(Jsonb({'conflicts':['CONFIRMED_PRICE_CONFLICT']}),version))
    assert not service.retrieve(query())['documents']
    corpus.execute('UPDATE sources SET enabled=false WHERE id=%s',(other,))
    assert service.retrieve(query())['documents']

def test_matching_supporting_prices_and_different_categories_are_not_conflicts(corpus):
    _,doc,version,_=seed(corpus)
    facts=[{'label':'Bậc 1','amount':'2000','unit':'VND/kWh','quote':'Fixture only'}]
    corpus.execute('UPDATE versions SET metadata=metadata || %s WHERE id=%s',(Jsonb({'price_facts':facts}),version))
    meta={'topic':'PRICES','utility':'ELECTRICITY','scope':'NATIONAL','effective_from':'2026-01-01',
          'price_category':'RESIDENTIAL','price_facts':facts}
    assert not service.overlapping_prices(corpus,uuid4(),meta)
    conflicting={**meta,'price_facts':[{**facts[0],'amount':'3000'}]}
    assert service.overlapping_prices(corpus,uuid4(),conflicting)
    assert not service.overlapping_prices(corpus,uuid4(),{**conflicting,'price_category':'BUSINESS'})
    assert not service.overlapping_prices(corpus,uuid4(),{**conflicting,'effective_from':'2026-02-01'})

def test_latest_dated_price_wins_and_historical_query_keeps_old_schedule(corpus):
    _,_,old,_=seed(corpus,effective='2025-01-01')
    _,_,new,_=seed(corpus,effective='2026-01-01')
    result=service.retrieve(query())
    assert {d['version_id'] for d in result['documents']}=={str(new)}
    historical=query();historical.as_of='2025-06-01';historical.current_price=False
    assert {d['version_id'] for d in service.retrieve(historical)['documents']}=={str(old)}

def test_water_provider_guidance_does_not_apply_to_another_region(corpus):
    _,_,version,_=seed(corpus,topic='GUIDANCE')
    corpus.execute('UPDATE versions SET metadata=metadata || %s WHERE id=%s',
        (Jsonb({'utility':'WATER','service_area':'ho chi minh','scope':None,'effective_from':None}),version))
    request=service.KnowledgeQuery(needs_public_knowledge=True,query='SAWACO dịch vụ nước',utility='WATER',
        location='TP. Hồ Chí Minh',as_of=None,current_price=False)
    assert service.retrieve(request)['documents']
    request.location='Thái Nguyên'
    assert not service.retrieve(request)['documents']
    request.location=None;request.utility='ELECTRICITY'
    assert not service.retrieve(request)['documents']

def test_admin_source_queue_validation_and_original_authorization(corpus,client,ready,db,monkeypatch):
    from app.knowledge import api,crawler
    from app.models import User
    from sqlalchemy import select
    headers,_,_=ready
    user=db.scalar(select(User).where(User.email=='a@example.com'));user.role='ADMIN';db.commit()
    @contextmanager
    def transactional(): yield corpus
    monkeypatch.setattr(api,'connection',transactional)
    monkeypatch.setattr(api,'validate_url',lambda u,d:crawler.validate_url(u,d,lambda *_:['93.184.216.34']))
    bad=client.post('/api/admin/knowledge/sources',headers=headers,json={'name':'Bad URL','domains':['evn.com.vn'],'seeds':['https://127.0.0.1/a'],'topic':'GUIDANCE'})
    assert bad.status_code==422
    source=client.post('/api/admin/knowledge/sources',headers=headers,json={'name':'Fixture EVN','domains':['evn.com.vn'],'seeds':['https://www.evn.com.vn/'],'topic':'GUIDANCE'})
    assert source.status_code==201,source.text
    a=client.post('/api/admin/knowledge/sources/'+source.json()['id']+'/crawl',headers=headers)
    b=client.post('/api/admin/knowledge/sources/'+source.json()['id']+'/crawl',headers=headers)
    assert a.status_code==b.status_code==202 and a.json()['id']==b.json()['id']
    assert client.get('/api/admin/knowledge/versions/'+str(uuid4())+'/original').status_code==401

def test_idempotent_ingestion_preserves_active_on_embedding_failure(corpus,monkeypatch):
    source_id,doc_id,version_id,_=seed(corpus,topic='GUIDANCE')
    source=corpus.execute('SELECT * FROM sources WHERE id=%s',(source_id,)).fetchone()
    monkeypatch.setattr(service,'metadata_for',lambda *_:{'topic':'GUIDANCE','utility':'ELECTRICITY','conflicts':[]})
    body=b'<html><body><article><p>Public electricity guidance with enough text to be read and indexed as a real document for this isolated fixture.</p></article></body></html>'
    assert service.ingest(source,'https://www.evn.com.vn/test','Guidance',body,'text/html')
    assert not service.ingest(source,'https://www.evn.com.vn/test','Guidance',body,'text/html')
    from app.security import DomainError
    def unavailable(*a,**k): raise DomainError('EMBEDDING_UNAVAILABLE','Unavailable',503)
    monkeypatch.setattr(service,'embed',unavailable)
    with pytest.raises(DomainError): service.ingest(source,'https://www.evn.com.vn/test','Guidance',body.replace(b'Public',b'Updated'),'text/html')
    assert corpus.execute('SELECT count(*) AS n FROM versions').fetchone()['n']==2
