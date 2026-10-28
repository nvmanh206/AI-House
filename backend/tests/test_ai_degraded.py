"""Quota/latency budget: one generateContent per message, local answer when Gemini fails."""
import json
import httpx
import pytest
from app.ai.gemini_structured import StructuredGemini
from app.ai.contracts import Reply
from app.config import settings
from app.knowledge import service as knowledge
from conftest import register,setup_house,reading

def reply(message='Câu trả lời từ Gemini.'):
    return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(
        {'requested_task':'OTHER','status':'ANSWERED','message':message,'evidence_refs':[]})}]}}]})

@pytest.fixture
def gemini(monkeypatch):
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    monkeypatch.setattr('app.ai.gemini_structured.time.sleep',lambda *_:None)
    calls=[]
    def install(handler):
        def post(url,**kw): calls.append(url); return handler(url)
        monkeypatch.setattr(httpx,'post',post)
    return calls,install

def test_quota_makes_one_call_and_never_tries_other_models(client,gemini):
    calls,install=gemini; h=register(client); setup_house(client,h)
    install(lambda url:httpx.Response(429,json={}))
    client.post('/api/ai/chat',headers=h,json={'message':'??'})
    assert len(calls)==1 and settings.gemini_model in calls[0]

def test_service_unavailable_retries_once_on_same_model(client,gemini):
    calls,install=gemini; h=register(client); setup_house(client,h)
    install(lambda url:httpx.Response(503,json={}))
    client.post('/api/ai/chat',headers=h,json={'message':'là sao'})
    assert len(calls)==2 and all(settings.gemini_model in url for url in calls)

def test_timeout_fails_fast_without_retry(client,gemini):
    calls,install=gemini; h=register(client); setup_house(client,h)
    def slow(url): raise httpx.ReadTimeout('slow')
    install(slow)
    r=client.post('/api/ai/chat',headers=h,json={'message':'là sao'})
    assert len(calls)==1 and r.status_code==504
    assert r.json()['error']['code']=='GEMINI_TIMEOUT'

def test_quota_degrades_to_local_household_answer(client,ready,gemini):
    calls,install=gemini; h,_,_=ready
    install(lambda url:httpx.Response(429,json={}))
    response=client.post('/api/ai/chat',headers=h,json={'message':'tháng này tôi dùng bao nhiêu số điện'})
    assert response.status_code==429 and response.json()['error']['code']=='GEMINI_QUOTA'
    assert 'metadata' not in response.json()

@pytest.mark.parametrize('message',['phân tích mức sử dụng của tôi','mức sử dụng điện nhà mình'])
def test_degraded_usage_analysis_uses_readings(client,ready,gemini,message):
    calls,install=gemini; h,_,meter=ready
    assert reading(client,h,meter).status_code==201
    install(lambda url:httpx.Response(429,json={}))
    response=client.post('/api/ai/chat',headers=h,json={'message':message})
    assert response.status_code==429 and response.json()['error']['code']=='GEMINI_QUOTA'

def test_degraded_price_question_never_invents_current_price(client,ready,gemini):
    calls,install=gemini; h,_,_=ready
    install(lambda url:httpx.Response(429,json={}))
    response=client.post('/api/ai/chat',headers=h,json={'message':'giá điện Thái Nguyên hiện nay'})
    assert response.status_code==429 and response.json()['error']['code']=='GEMINI_QUOTA'

def test_degraded_image_does_not_fabricate_reading(client,ready,gemini):
    import base64,io
    from PIL import Image
    calls,install=gemini; h,_,_=ready
    install(lambda url:httpx.Response(429,json={}))
    buffer=io.BytesIO();Image.new('RGB',(8,8),'white').save(buffer,format='PNG')
    response=client.post('/api/ai/chat',headers=h,json={'message':'đọc giúp','image_base64':base64.b64encode(buffer.getvalue()).decode()})
    assert response.status_code==429 and response.json()['error']['code']=='GEMINI_QUOTA'

