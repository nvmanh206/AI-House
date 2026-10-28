import base64
from io import BytesIO

import pytest
from PIL import Image
from pydantic import ValidationError
from sqlalchemy import select, func

from app.ai.contracts import Extraction, Reply
from app.ai.multimodal import validate_image
from app.ai.multimodal import overview, verify_extraction
from app.ai.gemini_structured import StructuredGemini
from app.config import settings
from app.models import AIAnalysis, MeterReading, Bill, Payment
from app.security import DomainError
from conftest import reading, register, setup_house


def image_data(fmt='PNG'):
    output = BytesIO()
    Image.new('RGB', (32, 32), 'white').save(output, format=fmt)
    return 'data:image/' + ('jpeg' if fmt == 'JPEG' else fmt.lower()) + ';base64,' + base64.b64encode(output.getvalue()).decode()


def extraction(**overrides):
    data = dict(document_status='READABLE', document_type='ELECTRICITY_BILL', requested_task='COMPARE_READING',
        extracted_data=dict(provider_name=None, customer_code=None, meter_code=None, billing_period='2026-08',
            previous_reading='100', current_reading='150', consumption='50', unit='kWh', total_amount=None, currency='VND', due_date=None),
        uncertain_fields=[], missing_fields=['total_amount', 'customer_code', 'meter_code', 'provider_name', 'due_date'])
    data.update(overrides)
    return Extraction.model_validate(data)


@pytest.fixture
def gemini_mode(monkeypatch):
    monkeypatch.setattr(settings, 'llm_provider', 'gemini')
    monkeypatch.setattr(StructuredGemini, 'extract', lambda self, **kw: extraction())
    monkeypatch.setattr(StructuredGemini, 'respond', lambda self, **kw: Reply(requested_task='COMPARE_READING',status='ANSWERED', message='Mình đã đối chiếu đúng kỳ bạn gửi.', evidence_refs=['verification:reading']))


@pytest.mark.parametrize('fmt,mime', [('PNG','image/png'), ('JPEG','image/jpeg'), ('WEBP','image/webp')])
def test_image_decodes_real_supported_formats(fmt, mime):
    result = validate_image(image_data(fmt))
    assert result['mimeType'] == mime


def test_image_metadata_is_removed_before_transmission():
    output = BytesIO()
    image = Image.new('RGB', (20, 20), 'white')
    exif = image.getexif()
    exif[270] = 'private-location-marker'
    image.save(output, format='PNG', exif=exif)
    cleaned = validate_image(base64.b64encode(output.getvalue()).decode())
    with Image.open(BytesIO(base64.b64decode(cleaned['data']))) as decoded:
        assert not decoded.getexif()


@pytest.mark.parametrize('payload', ['data:image/png;base64,SGVsbG8=', 'data:image/gif;base64,R0lGODlh', 'not-base64', base64.b64encode(b'x' * (10*1024*1024+1)).decode()], ids=['fake-png','gif','bad-base64','oversized'])
def test_image_rejects_fake_corrupt_and_oversized(payload):
    with pytest.raises(DomainError):
        validate_image(payload)


def test_extraction_preserves_zero_and_rejects_invalid_dates_and_numbers():
    data = extraction().model_dump(mode='json')
    data['extracted_data']['current_reading'] = '0'
    assert Extraction.model_validate(data).extracted_data.current_reading == '0'
    for field, value in [('total_amount', '1.000,50'), ('current_reading', '-1'), ('due_date', '2026-02-30'), ('billing_period', '2026-13')]:
        invalid = extraction().model_dump(mode='json')
        invalid['extracted_data'][field] = value
        with pytest.raises(ValidationError):
            Extraction.model_validate(invalid)


def test_uncertain_value_cannot_be_used_as_fact():
    data = extraction().model_dump(mode='json')
    data['uncertain_fields'] = ['current_reading']
    with pytest.raises(ValidationError):
        Extraction.model_validate(data)


