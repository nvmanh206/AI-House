from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import select, func

from app.billing_service import BillingService
from app.models import Bill, MeterReading, Tariff
from app.repository import Repository
from app.security import DomainError
from conftest import reading


DAY = date(2026, 1, 25)


def add_tariff(db, **overrides):
    values = dict(utility_type='ELECTRICITY', provider_name='Demo',
                  tariff_category='RESIDENTIAL_1PHASE', name='Test tariff',
                  version='v1', effective_from=date(2020, 1, 1), is_active=True)
    values.update(overrides)
    tariff = Tariff(**values)
    db.add(tariff)
    db.flush()
    return tariff


def account(**overrides):
    values = dict(utility_type='ELECTRICITY', provider_name='Demo',
                  tariff_category='RESIDENTIAL_1PHASE', province='Hà Nội', household_id=None)
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize('overrides', [
    {'provider_name': 'Other provider'},
    {'tariff_category': 'BUSINESS'},
    {'province': 'Đà Nẵng'},
    {'utility_type': 'WATER'},
    {'is_active': False},
    {'effective_from': date(2026, 2, 1)},
    {'effective_to': date(2026, 1, 24)},
])
def test_incompatible_tariff_is_not_a_fallback(db, overrides):
    add_tariff(db, **overrides)
    with pytest.raises(DomainError) as exc:
        BillingService(Repository(db)).tariff(account(), DAY)
    assert (exc.value.code, exc.value.status) == ('TARIFF_NOT_FOUND', 409)


def test_unknown_location_cannot_use_regional_tariff(db):
    add_tariff(db, province='Hà Nội')
    with pytest.raises(DomainError) as exc:
        BillingService(Repository(db)).tariff(account(province=None), DAY)
    assert exc.value.code == 'TARIFF_NOT_FOUND'


def test_local_tariff_takes_priority_over_nationwide(db):
    add_tariff(db)
    local = add_tariff(db, province='Hà Nội', version='local')
    selected, _ = BillingService(Repository(db)).tariff(account(province=' hà nội '), DAY)
    assert selected.id == local.id


def test_nationwide_tariff_is_allowed_when_no_local_match(db):
    nationwide = add_tariff(db)
    add_tariff(db, province='Đà Nẵng', version='regional')
    selected, _ = BillingService(Repository(db)).tariff(account(), DAY)
    assert selected.id == nationwide.id


@pytest.mark.parametrize('province', [None, 'Hà Nội'])
def test_overlapping_tariffs_at_same_priority_are_ambiguous(db, province):
    add_tariff(db, province=province)
    add_tariff(db, province=province, version='v2', effective_from=date(2026, 1, 1))
    with pytest.raises(DomainError) as exc:
        BillingService(Repository(db)).tariff(account(), DAY)
    assert (exc.value.code, exc.value.status) == ('TARIFF_AMBIGUOUS', 409)


@pytest.mark.parametrize('ambiguous', [False, True])
def test_missing_tariff_saves_reading_but_ambiguous_tariff_still_rolls_back(client, db, ready, ambiguous):
    headers, _, meter = ready
    if ambiguous:
        add_tariff(db, version='v2')
    else:
        tariff = db.scalar(select(Tariff))
        tariff.provider_name = 'Other provider'
    db.commit()
    response = reading(client, headers, meter)
    assert response.status_code == (409 if ambiguous else 201), response.text
    assert db.scalar(select(func.count()).select_from(MeterReading)) == (0 if ambiguous else 1)
    assert db.scalar(select(func.count()).select_from(Bill)) == 0
