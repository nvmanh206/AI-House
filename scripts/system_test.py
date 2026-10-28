"""Isolated real-HTTP/browser test stack. Never writes to the app database.

Modes: prepare, serve, exercise, zero, values. Test credentials are disposable.
The configured tariff is copied from PostgreSQL, not invented by the frontend.
"""
import argparse
import json
import os
import secrets
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url

root = Path(__file__).resolve().parents[1]
backend = root / 'backend'
state_path = root / '.local' / 'system-test-state.json'
mode = argparse.ArgumentParser()
mode.add_argument('action', choices=['prepare', 'serve', 'exercise', 'zero', 'values'])
action = mode.parse_args().action
app_config = dotenv_values(backend / '.env')
app_url = make_url(app_config['DATABASE_URL'])
if app_url.get_backend_name() != 'postgresql':
    raise SystemExit('PostgreSQL application configuration required.')
if action == 'prepare':
    test_url = app_url.set(database='utility_system_' + uuid4().hex[:12] + '_test')
    admin = create_engine(app_url.set(database='postgres'), isolation_level='AUTOCOMMIT')
    with admin.connect() as connection:
        identifier = connection.dialect.identifier_preparer.quote(test_url.database)
        connection.execute(text('CREATE DATABASE ' + identifier))
    admin.dispose()
    state = {'database_url': test_url.render_as_string(hide_password=False),
             'jwt_secret': secrets.token_urlsafe(48), 'email': 'system-' + uuid4().hex[:12] + '@example.com',
             'password': 'SystemTestOnly2026!', 'api': 'http://127.0.0.1:8108/api',
             'frontend': 'http://127.0.0.1:3108', 'database': test_url.database}
else:
    state = json.loads(state_path.read_text(encoding='utf-8'))
test_database = make_url(state['database_url']).database or ''
if (test_database == app_url.database or not test_database.startswith('utility_system_')
        or not test_database.endswith('_test')):
    raise SystemExit('Refusing to use application database for system tests.')
test_llm_provider = app_config.get('LLM_PROVIDER', 'gemini') if (action == 'serve' and app_config.get('GEMINI_API_KEY')) else 'deterministic'
test_gemini_key = app_config.get('GEMINI_API_KEY', '') if action == 'serve' else ''
os.environ.update(DATABASE_URL=state['database_url'], JWT_SECRET=state['jwt_secret'],
                  FRONTEND_URL=state['frontend'], APP_ENV='test', LLM_PROVIDER=test_llm_provider,
                  REFRESH_COOKIE_NAME='utility_system_refresh',
                  GEMINI_API_KEY=test_gemini_key, LLM_API_KEY='', RATE_LIMIT_ENABLED='false',
                  KNOWLEDGE_DATABASE_URL=app_config.get('KNOWLEDGE_DATABASE_URL', ''),
                  KNOWLEDGE_ARCHIVE_PATH=app_config.get('KNOWLEDGE_ARCHIVE_PATH', ''),
                  KNOWLEDGE_EMBEDDING_MODEL=app_config.get('KNOWLEDGE_EMBEDDING_MODEL', 'gemini-embedding-2'),
                  KNOWLEDGE_RAG_ENABLED=app_config.get('KNOWLEDGE_RAG_ENABLED', 'true'))
if action == 'serve' and app_config.get('GEMINI_MODEL'):
    os.environ['GEMINI_MODEL'] = app_config['GEMINI_MODEL']
sys.path.insert(0, str(backend))
os.chdir(backend)
from app.models import Tariff, TariffTier, Bill

if action == 'prepare':
    from alembic import command
    from alembic.config import Config
    config = Config(str(backend / 'alembic.ini'))
    config.set_main_option('script_location', str(backend / 'alembic'))
    command.upgrade(config, 'head')
    source, target = create_engine(app_url), create_engine(state['database_url'])
    with source.connect() as connection, target.begin() as destination:
        tariffs = connection.execute(select(Tariff).where(Tariff.utility_type == 'ELECTRICITY', Tariff.is_active == True)).mappings().all()
        candidates = [t for t in tariffs if t['effective_from'] <= date.today() and (t['effective_to'] is None or t['effective_to'] >= date.today())]
        if not candidates:
            raise SystemExit('No configured active electricity tariff available for system test.')
        tariff = dict(candidates[0])
        tiers = connection.execute(select(TariffTier).where(TariffTier.tariff_id == tariff['id'])).mappings().all()
        if not tiers:
            raise SystemExit('Configured tariff has no tiers.')
        destination.execute(Tariff.__table__.insert(), tariff)
        destination.execute(TariffTier.__table__.insert(), [dict(t) for t in tiers])
        state['account'] = {'utility_type': 'ELECTRICITY', 'provider_name': tariff['provider_name'],
                            'tariff_category': tariff['tariff_category'], 'province': tariff['province'] or ''}
    state_path.write_text(json.dumps(state), encoding='utf-8')
    print('Prepared isolated PostgreSQL database:', state['database'])
    print('Disposable browser login:', state['email'], '(password is the test-only fixture in this script)')
