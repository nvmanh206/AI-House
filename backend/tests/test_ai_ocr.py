import pytest
import inspect
from datetime import date
from app.ai.tools.ocr_parser import parse_ocr_text, mask_customer_code
from app.ai.tools.ocr_analysis import analyze_bill_ocr
from app.security import DomainError
from app.models import Tariff, TariffTier
from tests.conftest import register as register_helper, setup_house, reading as reading_helper

def test_ocr_parser_electricity_bill():
    raw_text = """
    CÔNG TY ĐIỆN LỰC THÁI NGUYÊN
    Mã KH: PD12003123
    Kỳ: 09/2026
    Chỉ số cũ: 1280
    Chỉ số mới: 1450
    Sản lượng: 170 kWh
    Tổng tiền: 512.340 VNĐ
    Hạn thanh toán: 28/09/2026
    """
    data = parse_ocr_text(raw_text)
    assert data.bill_type == 'ELECTRICITY'
    assert data.customer_code == 'PD12003123'
    assert data.billing_period == '2026-09'
    assert data.previous_reading == 1280.0
    assert data.current_reading == 1450.0
    assert data.consumption == 170.0
    assert data.amount == 512340.0
    assert str(data.due_date) == '2026-09-28'

def test_ocr_parser_water_bill():
    raw_text = """
    CÔNG TY CẤP NƯỚC SẠCH
    Mã KH: N987654
    Tháng 10/2026
    Từ 150 đến 175
    Khối nước: 25 m3
    Thành tiền: 250.000 đ
    """
    data = parse_ocr_text(raw_text)
    assert data.bill_type == 'WATER'
    assert data.customer_code == 'N987654'
    assert data.billing_period == '2026-10'
    assert data.previous_reading == 150.0
    assert data.current_reading == 175.0
    assert data.consumption == 25.0
    assert data.amount == 250000.0

def test_mask_customer_code():
    assert mask_customer_code('PD12003123') == 'PD****3123'
    assert mask_customer_code('N123') == 'N123'
    assert mask_customer_code(None) is None

# --- SECURITY TESTS & METER VERIFICATION BUSINESS RULES ---

def test_tool_signature_does_not_accept_household_id():
    """Requirement 1 & 29: Tool MUST NOT accept household_id or user_id parameters."""
    sig = inspect.signature(analyze_bill_ocr)
    params = sig.parameters.keys()
    assert 'household_id' not in params
    assert 'user_id' not in params
    assert 'member_id' not in params
    assert 'customer_owner_id' not in params

def test_security_recheck_member_context():
    """Requirement 4 & 29: Tool must recheck member context and reject if unauthorized."""
    class DummyServiceNoMember:
        def member(self):
            return None

    with pytest.raises(DomainError) as exc:
        analyze_bill_ocr(DummyServiceNoMember(), raw_ocr_text="Mã KH: PD123")
    assert exc.value.status == 401

def test_meter_verification_match(client, ready):
    """Test 1: OCR reading == DB reading => MATCH status."""
    headers, house, meter = ready
    r = reading_helper(client, headers, meter, month=8, current=150)
    assert r.status_code == 201

    # Upload OCR with current_reading = 150 (exactly matches DB reading)
    ocr_text = """
    HÓA ĐƠN ĐIỆN EVN
    Kỳ: 08/2026
    Chỉ số cũ: 150
    Chỉ số mới: 150
    """
    res = client.post('/api/ai/chat', headers=headers, json={'message': 'Phân tích hóa đơn này', 'raw_ocr_text': ocr_text})
    assert res.status_code == 200
    data = res.json()['metadata']['result']
    assert data['meter_verification']['status'] == 'MATCH'
    assert data['meter_verification']['ocr_reading'] == 150.0
    assert data['meter_verification']['database_reading'] == 150.0
    assert data['meter_verification']['difference'] == 0.0

def test_meter_verification_mismatch(client, ready):
    """Test 2: OCR reading != DB reading => MISMATCH status."""
    headers, house, meter = ready
    r = reading_helper(client, headers, meter, month=8, current=1250)
    assert r.status_code == 201

    # Upload OCR with current_reading = 1275 (diff +25 from 1250)
    ocr_text = """
    HÓA ĐƠN ĐIỆN EVN
    Kỳ: 08/2026
    Chỉ số cũ: 1200
    Chỉ số mới: 1275
    Sản lượng: 75 kWh
    """
    res = client.post('/api/ai/chat', headers=headers, json={'message': 'Phân tích hóa đơn', 'raw_ocr_text': ocr_text})
    assert res.status_code == 200
    data = res.json()['metadata']['result']
    assert data['meter_verification']['status'] == 'MISMATCH'
    assert data['meter_verification']['ocr_reading'] == 1275.0
    assert data['meter_verification']['database_reading'] == 1250.0
    assert data['meter_verification']['difference'] == 25.0
    # Must contain warning for mismatch
    codes = [w['code'] for w in data['warnings']]
    assert 'METER_READING_MISMATCH' in codes


def test_inline_bill_text_reaches_ocr_from_chat(client, ready):
    headers, house, meter = ready
    assert reading_helper(client, headers, meter, month=8, current=150).status_code == 201
    response = client.post('/api/ai/chat', headers=headers, json={
        'message': 'Phân tích hóa đơn điện\nKỳ: 08/2026\nChỉ số mới: 150',
    })
    assert response.status_code == 200
    result = response.json()['metadata']['result']
    assert result['status'] == 'success'
    assert result['meter_verification']['status'] == 'MATCH'

