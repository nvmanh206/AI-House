"""Run inside backend container: import reviewed EVN catalog and backfill one requested household."""
import json,os
import hashlib
from pathlib import Path
from datetime import date
from types import SimpleNamespace
from app.db import SessionLocal
from app.repository import Repository
from app.models import Household,User,UtilityAccount,Tariff,TariffTier,AuditLog
from app.schemas import TariffInput
from app.services import HouseholdService
from app.tariff_import import residential_tiers
catalog=json.loads(Path('/data/knowledge/evn-billing-verified.json').read_text())
source=catalog['source']
original=Path('/data/knowledge/evn-billing-original.html').read_bytes()
assert hashlib.sha256(original).hexdigest()==source['sha256'],'Source archive changed'
assert residential_tiers(original)[0]==catalog['tiers'],'Catalog differs from source table'
with SessionLocal.begin() as db:
    repo=Repository(db);house=repo.get(Household,os.environ['BILLING_HOUSEHOLD_ID'])
    assert house,'Unknown household'
    actor=repo.get(User,house.owner_user_id)
    assert actor.role=='ADMIN','Reviewed catalog import requires the existing admin owner'
    accounts=repo.all(UtilityAccount,household_id=house.id,utility_type='ELECTRICITY',provider_name='EVN',is_active=True)
    assert accounts and all(a.tariff_category=='RESIDENTIAL_1PHASE' for a in accounts),'Account category requires review'
    data=TariffInput(utility_type='ELECTRICITY',provider_name='EVN',name='EVN sinh hoạt - '+source['decision'],version='1279-2025-verified',
        tariff_category='RESIDENTIAL_1PHASE',province=None,effective_from=date.fromisoformat(source['effective_from']),tiers=catalog['tiers'])
    tariff=repo.one(Tariff,provider_name='EVN',utility_type='ELECTRICITY',tariff_category=data.tariff_category,version=data.version)
    if not tariff:
        tariff=repo.add(Tariff,**data.model_dump(exclude={'tiers'}))
        for i,tier in enumerate(data.tiers):repo.add(TariffTier,tariff_id=tariff.id,order_index=i,**tier.model_dump())
        repo.add(AuditLog,user_id=actor.id,household_id=None,action='VERIFY_TARIFF_SOURCE',entity_type='tariffs',entity_id=tariff.id,details=source)
    result=HouseholdService(repo,(actor,SimpleNamespace(household_id=house.id))).generate_bills()
    print(json.dumps({'created':[{'period_id':b['billing_period_id'],'consumption':b['consumption'],'amount_before_tax':b['final_amount'],'source':b['source']} for b in result['created']], 'skipped':result['skipped']},ensure_ascii=True))