def test_two_stage_image_flow_is_read_only_and_retains_context(client, ready, db, gemini_mode, monkeypatch):
    headers, _, meter = ready
    assert reading(client, headers, meter, month=8, current=150).status_code == 201
    calls = []
    def respond(self, **kw):
        calls.append(kw)
        return Reply(requested_task='COMPARE_READING',status='ANSWERED', message='Chỉ số kỳ này khớp với bản ghi của bạn.', evidence_refs=['verification:reading'])
    monkeypatch.setattr(StructuredGemini, 'respond', respond)
    before = [db.scalar(select(func.count()).select_from(model)) for model in (MeterReading, Bill, Payment)]
    response = client.post('/api/ai/chat', headers=headers, json={'message':'Kiểm tra chỉ số giúp mình', 'image_base64':image_data()})
    assert response.status_code == 200, response.text
    body = response.json()
    result = body['metadata']['result']
    assert result['verification']['reading']['status'] == 'MATCH'
    assert result['extracted_data']['current_reading'] == '150'
    assert body['message'] == 'Chỉ số kỳ này khớp với bản ghi của bạn.'
    assert 'user' not in calls[0]['overview'] and 'email' not in str(calls[0]['overview'])
    conversation = body['metadata']['conversation_id']
    follow = client.post('/api/ai/chat', headers=headers, json={'message':'Còn hóa đơn đó thì sao?', 'conversation_id':conversation})
    assert follow.status_code == 200
    assert len(calls[1]['history']) == 2
    assert calls[1]['history'][0]['extraction']['extracted_data']['current_reading'] == '150'
    assert calls[1]['extraction']['extracted_data']['current_reading'] == '150'
    assert before == [db.scalar(select(func.count()).select_from(model)) for model in (MeterReading, Bill, Payment)]
    foreign = register(client, 'other-chat@example.com')
    setup_house(client, foreign)
    assert client.post('/api/ai/chat', headers=foreign, json={'message':'x', 'conversation_id':conversation}).status_code == 404


def test_bad_reference_and_provider_failure_do_not_use_canned_answer(client, ready, gemini_mode, monkeypatch):
    headers, _, _ = ready
    monkeypatch.setattr(StructuredGemini, 'respond', lambda self, **kw: Reply(requested_task='OTHER',status='ANSWERED', message='Sai căn cứ', evidence_refs=['bill:foreign']))
    # An unsupported Gemini reply is never shown; the answer degrades to local records instead.
    bad = client.post('/api/ai/chat', headers=headers, json={'message':'Điện nhà mình thế nào?'})
    assert bad.status_code == 502 and bad.json()['error']['code']=='GEMINI_INVALID_EVIDENCE'
    def unavailable(self, **kw):
        raise DomainError('GEMINI_QUOTA', 'Gemini hết hạn mức.', 429)
    monkeypatch.setattr(StructuredGemini, 'respond', unavailable)
    response = client.post('/api/ai/chat', headers=headers, json={'message':'Điện nhà mình thế nào?'})
    assert response.status_code == 429
    assert response.json()['error']['code'] == 'GEMINI_QUOTA'


def test_overview_keeps_all_debt_and_six_periods_without_member_profiles():
    from types import SimpleNamespace
    rows = [{'id':str(i), 'utility_account_id':'a', 'period':f'2026-{(i%9)+1:02}', 'utility_type':'ELECTRICITY',
             'status':'UNPAID', 'final_amount':'0.10'} for i in range(61)]
    service = SimpleNamespace(accounts=lambda:[], meters=lambda:[], history=lambda:[], bills=lambda:rows)
    data, refs = overview(service)
    assert len(data['periods']) == 6
    assert data['total_unpaid'] == '6.10'
    assert data['unpaid_count'] == 61 and data['unpaid_has_more']
    assert len(data['unpaid_bills']) == 50
    assert 'user' not in data and 'household' not in data


