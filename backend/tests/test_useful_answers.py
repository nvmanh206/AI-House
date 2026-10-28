import httpx
import json
import pytest
from app.config import settings
from app.ai.router import route
from app.ai.provider import GeminiProvider
from conftest import register,setup_house,reading

@pytest.mark.parametrize('message,expected',[
 ('kWh là gì?','1 số điện'),
 ('Cách đọc công tơ?','chỉ số mới'),
 ('Cách tính tiền điện?','từng bậc'),
 ('Điện được tính theo bậc thang như thế nào?','từng bậc'),
 ('Làm sao tiết kiệm điện?','gợi ý chung'),
])
def test_basic_questions_use_gemini_without_canned_answer(client,monkeypatch,message,expected):
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(settings,'gemini_api_key','test-key')
    generated = 'Nội dung sinh riêng cho câu hỏi: ' + message
    def post(*a,**kw):
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'requested_task':'EXPLAIN','status':'ANSWERED','message':generated,'evidence_refs':[]})}]}}]})
    monkeypatch.setattr(httpx,'post',post)
    r=client.post('/api/ai/chat',headers=h,json={'message':message})
    assert r.status_code==200 and r.json()['metadata']['provider']=='gemini'
    assert generated == r.json()['message']

def test_quota_fallback_has_labeled_local_tariff(client,ready,monkeypatch):
    h,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    calls=[]
    def post(*a,**kw):calls.append(kw);return httpx.Response(429,json={})
    monkeypatch.setattr(httpx,'post',post)
    r=client.post('/api/ai/chat',headers=h,json={'message':'giá điện Thái Nguyên'})
    body=r.json()
    # Search and natural explanation are separate calls; the fallback is labeled configured data, not a price claim.
    assert r.status_code==429 and len(calls)==2
    assert body['error']['code']=='GEMINI_QUOTA' and 'message' not in body

def test_no_data_quota_fallback_does_not_invent_price(client,monkeypatch):
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    monkeypatch.setattr(httpx,'post',lambda *a,**kw:httpx.Response(429,json={}))
    body=client.post('/api/ai/chat',headers=h,json={'message':'giá điện Thái Nguyên'}).json()
    assert body['error']['code']=='GEMINI_QUOTA' and 'message' not in body

@pytest.mark.parametrize('count',[0,1])
def test_forecast_explains_remaining_periods(client,ready,count):
    h,_,meter=ready
    if count: assert reading(client,h,meter).status_code==201
    body=client.post('/api/ai/chat',headers=h,json={'message':'Tháng tới tiền điện khoảng bao nhiêu?'}).json()
    assert f'có {count} kỳ' in body['message']
    assert f'nhập thêm {2-count} kỳ' in body['message']
    assert body['metadata']['result']['available'] is False

def test_local_tariff_explicit_no_search(client,ready,monkeypatch):
    h,_,_=ready
    def forbidden(*a,**kw):raise AssertionError('Local tariff should not call Search')
    monkeypatch.setattr(httpx,'post',forbidden)
    r=client.post('/api/ai/chat',headers=h,json={'message':'biểu giá điện trong hệ thống'})
    assert r.status_code==200 and r.json()['intent']=='CONFIGURED_TARIFF'
    assert 'DỮ LIỆU DEMO' in r.json()['message']
    assert route('biểu giá trong hệ thống')=='configured_tariff'

def test_current_prices_still_use_verification():
    assert route('Giá điện hiện nay là bao nhiêu?')=='public_tariff'
    assert route('Cách tính tiền điện theo giá mới nhất')=='public_tariff'
