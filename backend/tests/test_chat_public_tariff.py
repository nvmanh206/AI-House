import pytest

from app.ai.contracts import Reply
from app.ai.gemini import GeminiProvider
from app.ai.gemini_structured import StructuredGemini
from app.config import settings


@pytest.mark.parametrize('message',['mình cần xem giá điện thái nguyên hiện nay','giá điện thái nguyên đang áp dụng'])
def test_public_tariff_reaches_search_then_natural_reply(client,ready,monkeypatch,message):
    headers,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(settings,'knowledge_rag_enabled',False)
    calls=[]
    def search(self,**kw):
        calls.append(kw)
        return {'message':'Nguồn chính thức đã xác minh theo ngày yêu cầu.',
                'sources':[{'type':'web','index':1,'title':'EVN','url':'https://www.evn.com.vn/'}],
                'metadata':{'grounded':True,'retrieved_at':'2026-10-28'}}
    monkeypatch.setattr(GeminiProvider,'search_tariff',search)
    def respond(self,**kw):
        evidence=kw['overview'].get('public_tariff')
        assert evidence is not None and evidence['grounded']
        return Reply(requested_task='EXPLAIN',status='ANSWERED',message='Mình đã tra nguồn giá áp dụng cho Thái Nguyên; đây là phần giải thích theo yêu cầu của bạn.',evidence_refs=['public_tariff:1'])
    monkeypatch.setattr(StructuredGemini,'respond',respond)
    response=client.post('/api/ai/chat',headers=headers,json={'message':message})
    assert response.status_code==200,response.text
    assert calls[0]['utility']=='ELECTRICITY' and calls[0]['location']=='Thái Nguyên'
    assert set(calls[0]) <= {'utility','day','location','customer_group','query_type'}
    assert response.json()['sources'][0]['type']=='web'
    assert response.json()['metadata']['public_tariff']['grounded']


def test_missing_search_evidence_is_missing_data_not_out_of_scope(client,ready,monkeypatch):
    headers,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(settings,'knowledge_rag_enabled',False)
    monkeypatch.setattr(GeminiProvider,'search_tariff',lambda *a,**kw:{'message':'OLD CANNED FALLBACK','sources':[],
        'metadata':{'grounded':False,'error_code':'GEMINI_SEARCH_QUOTA'}})
    def respond(self,**kw):
        assert kw['overview']['public_tariff']['grounded'] is False
        assert 'OLD CANNED FALLBACK' not in str(kw)
        return Reply(requested_task='EXPLAIN',status='INSUFFICIENT_DATA',message='Lượt tra cứu này chưa xác minh được giá hiện hành; mình có thể phân biệt biểu giá đã lưu với giá công bố.',evidence_refs=[])
    monkeypatch.setattr(StructuredGemini,'respond',respond)
    response=client.post('/api/ai/chat',headers=headers,json={'message':'Giá điện Thái Nguyên hiện nay?'})
    assert response.status_code==200,response.text
    assert response.json()['status']=='INSUFFICIENT_DATA'
