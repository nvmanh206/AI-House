from datetime import date
from decimal import Decimal
from app.models import User,Tariff,TariffTier,MeterReading,Bill,HouseholdMember,Notification
from app.repository import Repository
from app.notification_service import NotificationService
from conftest import register,setup_house,reading

def test_missing_tariff_rolls_back(client,ready,db):
    h,_,meter=ready
    for t in db.query(Tariff): t.is_active=False
    db.commit()
    result=reading(client,h,meter)
    assert result.status_code==409
    assert db.query(MeterReading).count()==0
    assert db.query(Bill).count()==0

def test_meter_reactivation_cannot_duplicate(client,ready):
    h,_,meter=ready
    assert client.patch('/api/meters/'+meter['id'],headers=h,json={'name':'Old','is_active':False}).status_code==200
    new=client.post('/api/meters',headers=h,json={'utility_account_id':meter['utility_account_id'],'name':'New','initial_reading':0})
    assert new.status_code==201
    assert client.patch('/api/meters/'+meter['id'],headers=h,json={'name':'Old','is_active':True}).status_code==409

def test_duplicate_account_bill_different_meter(client,ready,db):
    h,_,meter=ready; assert reading(client,h,meter).status_code==201
    client.patch('/api/meters/'+meter['id'],headers=h,json={'name':'Old','is_active':False})
    new=client.post('/api/meters',headers=h,json={'utility_account_id':meter['utility_account_id'],'name':'New'}).json()
    assert reading(client,h,new,current=10).status_code==409
    assert db.query(Bill).count()==1
    assert db.query(MeterReading).count()==1

def test_admin_tariff_validation(client,ready,db):
    h,_,_=ready
    user=db.query(User).first();user.role='ADMIN';db.commit()
    payload={'utility_type':'ELECTRICITY','provider_name':'Demo','name':'Version 2','version':'v2','effective_from':'2026-01-01','tiers':[{'from_value':1,'to_value':None,'unit_price':1000}]}
    assert client.post('/api/admin/tariffs',headers=h,json=payload).status_code==422
    payload['tiers'][0]['from_value']=0
    assert client.post('/api/admin/tariffs',headers=h,json=payload).status_code==201
    assert client.post('/api/admin/tariffs',headers=h,json=payload).status_code==409
    assert client.patch('/api/admin/users/'+user.id,headers=h,json={'is_active':False}).status_code==400

def test_member_removed_loses_context(client,ready):
    h,_,_=ready; other=register(client,'removed@example.com')
    member=client.post('/api/members',headers=h,json={'email':'removed@example.com'}).json()
    house=client.get('/api/households',headers=other).json()[0]
    client.post('/api/households/'+house['id']+'/select',headers=other)
    assert client.get('/api/bills',headers=other).status_code==200
    client.delete('/api/members/'+member['id'],headers=h)
    assert client.get('/api/bills',headers=other).status_code==403
    assert client.post('/api/ai/chat',headers=other,json={'message':'Tổng quan'}).status_code==403

def test_password_change_revokes_sessions(client):
    h=register(client)
    assert client.post('/api/auth/password',headers=h,json={'old_password':'StrongPass123!','new_password':'NewStrongPass123!'}).status_code==200
    assert client.get('/api/auth/me',headers=h).status_code==401
    assert client.post('/api/auth/refresh').status_code==401
    assert client.post('/api/auth/login',json={'email':'a@example.com','password':'NewStrongPass123!'}).status_code==200

def test_invalid_refresh_and_jwt(client):
    assert client.post('/api/auth/refresh').status_code==401
    assert client.get('/api/auth/me',headers={'Authorization':'Bearer invalid'}).status_code==401
    register(client)
    old=client.cookies.get('utility_refresh')
    assert client.post('/api/auth/refresh').status_code==200
    client.cookies.clear();client.cookies.set('utility_refresh',old,path='/api/auth')
    assert client.post('/api/auth/refresh').status_code==401

def test_sources_and_date_validation(client,ready):
    h,_,meter=ready
    payload={'meter_id':meter['id'],'year':2026,'month':1,'reading_date':'2026-02-01','current_reading':200}
    assert client.post('/api/readings',headers=h,json=payload).status_code==422
    payload['reading_date']='2026-01-25';payload['source']='PROVIDER_API'
    assert client.post('/api/readings',headers=h,json=payload).status_code==422

def test_notification_owner_only(client,ready,db):
    h,_,meter=ready;reading(client,h,meter)
    notification=client.get('/api/notifications',headers=h).json()[0]
    other=register(client,'notice@example.com');setup_house(client,other)
    assert client.patch('/api/notifications/'+notification['id']+'/read',headers=other).status_code==404
    assert client.patch('/api/notifications/'+notification['id']+'/read',headers=h).status_code==200

def test_zero_baseline_and_three_bill_comparison(client,ready):
    h,_,meter=ready
    for month,current in [(1,100),(2,100),(3,150)]: assert reading(client,h,meter,month,current).status_code==201
    reply=client.post('/api/ai/chat',headers=h,json={'message':'So sánh tiền điện 3 tháng gần đây.'}).json()
    assert all(period in reply['message'] for period in ['2026-01','2026-02','2026-03'])
    assert len(reply['sources'])==3

def test_statistics_missing_utility_is_not_zero(client,ready):
    h,_,meter=ready;reading(client,h,meter)
    result=client.get('/api/statistics?start=2026-01-01&end=2026-01-31',headers=h).json()
    assert result['summary']['ELECTRICITY']['average']==80
    assert result['summary']['WATER']['average'] is None
    assert result['series'][0]['WATER'] is None
