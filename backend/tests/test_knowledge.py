"""Public corpus boundaries and transforms; no provider/network dependency."""
from datetime import date
import pytest
from app.knowledge.transform import chunks, publication, fuse, normalize
from app.knowledge.crawler import validate_url
from app.knowledge.crawler import extract

def test_inline_price_table_is_read_as_data_with_old_and_new_headers():
    html='''<html><main><h1>Biểu giá thử nghiệm</h1><script>
    const residentialTableHeaders = ["Nhóm", "Giá cũ đồng/kWh", "Giá mới đồng/kWh"];
    const residentialElectricityData = [{group:"Sinh hoạt",values:[{desc:"Bậc thử",oldPrice:1234,newPrice:1567,},],}];
    </script></main></html>'''
    text,blocks,_=extract(html.encode(),'text/html')
    assert 'Bậc thử' in text and '1234' in text and '1567' in text
    assert 'Giá cũ đồng/kWh' in text and 'Giá mới đồng/kWh' in text
    assert any('<table' in b and '1567' in b for b in blocks)
    assert 'const residential' not in text

def test_inline_price_expressions_are_never_executed_or_published_as_numbers():
    html='''<main><script>const residentialTableHeaders=["a","b","c"];
    const residentialElectricityData=[{group:"x",values:[{desc:"x",oldPrice:1,newPrice:fetch("https://evil.test")}]}];</script></main>'''
    text,_,_=extract(html.encode(),'text/html')
    assert 'evil.test' not in text


def test_url_boundary_checks_every_resolved_address():
    resolve = lambda host, port: ['93.184.216.34']
    assert validate_url('https://www.evn.com.vn/a', ['evn.com.vn'], resolve)
    for url in ['http://evn.com.vn/a', 'https://evn.com.vn.evil.test/a',
                'https://user@evn.com.vn/a', 'https://evn.com.vn:8443/a']:
        with pytest.raises(ValueError): validate_url(url, ['evn.com.vn'], resolve)
    with pytest.raises(ValueError):
        validate_url('https://evn.com.vn/a', ['evn.com.vn'], lambda *_: ['93.184.216.34','127.0.0.1'])


def test_chunks_preserve_tables_and_limit_overlap():
    blocks = [' '.join(['Nội dung điện nước'] * 200), '<table><tr><th>Bậc</th><th>VND/kWh</th></tr><tr><td>1</td><td>2.000</td></tr></table>']
    result = chunks(blocks)
    assert any(blocks[1] in c for c in result)
    assert len(result) > 1
    assert normalize('ĐIỆN nước') == 'dien nuoc'

def test_aspnet_form_wrapper_does_not_destroy_article():
    html='<html><main><form><input name="__VIEWSTATE"><div class="chitiettinbai"><h2>Công tơ điện</h2><p>Đọc chỉ số tổng trên công tơ để xác định lượng điện sử dụng trong kỳ.</p></div></form></main></html>'
    text,blocks,kind=extract(html.encode(), 'text/html')
    assert 'Đọc chỉ số tổng' in text
    assert '__VIEWSTATE' not in text


def test_pricing_without_explicit_dates_scope_stays_pending():
    assert publication('PRICES', {'effective_from':None,'scope':None}, 'Readable') == 'PENDING_REVIEW'
    assert publication('PRICES', {'effective_from':None,'scope':'Hà Nội'}, 'Readable') == 'PENDING_REVIEW'
    assert publication('PRICES', {'effective_from':'2026-01-01','scope':'NATIONAL','conflicts':[]}, 'Readable') == 'PUBLISHED'
    assert publication('GUIDANCE', {}, '') == 'PENDING_REVIEW'
    assert publication('GUIDANCE', {}, 'Hướng dẫn đọc công tơ có căn cứ.') == 'PUBLISHED'
    assert publication('PRICES', {'effective_from':'2026-01-01','scope':'NATIONAL','conflicts':['VAT']}, 'Readable') == 'PENDING_REVIEW'


def test_rrf_merges_duplicates_and_keeps_both_retrievers():
    result = fuse([{'id':'a'},{'id':'b'}], [{'id':'b'},{'id':'c'}])
    assert [r['id'] for r in result] == ['b','a','c']

