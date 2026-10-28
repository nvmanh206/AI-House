from conftest import reading

def test_past_period_explains_next_period_limit_and_accepts_valid_backfill(client,ready):
    headers,_,meter=ready
    assert reading(client,headers,meter,month=10,current=2222).status_code==201
    rejected=reading(client,headers,meter,month=9,current=2334)
    assert rejected.status_code==400
    message=rejected.json()['error']['message']
    assert all(value in message for value in ('09/2026','10/2026','2334','2222'))
    assert len(client.get('/api/readings',headers=headers).json())==1
    accepted=reading(client,headers,meter,month=9,current=2000)
    assert accepted.status_code==201,accepted.text
    rows=client.get('/api/readings',headers=headers).json()
    october=next(r for r in rows if r['period']=='2026-10')
    assert float(october['previous_reading'])==2000
    assert float(october['consumption'])==222
