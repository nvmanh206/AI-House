import httpx
from app.ai.router import route
from app.ai.registry import SKILLS,TOOLS,instructions
from app.config import settings
from conftest import register,setup_house

def test_identity_without_data(client):
    h=register(client);setup_house(client,h)
    r=client.post('/api/ai/chat',headers=h,json={'message':'bạn là ai'})
    assert r.status_code==200 and r.json()['intent']=='ASSISTANT_IDENTITY'
    assert 'chưa đủ dữ liệu' not in r.json()['message'].lower()

def test_help_combined_utilities(client):
    h=register(client);setup_house(client,h)
    r=client.post('/api/ai/chat',headers=h,json={'message':'bạn có thể giúp mik xem điện nước thái nguyên không'})
    assert r.status_code==200 and r.json()['intent']=='PUBLIC_TARIFF'
    assert 'Thái Nguyên' in r.json()['message'] and 'loại nào' in r.json()['message']

def test_general_chat_calls_gemini_without_database(client,monkeypatch):
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    calls=[]
    def post(url,**kwargs):
        calls.append(kwargs['json']);return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'Xin chào, mình hỗ trợ bạn.'}]}}]})
    monkeypatch.setattr(httpx,'post',post)
    r=client.post('/api/ai/chat',headers=h,json={'message':'Mình nên bắt đầu như thế nào?'})
    assert r.status_code==200 and r.json()['metadata']['provider']=='gemini'
    assert 'tools' not in calls[0] and 'Gia đình An' not in str(calls[0])
    assert 'general_chat' in calls[0]['systemInstruction']['parts'][0]['text']

def test_registry_complete():
    assert 'get_public_tariff' in TOOLS and 'public_tariff' in SKILLS
    for skill in SKILLS: assert instructions(skill)

def test_household_routes_preserved():
    assert route('Tổng quan')=='household_overview'
    assert route('Hóa đơn nào chưa thanh toán?')=='payment_assistant'
    assert route('Tháng tới tiền điện khoảng bao nhiêu?')=='bill_forecast'

def test_search_quota_is_recorded_as_error(client,monkeypatch,db):
    from app.models import AIAnalysis
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    monkeypatch.setattr(httpx,'post',lambda *a,**k:httpx.Response(429,json={'error':{'status':'RESOURCE_EXHAUSTED'}}))
    r=client.post('/api/ai/chat',headers=h,json={'message':'giá điện Thái Nguyên'})
    assert r.json()['metadata']['error_code']=='GEMINI_SEARCH_QUOTA'
    assert db.query(AIAnalysis).first().result_json['status']=='error'