def test_metadata_does_not_confuse_issued_date_or_issuer_with_scope():
    from app.knowledge.service import validate_metadata
    text='Quyết định số 123 ngày 09/5/2025 của Bộ Công Thương'
    meta={'effective_from':'2025-05-09','effective_to':None,'published_at':None,
          'effective_quote':text,'scope':'NATIONAL','scope_quote':'Bộ Công Thương','utility':'ELECTRICITY'}
    result=validate_metadata(meta,text)
    assert result['effective_from'] is None and result['scope'] is None

def test_locality_and_dates_must_match_actual_quoted_expression():
    from app.knowledge.service import validate_metadata
    text='Giá nước áp dụng tại Hà Nội. Có hiệu lực từ ngày 10/05/2025 đến ngày 09/06/2026.'
    meta={'effective_from':'2026-05-09','effective_to':'2025-05-10','published_at':None,
          'effective_quote':text,'scope':'Thái Nguyên','scope_quote':'Giá nước áp dụng tại Hà Nội.','utility':'WATER'}
    result=validate_metadata(meta,text)
    assert result['scope'] is None
    assert result['effective_from'] is None
    assert result.get('effective_to') is None

def test_quoted_price_facts_are_not_invented_and_interval_is_ordered():
    from app.knowledge.service import validate_metadata
    text='Áp dụng trên toàn quốc. Có hiệu lực từ ngày 10/05/2025. Bậc 1: 2.000 đồng/kWh.'
    meta={'topic':'PRICES','effective_from':'2025-05-10','effective_to':'2024-01-01','published_at':None,
          'effective_quote':'Có hiệu lực từ ngày 10/05/2025.','scope':'NATIONAL','scope_quote':'Áp dụng trên toàn quốc.',
          'utility':'ELECTRICITY','price_category':'RESIDENTIAL','price_facts':[
              {'label':'Bậc 1','amount':'2000','unit':'VND/kWh','quote':'Bậc 1: 2.000 đồng/kWh.'},
              {'label':'Bậc 1','amount':'3000','unit':'VND/kWh','quote':'Bậc 1: 2.000 đồng/kWh.'}]}
    result=validate_metadata(meta,text)
    assert result['effective_from']=='2025-05-10' and result['effective_to'] is None
    assert 'INVALID_EFFECTIVE_INTERVAL' in result['conflicts']
    assert len(result['price_facts'])==1 and result['price_facts'][0]['amount']=='2000'


def test_admin_knowledge_requires_admin_before_database_access(client, ready):
    headers, _, _ = ready
    assert client.get('/api/admin/knowledge/sources').status_code == 401
    assert client.get('/api/admin/knowledge/sources', headers=headers).status_code == 403


def test_rag_supplies_public_evidence_without_search(client,ready,monkeypatch):
    from app.config import settings
    from app.ai.contracts import Reply
    from app.ai.gemini_structured import StructuredGemini
    from app.ai.gemini import GeminiProvider
    from app.knowledge import service as knowledge
    headers,_,_=ready
    monkeypatch.setattr(settings,'llm_provider','gemini')
    monkeypatch.setattr(settings,'knowledge_rag_enabled',True)
    monkeypatch.setattr(knowledge,'public_query',lambda *a:knowledge.KnowledgeQuery(needs_public_knowledge=True,
        query='đơn vị điện năng',utility='ELECTRICITY',location=None,as_of=None,current_price=False))
    monkeypatch.setattr(knowledge,'retrieve',lambda *a:{'mode':'HYBRID','status':'FOUND','warnings':[],
        'current_price':False,'documents':[{'id':'abc','ref':'knowledge:abc','title':'Hướng dẫn EVN',
        'url':'https://www.evn.com.vn/','version_id':'v1','position':0,'metadata':{},'checked_at':'2026-10-28',
        'content':'Nội dung gốc để giải thích đơn vị điện năng.'}]})
    monkeypatch.setattr(GeminiProvider,'search_tariff',lambda *a,**k:pytest.fail('Search must not be needed'))
    def respond(self,**kwargs):
        assert kwargs['overview']['public_knowledge']['documents'][0]['ref']=='knowledge:abc'
        return Reply(requested_task='EXPLAIN',status='ANSWERED',message='Mình giải thích dựa trên hướng dẫn của EVN. [1]',evidence_refs=['knowledge:abc'])
    monkeypatch.setattr(StructuredGemini,'respond',respond)
    result=client.post('/api/ai/chat',headers=headers,json={'message':'Giải thích đơn vị điện năng'})
    assert result.status_code==200,result.text
    assert result.json()['metadata']['retrieval']['mode']=='HYBRID'
    assert result.json()['sources'][0]['type']=='knowledge'
