"""Real HTTP OCR regression on the existing isolated System PostgreSQL stack.

Run system_test.py prepare/serve first. Never connects writes to the app DB.
Creates a disposable user/household; retains fixture state for browser verification.
"""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

root = Path(__file__).resolve().parents[1]
state = json.loads((root / '.local/system-test-state.json').read_text())
database = make_url(state['database_url']).database or ''
assert database.startswith('utility_system_') and database.endswith('_test')
day = date.today()
previous = date(day.year - (day.month == 1), 12 if day.month == 1 else day.month - 1, 1)
fixture = {'email': 'ocr-' + uuid4().hex[:12] + '@example.com', 'password': 'SystemTestOnly2026!'}
with httpx.Client(base_url=state['api'], timeout=30) as client:
    def call(method, path, payload=None, expected=200):
        response = client.request(method, path, json=payload)
        assert response.status_code == expected, f'{method} {path}: HTTP {response.status_code}'
        return response.json()

    call('POST', '/auth/register', {**fixture, 'full_name': 'OCR System Test'}, 201)
    auth = call('POST', '/auth/login', fixture)
    client.headers['Authorization'] = 'Bearer ' + auth['access_token']
    house = call('POST', '/households', {'name': 'OCR verification', 'province': state['account']['province'],
        'accounts': [{**state['account'], 'customer_code': 'PD12345', 'initial_reading': '100'}]}, 201)
    meter = call('GET', '/meters')[0]
    for period, reading in [(previous, 150), (day, 180)]:
        recorded = call('POST', '/readings', {'meter_id': meter['id'], 'year': period.year, 'month': period.month,
            'reading_date': str(period), 'current_reading': reading}, 201)
    account = call('POST', '/utility-accounts', {**state['account'], 'customer_code': 'PD99999'}, 201)
    other = call('POST', '/meters', {'utility_account_id': account['id'], 'name': 'Other account meter', 'initial_reading': 0}, 201)
    call('POST', '/readings', {'meter_id': other['id'], 'year': previous.year, 'month': previous.month,
         'reading_date': str(previous), 'current_reading': 900}, 201)

    def analyze(code, reading, period=True):
        content = f'Phân tích hóa đơn điện\nMã KH: {code}\n'
        if period:
            content += f'Kỳ: {day.month:02}/{day.year}\n'
        content += f'Chỉ số cũ: 150\nChỉ số mới: {reading}\nTổng tiền: 123000 VNĐ'
        return call('POST', '/ai/chat', {'message': content})

    matched = analyze('PD12345', 180)
    result = matched['metadata']['result']
    assert result['meter_verification']['status'] == 'MATCH'
    assert result['comparison']['previous_3_period_average'] == 50
    assert result['bill']['consumption'] == 30
    assert Decimal(str(result['amount_analysis']['expected_amount'])) == Decimal(recorded['bill']['final_amount'])
    assert result['amount_analysis']['source'] == recorded['bill']['source']
    assert analyze('PD12345', 181)['metadata']['result']['meter_verification']['status'] == 'MISMATCH'
    for response in [analyze('PD00000', 180), analyze('PD12345', 180, period=False)]:
        unknown = response['metadata']['result']
        assert unknown['meter_verification']['status'] == 'UNKNOWN'
        assert unknown['comparison']['previous_3_period_average'] is None
        assert unknown['forecast']['next_period_consumption'] is None
        assert 'tài khoản' in response['message']
    engine = create_engine(state['database_url'])
    with engine.connect() as connection:
        persisted = connection.execute(text('SELECT final_amount FROM bills WHERE id=:id'), {'id': recorded['bill']['id']}).scalar_one()
        assert persisted == Decimal(str(result['amount_analysis']['expected_amount']))
        assert connection.execute(text('SELECT count(*) FROM meter_readings WHERE meter_id=:id'), {'id': meter['id']}).scalar_one() == 2
    engine.dispose()
    fixture.update(household_id=house['id'], database=database, period=day.strftime('%m/%Y'))
    (root / '.local/ocr-browser-state.json').write_text(json.dumps(fixture), encoding='utf-8')
    (root / '.local/ocr-system-result.json').write_text(json.dumps(matched, ensure_ascii=False), encoding='utf-8')
    print('PASS: HTTP auth -> two accounts -> PostgreSQL readings -> inline OCR MATCH/MISMATCH/UNKNOWN; scoped history and SQL amount agree; no OCR reading writes.')
    print('Disposable browser email:', fixture['email'])
