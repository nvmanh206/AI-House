from types import SimpleNamespace

import pytest

from app.ai.tools.ocr_analysis import analyze_bill_ocr


@pytest.fixture
def scoped_service(monkeypatch):
    monkeypatch.setattr('app.ai.tools.ocr_analysis.GeminiProvider.analyze_ocr_with_gemini', lambda *a, **kw: None)
    return SimpleNamespace(
        member=lambda: SimpleNamespace(household_id='own-house'),
        accounts=lambda: [{'id': 'account', 'utility_type': 'ELECTRICITY', 'customer_code': 'PD12345'}],
        meters=lambda: [{'id': 'meter', 'utility_account_id': 'account', 'utility_type': 'ELECTRICITY', 'initial_reading': 150}],
        history=lambda: [
            {'meter_id': 'meter', 'period': '2026-08', 'utility_type': 'ELECTRICITY', 'current_reading': 150, 'consumption': 50},
            {'meter_id': 'meter', 'period': '2026-09', 'utility_type': 'ELECTRICITY', 'current_reading': 200, 'consumption': 50},
        ],
        bills=lambda: [], forecast=lambda _: {'available': False},
    )


@pytest.mark.parametrize('code,period,expected,reading', [
    ('PD12345', '08/2026', 'MATCH', 150),
    ('PD12345', '07/2026', 'UNKNOWN', None),
    ('PD99999', '08/2026', 'UNKNOWN', None),
    ('PD12345', '', 'UNKNOWN', None),
])
def test_ocr_requires_correct_account_and_period(scoped_service, code, period, expected, reading):
    result = analyze_bill_ocr(scoped_service, raw_ocr_text=f'HÓA ĐƠN ĐIỆN\nMã KH: {code}\nKỳ: {period}\nChỉ số mới: 150')
    assert result['meter_verification']['status'] == expected
    assert result['meter_verification']['database_reading'] == reading


def test_ocr_does_not_choose_first_of_multiple_accounts(scoped_service):
    scoped_service.accounts = lambda: [
        {'id': 'account', 'utility_type': 'ELECTRICITY'},
        {'id': 'other', 'utility_type': 'ELECTRICITY'},
    ]
    result = analyze_bill_ocr(scoped_service, raw_ocr_text='HÓA ĐƠN ĐIỆN\nKỳ: 09/2026\nChỉ số mới: 200')
    assert result['meter_verification']['status'] == 'UNKNOWN'
    assert result['meter_verification']['database_reading'] is None


def test_comparison_excludes_other_meters_current_and_future_periods(scoped_service):
    scoped_service.history = lambda: [
        {'meter_id': 'meter', 'period': '2026-06', 'utility_type': 'ELECTRICITY', 'current_reading': 100, 'consumption': 10},
        {'meter_id': 'meter', 'period': '2026-07', 'utility_type': 'ELECTRICITY', 'current_reading': 120, 'consumption': 20},
        {'meter_id': 'meter', 'period': '2026-08', 'utility_type': 'ELECTRICITY', 'current_reading': 150, 'consumption': 30},
        {'meter_id': 'other', 'period': '2026-07', 'utility_type': 'ELECTRICITY', 'current_reading': 999, 'consumption': 999},
        {'meter_id': 'meter', 'period': '2026-09', 'utility_type': 'ELECTRICITY', 'current_reading': 500, 'consumption': 350},
    ]
    result = analyze_bill_ocr(scoped_service, raw_ocr_text='HÓA ĐƠN ĐIỆN\nMã KH: PD12345\nKỳ: 08/2026\nChỉ số cũ: 120\nChỉ số mới: 150')
    assert result['comparison']['previous_3_period_average'] == 15
    assert result['comparison']['difference_percent'] == 100
    assert result['bill']['consumption'] == 30


def test_unknown_account_has_no_comparison_or_forecast(scoped_service):
    scoped_service.forecast = lambda _: {'available': True, 'predicted_consumption': 999, 'predicted_amount': 999}
    result = analyze_bill_ocr(scoped_service, raw_ocr_text='HÓA ĐƠN ĐIỆN\nMã KH: PD99999\nKỳ: 08/2026\nSản lượng: 10 kWh')
    assert result['comparison']['previous_3_period_average'] is None
    assert result['comparison']['trend'] == 'unknown'
    assert result['forecast']['next_period_consumption'] is None


def test_amount_uses_exact_recorded_bill_including_zero(scoped_service):
    scoped_service.bills = lambda: [
        {'id': 'wrong', 'utility_account_id': 'other', 'utility_type': 'ELECTRICITY', 'period': '2026-09', 'final_amount': 999,
         'tariff_version_snapshot': {'tiers': [{'unit_price': 999}]}},
        {'id': 'own', 'utility_account_id': 'account', 'utility_type': 'ELECTRICITY', 'period': '2026-08', 'final_amount': 0, 'source': 'SYSTEM_ESTIMATE', 'status': 'UNPAID'},
    ]
    result = analyze_bill_ocr(scoped_service, raw_ocr_text='HÓA ĐƠN ĐIỆN\nMã KH: PD12345\nKỳ: 08/2026\nSản lượng: 10 kWh\nTổng tiền: 100 VNĐ')
    assert result['amount_analysis']['expected_amount'] == 0
    assert result['amount_analysis']['difference'] == 100
    assert result['amount_analysis']['source'] == 'SYSTEM_ESTIMATE'


def test_duplicate_meter_observations_are_unknown(scoped_service):
    original = scoped_service.history()
    scoped_service.history = lambda: [*original, original[0]]
    result = analyze_bill_ocr(scoped_service, raw_ocr_text='HÓA ĐƠN ĐIỆN\nMã KH: PD12345\nKỳ: 08/2026\nChỉ số mới: 150')
    assert result['meter_verification']['status'] == 'UNKNOWN'
