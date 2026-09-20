"""Explicit demo-only seed; never invoked by migrations or normal startup."""
import argparse
from datetime import date
from decimal import Decimal
from app.config import settings
from app.db import SessionLocal
from app.models import *
from app.repository import Repository
from app.services import HouseholdService,today,day_in_month
from app.security import hasher,issue
from app.schemas import Onboarding,ReadingInput,TariffInput,PaymentInput
from app.admin_service import AdminService
from app.notification_service import NotificationService

def seed():
    if settings.app_env=='production': raise RuntimeError('Demo seed is disabled in production')
    with SessionLocal.begin() as db:
        repo=Repository(db)
        if repo.one(User,email='demo@example.com'):
            print('Demo already exists; no data changed.'); return
        user=repo.add(User,email='demo@example.com',full_name='Nguyễn Minh An',password_hash=hasher.hash('DemoHouse123!'))
        admin=repo.one(User,email='admin@example.com') or repo.add(User,email='admin@example.com',full_name='Quản trị viên Demo',password_hash=hasher.hash('AdminHouse123!'),role='ADMIN')
        issue(repo,user); session=repo.one(AuthSession,user_id=user.id)
        service=HouseholdService(repo,(user,session))
        admin_service=AdminService(repo,(admin,session))
        for utility,name,category,province,prices in [('ELECTRICITY','Điện Demo','RESIDENTIAL_1PHASE',None,[1800,2100,2500,2900,3300,3500]),('ELECTRICITY','Điện Demo','RESIDENTIAL_3PHASE',None,[2200,2600,3000,3400,3800,4100]),('WATER','Nước Demo','RESIDENTIAL','TP. Hồ Chí Minh',[6000,8000,10000])]:
            bounds=[0,50,100,200,300,400] if utility=='ELECTRICITY' else [0,10,20]
            admin_service.tariff(TariffInput(utility_type=utility,provider_name=name,tariff_category=category,province=province,name=f'Biểu giá {name} ({category}) minh họa',version='demo-1',effective_from=date(2020,1,1),tiers=[{'from_value':lower,'to_value':bounds[i+1] if i+1<len(bounds) else None,'unit_price':prices[i]} for i,lower in enumerate(bounds)]))
        house=service.onboard(Onboarding(name='Gia đình Minh An',address='12 Nguyễn Văn Cừ, TP. Hồ Chí Minh',province='TP. Hồ Chí Minh',member_count=4,accounts=[{'utility_type':'ELECTRICITY','provider_name':'Điện Demo','tariff_category':'RESIDENTIAL_1PHASE','province':'TP. Hồ Chí Minh','customer_code':'DEMO-ELECTRIC-001','initial_reading':1200,'billing_day':25,'due_day':28},{'utility_type':'WATER','provider_name':'Nước Demo','tariff_category':'RESIDENTIAL','province':'TP. Hồ Chí Minh','customer_code':'DEMO-WATER-001','initial_reading':200,'billing_day':25,'due_day':28}]))
        electricity=[210,228,245,232,267,290,278,305,320,296,282,318]
        water=[14,15,16,15,17,18,17,19,18,17,16,18]
        day=today()
        for meter in repo.all(Meter,household_id=house['id']):
            cumulative=meter.initial_reading
            for i in range(12):
                index=day.year*12+day.month-1-11+i
                year,month=index//12,index%12+1
                cumulative+=Decimal((electricity if meter.utility_type=='ELECTRICITY' else water)[i])
                reading_day=min(day,day_in_month(year,month,25))
                result=service.reading(ReadingInput(meter_id=meter.id,year=year,month=month,current_reading=cumulative,reading_date=reading_day))
                if i<10: service.pay(PaymentInput(bill_id=result['bill']['id'],reference='DEMO-MANUAL'))
        NotificationService(repo).run()
        session.revoked=True
        print('Seeded demo user, admin, household, 24 readings/bills, illustrative tariffs and notifications.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--demo',action='store_true',required=True);parser.parse_args();seed()
