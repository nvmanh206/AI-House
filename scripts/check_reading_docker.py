"""Run via docker exec -i nha-minh-backend python -; every fixture rolls back."""
from uuid import uuid4
import os
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app
from app.db import get_db

engine=create_engine(settings.database_url)
with engine.connect() as connection:
    before={t:connection.scalar(text('SELECT count(*) FROM '+t)) for t in ('users','meter_readings','bills')}
    connection.rollback()
    tx=connection.begin()
    factory=sessionmaker(bind=connection,join_transaction_mode='create_savepoint',expire_on_commit=False)
    def database():
        with factory() as db:
            try:yield db;db.commit()
            except Exception:db.rollback();raise
    app.dependency_overrides[get_db]=database
    try:
        with TestClient(app) as client:
            response=client.post('/api/auth/register',json={'email':'reading-check-'+uuid4().hex+'@example.com','password':'TestOnlyReading2026!','full_name':'Rollback fixture'})
            assert response.status_code==201,response.text
            headers={'Authorization':'Bearer '+response.json()['access_token']}
            response=client.post('/api/households',headers=headers,json={'name':'Rollback fixture','accounts':[{'utility_type':'ELECTRICITY','provider_name':'Unconfigured test','initial_reading':'0'},{'utility_type':'WATER','provider_name':'Unconfigured test','initial_reading':'0'}]})
            assert response.status_code==201,response.text
            meter=next(m for m in client.get('/api/meters',headers=headers).json() if m['utility_type']=='WATER')
            response=client.post('/api/readings',headers=headers,json={'meter_id':meter['id'],'year':2026,'month':1,'reading_date':'2026-01-25','current_reading':'2223'})
            assert response.status_code==201,response.text
            result=response.json()
            assert result['bill'] is None and result['billing_status']=='TARIFF_NOT_FOUND'
            assert float(result['reading']['consumption'])==2223
            assert len(client.get('/api/readings',headers=headers).json())==1
            assert client.get('/api/bills',headers=headers).json()==[]
            if os.environ.get('CHECK_GEMINI')=='1':
                response=client.post('/api/ai/chat',headers=headers,json={'message':'Phân tích lượng nước tôi đã ghi kỳ tháng 1/2026, nêu rõ khi thiếu dữ liệu so sánh.'})
                assert response.status_code==200,response.text
                answer=response.json()
                assert answer['metadata']['provider']=='gemini' and not answer['metadata']['degraded']
                assert answer['message'] and answer['metadata']['conversation_id']
                response=client.post('/api/ai/chat',headers=headers,json={'message':'Vậy tiền nước kỳ đó là bao nhiêu?', 'conversation_id':answer['metadata']['conversation_id']})
                assert response.status_code==200,response.text
                followup=response.json()
                assert followup['metadata']['provider']=='gemini' and not followup['metadata']['degraded']
                assert followup['status'] in ('INSUFFICIENT_DATA','NEEDS_CLARIFICATION')
                print('Real Gemini analysis and contextual follow-up: PASS; no tariff invented')
    finally:
        app.dependency_overrides.clear();tx.rollback()
    after={t:connection.scalar(text('SELECT count(*) FROM '+t)) for t in before}
    assert before==after
print('Docker PostgreSQL: reading saved, no invented bill, all fixture rows rolled back: PASS')
