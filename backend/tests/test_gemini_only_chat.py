import pytest
from app.config import settings
from app.ai.gemini_structured import StructuredGemini
from app.security import DomainError
from app.models import AIAnalysis
from app.ai.contracts import Reply

def test_answers_are_exactly_gemini_output_and_followup_receives_history(client,ready,monkeypatch):
    headers,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(settings,'knowledge_rag_enabled',False)
    calls=[]
    messages=['Phân tích riêng từ Gemini.','Câu trả lời tiếp nối từ Gemini.']
    def respond(self,**kwargs):
        calls.append(kwargs)
        return Reply(requested_task='EXPLAIN',status='ANSWERED',message=messages[len(calls)-1],evidence_refs=[])
    monkeypatch.setattr(StructuredGemini,'respond',respond)
    first=client.post('/api/ai/chat',headers=headers,json={'message':'phân tích mức sử dụng điện của tôi'})
    assert first.status_code==200 and first.json()['message']==messages[0]
    second=client.post('/api/ai/chat',headers=headers,json={'message':'tiền điện sẽ hết bao nhiêu','conversation_id':first.json()['metadata']['conversation_id']})
    assert second.status_code==200 and second.json()['message']==messages[1]
    assert second.json()['metadata']['provider']=='gemini'
    assert calls[1]['history'][0]['message']=='phân tích mức sử dụng điện của tôi'
    assert calls[1]['history'][1]['message']==messages[0]

@pytest.mark.parametrize('code,status',[('GEMINI_KEY_REQUIRED',503),('GEMINI_QUOTA',429),('GEMINI_TIMEOUT',504),('GEMINI_INVALID_RESPONSE',502)])
def test_provider_failure_never_returns_a_local_answer_or_saves_fake_context(client,ready,monkeypatch,db,code,status):
    headers,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(settings,'knowledge_rag_enabled',False)
    def fail(*args,**kwargs):raise DomainError(code,'Provider error',status)
    monkeypatch.setattr(StructuredGemini,'respond',fail)
    response=client.post('/api/ai/chat',headers=headers,json={'message':'phân tích mức sử dụng điện của tôi'})
    assert response.status_code==status,response.text
    assert response.json()['error']['code']==code
    assert 'message' not in response.json()
    assert db.query(AIAnalysis).filter_by(analysis_type='CHAT_CONTEXT').count()==0
