import pytest

from conftest import reading


@pytest.mark.parametrize('message', [
    'Tháng này dùng bao nhiêu nước?',
    'Thang nay dung bao nhieu nuoc?',
])
def test_water_query_does_not_answer_with_electricity_data(client, ready, message):
    headers, _, meter = ready
    assert reading(client, headers, meter).status_code == 201
    response = client.post('/api/ai/chat', headers=headers, json={'message': message})
    assert response.status_code == 200, response.text
    answer = response.json()
    assert answer['intent'] == 'CONSUMPTION_ANALYSIS'
    assert 'Chưa đủ dữ liệu' in answer['message']
    assert 'kWh' not in answer['message']
    assert answer['sources'] == []


@pytest.mark.parametrize('message', [
    'So sánh tiền điện các tháng',
    'So sanh tien dien cac thang',
])
def test_money_comparison_uses_bill_amount_with_or_without_accents(client, ready, message):
    headers, _, meter = ready
    assert reading(client, headers, meter).status_code == 201
    assert reading(client, headers, meter, month=2, current=280).status_code == 201
    response = client.post('/api/ai/chat', headers=headers, json={'message': message})
    assert response.status_code == 200, response.text
    answer = response.json()
    assert answer['intent'] == 'CONSUMPTION_COMPARISON'
    assert 'VND' in answer['message']
    assert '110,000' in answer['message']
    assert 'kWh' not in answer['message']
    assert {source['type'] for source in answer['sources']} == {'bill'}


@pytest.mark.parametrize('message', [
    'So sánh hóa đơn nước 3 tháng gần nhất.',
    'So sanh hoa don nuoc 3 thang gan nhat.',
])
def test_water_bill_comparison_does_not_trigger_ocr_intent(client, ready, message):
    headers, _, meter = ready
    response = client.post('/api/ai/chat', headers=headers, json={'message': message})
    assert response.status_code == 200, response.text
    answer = response.json()
    assert answer['intent'] == 'CONSUMPTION_COMPARISON'
    assert 'Chưa có hóa đơn để so sánh' in answer['message']
    assert 'Chưa đủ dữ liệu để đối chiếu' not in answer['message']
    assert 'meter_verification' not in answer.get('metadata', {}).get('result', {})