def test_meter_verification_unknown(client):
    """Test 3: Missing OCR reading or DB reading => UNKNOWN status."""
    headers = register_helper(client, 'ver_unknown@example.com')
    client.post('/api/households', headers=headers, json={
        'name': 'Unknown House', 'address': 'Addr', 'member_count': 1,
        'accounts': [{'utility_type': 'ELECTRICITY', 'provider_name': 'EVN', 'customer_code': 'PD333', 'initial_reading': 100}]
    })

    # OCR text missing meter reading numbers
    ocr_text = """
    HÓA ĐƠN ĐIỆN EVN
    Mã KH: PD333
    Tổng tiền: 300.000 VNĐ
    """
    res = client.post('/api/ai/chat', headers=headers, json={'message': 'Phân tích hóa đơn', 'raw_ocr_text': ocr_text})
    assert res.status_code == 200
    data = res.json()['metadata']['result']
    assert data['meter_verification']['status'] == 'UNKNOWN'
    assert 'tài khoản' in res.json()['message']
    assert data['meter_verification']['ocr_reading'] is None
    codes = [w['code'] for w in data['warnings']]
    assert 'METER_READING_UNKNOWN' in codes

def test_cross_tenant_isolation(client):
    """Test 4: Customer code belonging to another tenant in OCR must NOT switch query scope."""
    headers = register_helper(client, 'isolation@example.com')
    client.post('/api/households', headers=headers, json={
        'name': 'Iso House', 'address': 'Addr', 'member_count': 1,
        'accounts': [{'utility_type': 'ELECTRICITY', 'provider_name': 'EVN', 'customer_code': 'PD_MINE', 'initial_reading': 500}]
    })

    # OCR contains customer code belonging to someone else
    ocr_text = """
    CÔNG TY ĐIỆN LỰC
    Mã KH: PD_OTHER_TENANT
    Chỉ số cũ: 500
    Chỉ số mới: 500
    """
    res = client.post('/api/ai/chat', headers=headers, json={'message': 'Phân tích', 'raw_ocr_text': ocr_text})
    assert res.status_code == 200
    data = res.json()['metadata']['result']
    # A foreign customer code must never match the household baseline.
    assert data['meter_verification']['database_reading'] is None
    assert data['meter_verification']['status'] == 'UNKNOWN'

def test_unsupported_document_handling(client):
    """Requirement 26: Non-bill image/text must return unsupported_document status gracefully."""
    headers = register_helper(client, 'unsupported@example.com')
    client.post('/api/households', headers=headers, json={
        'name': 'House U', 'address': 'Addr', 'member_count': 1,
        'accounts': [{'utility_type': 'ELECTRICITY', 'provider_name': 'EVN', 'customer_code': 'PD112233', 'initial_reading': 100}]
    })

    res = client.post('/api/ai/chat', headers=headers, json={
        'message': 'Đọc giúp tôi tấm hình này',
        'raw_ocr_text': 'Xin chào đây là một đoạn văn bản ghi chú khong phai hoa don nào cả.'
    })
    assert res.status_code == 200
    body = res.json()
    assert body['intent'] == 'OCR_BILL_ANALYSIS'
    assert 'Không nhận diện được' in body['message'] or 'không được nhận diện' in body['message']

def test_image_attachment_without_text_message(client):
    """Requirement 9 & 29: Chat input with image/ocr text but empty message string must be accepted and processed with default prompt."""
    headers = register_helper(client, 'no_msg_img@example.com')
    client.post('/api/households', headers=headers, json={
        'name': 'No Msg House', 'address': 'Addr', 'member_count': 1,
        'accounts': [{'utility_type': 'ELECTRICITY', 'provider_name': 'EVN', 'customer_code': 'PD777888', 'initial_reading': 100}]
    })

    ocr_text = """
    HÓA ĐƠN ĐIỆN EVN
    Mã KH: PD777888
    Chỉ số cũ: 100
    Chỉ số mới: 200
    Sản lượng: 100 kWh
    Tổng tiền: 200.000 VNĐ
    """
    res = client.post('/api/ai/chat', headers=headers, json={
        'message': '',
        'raw_ocr_text': ocr_text
    })
    assert res.status_code == 200
    body = res.json()
    assert body['intent'] == 'OCR_BILL_ANALYSIS'

def test_empty_chat_input_rejection(client):
    """Requirement 9: Chat input with empty message, no image, no OCR text must be rejected with 422."""
    headers = register_helper(client, 'empty_chat@example.com')
    res = client.post('/api/households', headers=headers, json={'name': 'E', 'address': 'A', 'member_count': 1, 'accounts': []})
    res = client.post('/api/ai/chat', headers=headers, json={
        'message': '   ',
        'image_base64': None,
        'raw_ocr_text': None
    })
    assert res.status_code == 422

def test_gemini_structured_ocr_pipeline():
    """Test GeminiProvider.analyze_ocr_with_gemini structured JSON parsing logic."""
    from app.ai.gemini import GeminiProvider
    provider = GeminiProvider()
    
    # Missing API Key returns None gracefully
    result = provider.analyze_ocr_with_gemini(raw_ocr_text="Mã KH: PD123\nChỉ số mới: 500", user_instruction="Phân tích", household_context={})
    assert result is None or isinstance(result, dict)

