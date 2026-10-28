from conftest import register,setup_house

def test_reading_without_tariff_is_saved_without_inventing_a_bill(client):
    headers=register(client);setup_house(client,headers)
    meter=client.get('/api/meters',headers=headers).json()[0]
    response=client.post('/api/readings',headers=headers,json={'meter_id':meter['id'],'year':2026,'month':1,'current_reading':'125.5','reading_date':'2026-01-25'})
    assert response.status_code==201,response.text
    body=response.json()
    assert body['bill'] is None and body['billing_status']=='TARIFF_NOT_FOUND'
    assert float(body['reading']['consumption'])==25.5
    assert len(client.get('/api/readings',headers=headers).json())==1
    assert client.get('/api/bills',headers=headers).json()==[]
    duplicate=client.post('/api/readings',headers=headers,json={'meter_id':meter['id'],'year':2026,'month':1,'current_reading':'126','reading_date':'2026-01-25'})
    assert duplicate.status_code==409

def test_dashboard_statistics_keep_usage_when_no_bill_exists(client):
    headers=register(client);setup_house(client,headers)
    meter=client.get('/api/meters',headers=headers).json()[0]
    for month,current in ((9,'1500'),(10,'2222')):
        response=client.post('/api/readings',headers=headers,json={'meter_id':meter['id'],'year':2026,'month':month,'current_reading':current,'reading_date':f'2026-{month:02}-25'})
        assert response.status_code==201,response.text
    stats=client.get('/api/statistics?start=2026-09-01&end=2026-10-31',headers=headers)
    assert stats.status_code==200
    latest=stats.json()['series'][-1]
    assert latest['period']=='2026-10' and latest['ELECTRICITY']==722
    assert latest['cost'] is None and latest['ELECTRICITY_COST'] is None and latest['WATER'] is None