def test_structured_provider_rejects_invalid_and_truncated_json(monkeypatch):
    import httpx
    monkeypatch.setattr(settings, 'gemini_api_key', 'test-key')
    for finish, content in [('STOP','not JSON'), ('MAX_TOKENS','{}'), ('STOP','{"status":"ANSWERED","message":"x","evidence_refs":[],"extra":true}')]:
        monkeypatch.setattr(httpx,'post',lambda *a,**kw: httpx.Response(200,json={'candidates':[{'finishReason':finish,'content':{'parts':[{'text':content}]}}]}))
        with pytest.raises(DomainError) as exc:
            StructuredGemini()._generate(Reply, 'test', [{'text':'test'}])
        assert exc.value.code == 'GEMINI_INVALID_RESPONSE'


def test_mismatched_units_and_arithmetic_prevent_reading_match():
    from types import SimpleNamespace
    data = extraction().model_dump(mode='json')
    data['extracted_data']['unit'] = 'm³'
    data['extracted_data']['consumption'] = '999'
    service = SimpleNamespace(accounts=lambda:[{'id':'a','utility_type':'ELECTRICITY'}],
        meters=lambda:[{'id':'m','utility_account_id':'a'}],
        history=lambda:[{'id':'r','meter_id':'m','period':'2026-08','current_reading':'150'}], bills=lambda:[])
    result = verify_extraction(service, Extraction.model_validate(data))
    assert result['reading']['status'] == 'UNKNOWN'
    assert set(result['consistency']) == {'UNIT_MISMATCH','CONSUMPTION_MISMATCH'}


@pytest.mark.parametrize('original_task,current_task,blocked', [('COMPARE_AMOUNT','OTHER',False), ('READ_INFO','COMPARE_AMOUNT',True)])
def test_followup_guard_uses_current_task(client, ready, gemini_mode, monkeypatch, original_task, current_task, blocked):
    from types import SimpleNamespace
    headers, _, _ = ready
    monkeypatch.setattr(StructuredGemini,'extract',lambda self,**kw: extraction(requested_task=original_task))
    monkeypatch.setattr(StructuredGemini,'respond',lambda self,**kw: Reply(requested_task=original_task,status='NEEDS_CLARIFICATION',message='Cần thêm thông tin.',evidence_refs=[]))
    first=client.post('/api/ai/chat',headers=headers,json={'message':'Đọc ảnh giúp tôi','image_base64':image_data()})
    assert first.status_code == 200
    class CurrentReply(SimpleNamespace):
        def model_dump(self):
            return vars(self)
    monkeypatch.setattr(StructuredGemini,'respond',lambda self,**kw: CurrentReply(
        status='ANSWERED',message='Phản hồi cho yêu cầu hiện tại.',evidence_refs=[],requested_task=current_task))
    response=client.post('/api/ai/chat',headers=headers,json={'message':'Câu hỏi tiếp theo','conversation_id':first.json()['metadata']['conversation_id']})
    assert response.status_code == (502 if blocked else 200)
    if blocked: assert response.json()['error']['code']=='GEMINI_UNSUPPORTED_CONCLUSION'
    else: assert response.json()['message']=='Phản hồi cho yêu cầu hiện tại.'


def test_can_explain_inconsistent_image_without_claiming_a_match(client,ready,gemini_mode,monkeypatch):
    headers,_,_=ready
    data=extraction(requested_task='EXPLAIN').model_dump(mode='json')
    data['extracted_data']['consumption']='999'
    monkeypatch.setattr(StructuredGemini,'extract',lambda self,**kw: Extraction.model_validate(data))
    monkeypatch.setattr(StructuredGemini,'respond',lambda self,**kw: Reply(requested_task='EXPLAIN',status='ANSWERED',
        message='Sản lượng ghi trên ảnh không bằng hiệu hai chỉ số; cần kiểm tra lại hóa đơn.',evidence_refs=['verification:consistency']))
    response=client.post('/api/ai/chat',headers=headers,json={'message':'Số liệu có hợp lý không?','image_base64':image_data()})
    assert response.status_code == 200
    assert response.json()['metadata']['result']['verification']['reading']['status'] == 'UNKNOWN'