elif action == 'serve':
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=8108)
else:
    import httpx
    with httpx.Client(base_url=state['api'], timeout=20) as client:
        def call(method, path, payload=None, status=200):
            response = client.request(method, path, json=payload)
            assert response.status_code == status, f'{method} {path}: {response.status_code} {response.text}'
            return response.json()
        if action == 'exercise':
            assert call('GET', '/health')['status'] == 'ok'
            assert client.get('/statistics').status_code == 401
            call('POST', '/auth/register', {'email': state['email'], 'password': state['password'], 'full_name': 'System Test'}, 201)
        auth = call('POST', '/auth/login', {'email': state['email'], 'password': state['password']})
        client.headers['Authorization'] = 'Bearer ' + auth['access_token']
        if action == 'exercise':
            house = call('POST', '/households', {'name': 'System verification', 'province': state['account']['province'], 'accounts': [{**state['account'], 'initial_reading': '0'}]}, 201)
            account = call('POST', '/utility-accounts', state['account'], 201)
            call('POST', '/meters', {'utility_account_id': account['id'], 'name': 'Second system meter', 'initial_reading': '0'}, 201)
            state['household_id'] = house['id']
            assert call('GET', '/statistics')['series'] == []
            state_path.write_text(json.dumps(state), encoding='utf-8')
            print('HTTP health/auth/isolation/onboarding/two accounts/empty statistics: PASS')
        else:
            now = date.today()
            previous = date(now.year - (now.month == 1), 12 if now.month == 1 else now.month - 1, 1)
            day = previous if action == 'zero' else now
            meters = call('GET', '/meters')
            assert len(meters) == 2
            created = []
            for index, meter in enumerate(meters):
                payload = {'meter_id': meter['id'], 'year': day.year, 'month': day.month,
                           'reading_date': str(day), 'current_reading': str(0 if action == 'zero' else (index+1)*10)}
                response = client.post('/readings', json=payload)
                if response.status_code == 201:
                    created.append(response.json()['bill'])
                else:
                    # A browser may already have entered this meter for this phase.
                    assert response.status_code == 409, response.text
                    matches = [b for b in call('GET', '/bills')
                               if b['utility_account_id'] == meter['utility_account_id']
                               and b['period'] == day.strftime('%Y-%m')]
                    assert len(matches) == 1
                    assert Decimal(matches[0]['consumption']) == Decimal(payload['current_reading'])
                    created.append(matches[0])
                assert client.post('/readings', json=payload).status_code == 409
            period = day.strftime('%Y-%m')
            row = next(r for r in call('GET', '/statistics')['series'] if r['period'] == period)
            expected = sum((Decimal(b['final_amount']) for b in created), Decimal(0))
            assert Decimal(str(row['ELECTRICITY_COST'])) == expected
            assert Decimal(str(row['cost'])) == expected and row['WATER_COST'] is None
            assert row['ELECTRICITY'] == (0 if action == 'zero' else 30)
            engine = create_engine(state['database_url'])
            with engine.connect() as connection:
                persisted = connection.execute(select(Bill.final_amount).where(Bill.id.in_([b['id'] for b in created]))).scalars().all()
                assert sum(persisted, Decimal(0)) == expected
            if action == 'values':
                payment = call('POST', '/payments', {'bill_id': created[0]['id']})
                assert call('POST', '/payments', {'bill_id': created[0]['id']})['id'] == payment['id']
                assert call('GET', '/bills/' + created[0]['id'])['status'] == 'PAID'
            print(f'HTTP readings/duplicate rollback/statistics/PostgreSQL comparison ({action}): PASS; period={period}; expected total={expected}')
