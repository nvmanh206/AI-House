"""Read-only verification of the explicitly selected household, including real Gemini."""
import os,json
from decimal import Decimal
from types import SimpleNamespace
from app.db import SessionLocal
from app.repository import Repository
from app.models import Household,User
from app.services import HouseholdService
from app.ai.context import build_context
from app.ai.agent import Agent
with SessionLocal() as db:
    repo=Repository(db);house=repo.get(Household,os.environ['BILLING_HOUSEHOLD_ID'])
    auth=(repo.get(User,house.owner_user_id),SimpleNamespace(household_id=house.id))
    service=HouseholdService(repo,auth)
    bills=service.bills();assert bills
    for bill in bills:
        assert Decimal(bill['final_amount'])==sum(Decimal(line['amount']) for line in bill['bill_detail_snapshot']['tiers'])
        assert bill['source']=='SYSTEM_ESTIMATE' and bill['tariff_version_snapshot']['source']['url']
    stats=service.statistics();latest=stats['series'][-1]
    latest_bill=next(b for b in bills if b['period']==latest['period'])
    assert Decimal(str(latest['ELECTRICITY_COST']))==Decimal(latest_bill['final_amount'])
    answer=Agent(build_context(auth,repo),service).chat('Tiền điện kỳ '+latest['period']+' của tôi là bao nhiêu? Nêu rõ tiền này đã có thuế phí hay chưa.')
    assert answer['metadata']['provider']=='gemini' and answer['status']=='ANSWERED',answer['status']
    assert any(s.get('ref')=='bill:'+latest_bill['id'] for s in answer['sources']),answer['sources']
    print(json.dumps({'bill_count':len(bills),'latest_period':latest['period'],'latest_cost_before_tax':latest_bill['final_amount'],
        'gemini_status':answer['status'],'message':answer['message']},ensure_ascii=True))
    db.rollback()
