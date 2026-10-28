"""Live RAG acceptance using existing disposable System database, never utility_app."""
import argparse,json,os,sys,base64,time
from pathlib import Path
from uuid import uuid4
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'.local/system-test-state.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('action',choices=['serve','exercise']);args=parser.parse_args()
if args.action=='serve':
    for k,v in dotenv_values(ROOT/'backend/.env').items():
        if v is not None: os.environ[k]=v
    os.environ.update(DATABASE_URL=state['database_url'],JWT_SECRET=state['jwt_secret'],APP_ENV='test',
        LLM_PROVIDER='gemini',KNOWLEDGE_RAG_ENABLED='true',GEMINI_SEARCH_ENABLED='false',
        REFRESH_COOKIE_NAME='utility_knowledge_refresh',FRONTEND_URL='http://127.0.0.1:3112',RATE_LIMIT_ENABLED='false')
    sys.path.insert(0,str(ROOT/'backend'));os.chdir(ROOT/'backend')
    import uvicorn
    uvicorn.run('app.main:app',host='127.0.0.1',port=8112)
else:
    import httpx
    from sqlalchemy import create_engine,text
    assert state['database_url'].rsplit('/',1)[-1].endswith('_test')
    fixture={'email':'knowledge-'+uuid4().hex[:10]+'@example.com','password':'SystemTestOnly2026!'}
    with httpx.Client(base_url='http://127.0.0.1:8112/api',timeout=180) as client:
        def call(method,path,data=None,status=200):
            for attempt in range(3):
                r=client.request(method,path,json=data)
                if r.status_code!=503 or path!='/ai/chat' or attempt==2: break
                print('Gemini temporarily unavailable; bounded live-test retry.',flush=True)
                time.sleep(2)
            if r.status_code!=status:
                print('Acceptance failed',path,r.status_code,r.json().get('error',{}).get('code'));raise SystemExit(1)
            return r.json()
        auth=call('POST','/auth/register',{**fixture,'full_name':'RAG acceptance'},201)
        client.headers['Authorization']='Bearer '+auth['access_token']
        call('POST','/households',{'name':'RAG system acceptance','accounts':[{**state['account'],'initial_reading':'0'}]},201)
        engine=create_engine(state['database_url'])
        with engine.begin() as db: db.execute(text("UPDATE users SET role='ADMIN' WHERE email=:email"),{'email':fixture['email']})
        def counts():
            with engine.connect() as db:
                return {table:db.execute(text('SELECT count(*) FROM '+table)).scalar() for table in ('meter_readings','bills','payments')}
        before=counts()
        response=call('POST','/ai/chat',{'message':'VNeID có hỗ trợ thay đổi chủ thể hợp đồng mua bán điện không?'})
        assert response['metadata']['retrieval']['mode']=='HYBRID',response['metadata']['retrieval']
        assert response['status']=='ANSWERED',response['status']
        assert any(s['type']=='knowledge' for s in response['sources'])
        followup=call('POST','/ai/chat',{'message':'Còn yêu cầu cấp điện trở lại thì sao?', 'conversation_id':response['metadata']['conversation_id']})
        assert followup['status']=='ANSWERED' and any(s['type']=='knowledge' for s in followup['sources'])
        missing=call('POST','/ai/chat',{'message':'Giá nước sinh hoạt hiện hành ở Thái Nguyên là bao nhiêu?'})
        assert missing['status'] in ('INSUFFICIENT_DATA','NEEDS_CLARIFICATION')
        assert not any(s['type']=='knowledge' for s in missing['sources'])
        unrelated=call('POST','/ai/chat',{'message':'Hãy viết một bài quảng cáo bán giày thể thao.'})
        assert unrelated['status']=='OUT_OF_SCOPE'
        image=ROOT/'.local/multimodal-test-invoice.png'
        if image.exists():
            reading=call('POST','/ai/chat',{'message':'Đọc thông tin trên ảnh hóa đơn này; chỉ đọc, không cần đối chiếu.',
                'image_base64':'data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()})
            assert reading['metadata']['result']['extracted_data'] is not None
        assert counts()==before
        call('GET','/admin/knowledge/sources')
        saved={**fixture,'api':'http://127.0.0.1:8112/api','frontend':'http://127.0.0.1:3112',
               'status':response['status'],'source_count':len(response['sources']),'business_counts_unchanged':True,
               'followup':followup['status'],'missing_source':missing['status'],'out_of_scope':unrelated['status'],
               'image_regression':image.exists()}
        (ROOT/'.local/knowledge-system-result.json').write_text(json.dumps(saved),encoding='utf-8')
        (ROOT/'.local/knowledge-chat-result.json').write_text(json.dumps(response,ensure_ascii=False,default=str),encoding='utf-8')
        print('Real Gemini + hybrid PostgreSQL RAG + source refs + unchanged business rows: PASS')
