from conftest import reading,register,setup_house
from app.models import Tariff,MeterReading,Bill

def test_private_bill_tax_note_does_not_require_public_search():
    from app.knowledge.service import public_query
    assert not public_query('Tiền điện kỳ 2026-10 của tôi là bao nhiêu? Tiền này đã có thuế phí chưa?',[]).needs_public_knowledge
    assert public_query('Thuế suất VAT tiền điện hiện hành là bao nhiêu?',[]).needs_public_knowledge

def test_generate_after_tariff_configured_is_scoped_and_idempotent(client,ready,db):
    headers,_,meter=ready
    tariff=db.query(Tariff).one();tariff.is_active=False;db.commit()
    assert reading(client,headers,meter,month=9,current=1500).status_code==201
    assert reading(client,headers,meter,month=10,current=2222).status_code==201
    missing=client.post('/api/bills/generate',headers=headers)
    assert missing.status_code==200 and len(missing.json()['skipped'])==2
    tariff.is_active=True;db.commit()
    result=client.post('/api/bills/generate',headers=headers)
    assert result.status_code==200 and len(result.json()['created'])==2
    assert all(b['source']=='SYSTEM_ESTIMATE' for b in result.json()['created'])
    assert db.query(MeterReading).count()==2
    assert len(client.post('/api/bills/generate',headers=headers).json()['created'])==0
    other=register(client,'foreign-bills@example.com');setup_house(client,other)
    assert client.post('/api/bills/generate',headers=other).json()['created']==[]
    assert db.query(Bill).count()==2
    bill=db.query(Bill).first();original=bill.final_amount;bill.status='PAID';db.commit()
    assert client.post('/api/bills/generate',headers=headers).json()['created']==[]
    assert db.query(Bill).filter_by(id=bill.id).one().final_amount==original
