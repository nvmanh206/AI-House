import httpx
import json
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

def test_chat_calls_gemini_with_user_overview_and_no_tools(client,monkeypatch):
    h=register(client);setup_house(client,h)
    monkeypatch.setattr(settings,'llm_provider','gemini');monkeypatch.setattr(settings,'gemini_api_key','test-key')
    calls=[]
    def post(url,**kwargs):
        calls.append(kwargs['json']);return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'requested_task':'OTHER','status':'ANSWERED','message':'Bạn có thể bắt đầu từ chỉ số đã ghi.','evidence_refs':[]})}]}}]})
    monkeypatch.setattr(httpx,'post',post)
    r=client.post('/api/ai/chat',headers=h,json={'message':'Mình nên bắt đầu như thế nào?'})
    assert r.status_code==200 and r.json()['metadata']['provider']=='gemini'
    assert 'tools' not in calls[0] and 'accounts' in str(calls[0])
    assert 'email' not in str(calls[0])
    assert 'Nhà Mình' in calls[0]['systemInstruction']['parts'][0]['text']

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
    assert r.status_code == 429 and r.json()['error']['code']=='GEMINI_QUOTA'
    error=db.query(AIAnalysis).filter_by(analysis_type='ERROR').one()
    assert error.result_json['status']=='error' and error.result_json['code']=='GEMINI_QUOTA'