@pytest.mark.parametrize('message',['??','là sao','phân tích mức sử dụng của tôi'])
def test_rag_not_used_for_household_or_vague_questions(client,ready,gemini,monkeypatch,message):
    calls,install=gemini; h,_,_=ready
    monkeypatch.setattr(settings,'knowledge_rag_enabled',True)
    monkeypatch.setattr(knowledge,'retrieve',lambda *a:pytest.fail('RAG must not run for '+message))
    install(lambda url:reply())
    r=client.post('/api/ai/chat',headers=h,json={'message':message})
    assert r.status_code==200 and r.json()['metadata']['provider']=='gemini'
    assert len(calls)==1 and calls[0].endswith(':generateContent')

def documents():
    return {'mode':'HYBRID','status':'FOUND','warnings':[],'current_price':True,'documents':[{'id':'abc','ref':'knowledge:abc',
        'title':'Biểu giá bán lẻ điện','url':'https://www.evn.com.vn/gia','version_id':'v1','position':0,
        'metadata':{'effective_from':'2025-05-10','scope':'NATIONAL'},'checked_at':'2026-10-28','content':'Bậc 1: 0 - 50 kWh.'}]}

def test_rag_used_for_tariff_question_with_one_generation(client,ready,gemini,monkeypatch):
    calls,install=gemini; h,_,_=ready
    monkeypatch.setattr(settings,'knowledge_rag_enabled',True)
    queries=[]
    monkeypatch.setattr(knowledge,'retrieve',lambda q:queries.append(q) or documents())
    install(lambda url:httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(
        {'requested_task':'EXPLAIN','status':'ANSWERED','message':'Theo EVN [1].','evidence_refs':['knowledge:abc']})}]}}]}))
    body=client.post('/api/ai/chat',headers=h,json={'message':'giá điện thái nguyên hiện nay'}).json()
    assert queries and queries[0].current_price and queries[0].location=='Thái Nguyên'
    assert len(calls)==1 and body['sources'][0]['type']=='knowledge'

def test_rag_documents_survive_gemini_quota(client,ready,gemini,monkeypatch):
    calls,install=gemini;h,_,_=ready
    monkeypatch.setattr(settings,'knowledge_rag_enabled',True)
    monkeypatch.setattr(knowledge,'retrieve',lambda q:documents())
    install(lambda url:httpx.Response(429,json={}))
    response=client.post('/api/ai/chat',headers=h,json={'message':'giá điện thái nguyên hiện nay'})
    assert response.status_code==429 and response.json()['error']['code']=='GEMINI_QUOTA'

def test_invalid_evidence_degrades_instead_of_failing(client,ready,monkeypatch):
    h,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(StructuredGemini,'respond',lambda self,**kw:Reply(requested_task='OTHER',status='ANSWERED',message='x',evidence_refs=['bill:invented']))
    r=client.post('/api/ai/chat',headers=h,json={'message':'tổng quan nhà tôi'})
    assert r.status_code==502 and r.json()['error']['code']=='GEMINI_INVALID_EVIDENCE'

@pytest.mark.parametrize('message,needs,utility,location,current',[
    ('giá điện thái nguyên hiện nay',True,'ELECTRICITY','Thái Nguyên',True),
    ('Giải thích đơn vị điện năng kWh là gì',True,'ELECTRICITY',None,False),
    ('biểu giá nước Hà Nội',True,'WATER','Hà Nội',True),
    ('phân tích mức sử dụng của tôi',False,None,None,False),
    ('??',False,None,None,False),
])
def test_public_query_is_local(monkeypatch,message,needs,utility,location,current):
    monkeypatch.setattr(httpx,'post',lambda *a,**k:pytest.fail('classification must not call Gemini'))
    q=knowledge.public_query(message,[])
    assert (q.needs_public_knowledge,q.utility,q.location,q.current_price)==(needs,utility,location,current)
    if location: assert 'nguyen' not in q.query.lower() and 'hien nay' not in q.query.lower()

def test_short_follow_up_inherits_public_topic():
    history=[{'role':'user','message':'giá điện thái nguyên hiện nay'},{'role':'assistant','message':'...'}]
    q=knowledge.public_query('là sao',history)
    assert q.needs_public_knowledge and q.location=='Thái Nguyên'
    assert not knowledge.public_query('phân tích mức sử dụng của tôi',history).needs_public_knowledge
