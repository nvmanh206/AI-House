import os
os.environ['JWT_SECRET']='test-only-secret-012345678901234567890'
os.environ['DATABASE_URL']=os.environ.get('TEST_DATABASE_URL','sqlite://')
os.environ['APP_ENV']='test'
os.environ['LLM_PROVIDER']='deterministic'
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db import Base,get_db
from app.main import app,attempts
from app.models import Tariff,TariffTier
from datetime import date

@pytest.fixture
def db():
    url=os.environ['DATABASE_URL']
    engine=create_engine(url,**({'connect_args':{'check_same_thread':False},'poolclass':StaticPool} if url=='sqlite://' else {}))
    if url=='sqlite://':
        from sqlalchemy import event
        @event.listens_for(engine,'connect')
        def fk(c,_): c.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    connection=engine.connect(); tx=connection.begin()
    factory=sessionmaker(bind=connection,join_transaction_mode='create_savepoint',expire_on_commit=False)
    with factory() as session:
        yield session
    tx.rollback(); connection.close(); engine.dispose()

@pytest.fixture
def client(db):
    def override():
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback(); raise
    app.dependency_overrides[get_db]=override; attempts.clear()
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()

def register(client,email='a@example.com'):
    r=client.post('/api/auth/register',json={'email':email,'password':'StrongPass123!','full_name':'Nguyễn An'})
    assert r.status_code==201,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}

def setup_house(client,headers):
    r=client.post('/api/households',headers=headers,json={'name':'Gia đình An','accounts':[{'utility_type':'ELECTRICITY','provider_name':'Demo','initial_reading':'100'}]})
    assert r.status_code==201,r.text
    return r.json()

@pytest.fixture
def ready(client,db):
    headers=register(client); house=setup_house(client,headers)
    tariff=Tariff(utility_type='ELECTRICITY',provider_name='Demo',name='Giá demo',version='v1',effective_from=date(2020,1,1))
    db.add(tariff); db.flush()
    db.add_all([TariffTier(tariff_id=tariff.id,from_value=0,to_value=50,unit_price=1000,order_index=0),TariffTier(tariff_id=tariff.id,from_value=50,to_value=None,unit_price=2000,order_index=1)]); db.commit()
    meter=client.get('/api/meters',headers=headers).json()[0]
    return headers,house,meter

def reading(client,headers,meter,month=1,current=180):
    return client.post('/api/readings',headers=headers,json={'meter_id':meter['id'],'year':2026,'month':month,'current_reading':current,'reading_date':f'2026-{month:02}-25'})
