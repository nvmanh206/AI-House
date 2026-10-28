from decimal import Decimal

from app.models import Bill, UtilityAccount, Meter
from conftest import reading


def test_statistics_reports_zero_electricity_and_missing_water_separately(client, ready):
    headers, _, meter = ready
    assert reading(client, headers, meter, current=100).status_code == 201
    response = client.get('/api/statistics?start=2026-01-01&end=2026-01-31', headers=headers)
    assert response.status_code == 200
    row = response.json()['series'][0]
    assert row['ELECTRICITY'] == 0
    assert row['ELECTRICITY_COST'] == 0
    assert row['WATER'] is None
    assert row['WATER_COST'] is None
    assert row['cost'] == 0


def test_cancelled_bill_is_excluded_from_utility_and_total_cost(client, ready, db):
    headers, _, meter = ready
    assert reading(client, headers, meter).status_code == 201
    bill = db.query(Bill).one()
    bill.status = 'CANCELLED'
    db.commit()
    response = client.get('/api/statistics?start=2026-01-01&end=2026-01-31', headers=headers)
    assert response.status_code == 200
    row = response.json()['series'][0]
    assert row['ELECTRICITY'] == 80
    assert row['ELECTRICITY_COST'] is None
    assert row['WATER_COST'] is None
    assert row['cost'] is None


def test_cost_aggregates_multiple_accounts_without_binary_roundoff(client, ready, db):
    headers, house, meter = ready
    assert reading(client, headers, meter).status_code == 201
    first_bill = db.query(Bill).one()
    first_bill.final_amount = Decimal('0.10')
    account = UtilityAccount(household_id=house['id'], utility_type='ELECTRICITY', provider_name='Demo')
    db.add(account); db.flush()
    other = Meter(household_id=house['id'], utility_account_id=account.id,
                  name='Second meter', utility_type='ELECTRICITY', unit='kWh', initial_reading=0)
    db.add(other); db.commit()
    second = reading(client, headers, {'id': other.id}, current=10)
    assert second.status_code == 201, second.text
    db.get(Bill, second.json()['bill']['id']).final_amount = Decimal('0.20')
    db.commit()
    response = client.get('/api/statistics?start=2026-01-01&end=2026-01-31', headers=headers)
    assert response.status_code == 200
    row = response.json()['series'][0]
    assert row['ELECTRICITY'] == 90
    assert row['ELECTRICITY_COST'] == 0.3
    assert row['cost'] == 0.3
    assert row['WATER_COST'] is None
    assert db.query(Bill).count() == 2
