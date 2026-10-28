"""Live admin/API acceptance; existing disposable login, no business mutations."""
import json
from pathlib import Path
import httpx

root=Path(__file__).resolve().parents[1]
fixture=json.loads((root/'.local/knowledge-system-result.json').read_text())
result={}
with httpx.Client(base_url=fixture['api'],timeout=180) as client:
    login=client.post('/auth/login',json={'email':fixture['email'],'password':fixture['password']})
    login.raise_for_status();client.headers['Authorization']='Bearer '+login.json()['access_token']
    docs=client.get('/admin/knowledge/documents');docs.raise_for_status();docs=docs.json()
    pending=next(d for d in docs if d['status']=='PENDING_REVIEW' and d['metadata'].get('topic')=='PRICES')
    detail=client.get('/admin/knowledge/versions/'+pending['version_id']);detail.raise_for_status()
    assert not detail.json()['readiness']['can_publish'] and detail.json()['readiness']['missing']
    denied=client.patch('/admin/knowledge/versions/'+pending['version_id'],json={'status':'PUBLISHED'})
    assert denied.status_code==422
    original=client.get('/admin/knowledge/versions/'+pending['version_id']+'/original')
    original.raise_for_status();assert original.content and 'filename' in original.headers['content-disposition']
    result.update(preview=True,unverified_publish_rejected=True,original_bytes=len(original.content))
    source_url='https://cskh.evnspc.vn/TraCuu/ThongTinGiaDien'
    sources=client.get('/admin/knowledge/sources').json()
    source=next((s for s in sources if source_url in s['seeds']),None)
    if source is None:
        response=client.post('/admin/knowledge/sources',json={'name':'EVNSPC · Bảng giá điện công khai','domains':['evnspc.vn'],
            'seeds':[source_url],'topic':'PRICES','seed_mode':'DOCUMENT','utility':'ELECTRICITY','enabled':True})
        response.raise_for_status();source=response.json()
    response=client.post('/admin/knowledge/sources/'+source['id']+'/crawl');response.raise_for_status()
    result['crawl_job']=response.json()
    query=client.post('/admin/knowledge/retrieve',json={'query':'VNeID dịch vụ điện thay đổi chủ thể hợp đồng','utility':'ELECTRICITY'})
    query.raise_for_status();assert query.json()['documents']
    result['retrieval_mode']=query.json()['mode'];result['retrieved_chunks']=len(query.json()['documents'])
(root/'.local/knowledge-actions-result.json').write_text(json.dumps(result,default=str),encoding='utf-8')
print('Preview readiness, reject unverified publication, original download, crawl queue, real retrieval: PASS')
