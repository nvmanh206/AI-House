import httpx
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
def test_basic_without_network_or_readings(client,monkeypatch,message,expected):
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini')
    def forbidden(*a,**kw): raise AssertionError('Basic explanation must not call Gemini/Search')
    monkeypatch.setattr(httpx,'post',forbidden)
    r=client.post('/api/ai/chat',headers=h,json={'message':message})
    assert r.status_code==200 and r.json()['intent']=='BASIC_KNOWLEDGE'
    assert expected in r.json()['message']

def test_quota_fallback_has_labeled_local_tariff(client,ready,monkeypatch):
    h,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    calls=[]
    def post(*a,**kw):calls.append(kw);return httpx.Response(429,json={})
    monkeypatch.setattr(httpx,'post',post)
    r=client.post('/api/ai/chat',headers=h,json={'message':'giá điện Thái Nguyên'})
    body=r.json()
    assert r.status_code==200 and len(calls)==1
    assert 'DỮ LIỆU DEMO' in body['message'] and '2020-01-01' in body['message']
    assert '1,000 VND/kWh' in body['message']
    assert body['sources']==[] and body['metadata']['grounded'] is False
    assert body['metadata']['error_code']=='GEMINI_SEARCH_QUOTA'

def test_no_data_quota_fallback_does_not_invent_price(client,monkeypatch):
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    monkeypatch.setattr(httpx,'post',lambda *a,**kw:httpx.Response(429,json={}))
    body=client.post('/api/ai/chat',headers=h,json={'message':'giá điện Thái Nguyên'}).json()
    assert 'chưa có biểu giá phù hợp' in body['message']
    assert 'từng bậc' in body['message']
    assert body['metadata']['configured_tariffs']==[]

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
