import httpx
import pytest
from app.config import settings
from app.ai.gemini import GeminiProvider, build_public_tariff_question
from app.ai.router import route
from app.ai.agent import extract_tariff_args
from app.security import DomainError
from conftest import register, setup_house

def payload():
    return {
        'candidates': [{
            'finishReason': 'STOP',
            'content': {
                'parts': [
                    {'text': 'Không công bố suy nghĩ.', 'thought': True},
                    {'text': 'Giá theo bậc, cần xem ngày hiệu lực.'}
                ]
            },
            'groundingMetadata': {
                'groundingChunks': [{'web': {'uri': 'https://evn.com.vn/example', 'title': 'EVN'}}],
                'groundingSupports': [{'segment': {'text': 'Giá theo bậc, cần xem ngày hiệu lực.'}, 'groundingChunkIndices': [0]}],
                'searchEntryPoint': {'renderedContent': '<div>Google Search</div>'}
            }
        }]
    }

# Test 1: "giá điện thái nguyên hôm nay" -> ELECTRICITY, Thái Nguyên
def test_args_electricity_location():
    args = extract_tariff_args("giá điện thái nguyên hôm nay")
    assert args['utility'] == 'ELECTRICITY'
    assert args['location'] == 'Thái Nguyên'

# Test 2: "giá nước thái nguyên" -> WATER, Thái Nguyên
def test_args_water_location():
    args = extract_tariff_args("giá nước thái nguyên")
    assert args['utility'] == 'WATER'
    assert args['location'] == 'Thái Nguyên'

# Test 3: "giá nước hiện tại" -> Yêu cầu location (Location Rule)
def test_water_without_location_asks_user(client):
    headers = register(client)
    setup_house(client, headers)
    r = client.post('/api/ai/chat', headers=headers, json={'message': 'giá nước hiện tại'})
    assert r.status_code == 200
    assert 'Bạn muốn tra giá nước tại tỉnh/thành phố nào?' in r.json()['message']

# Test 4: "350 kWh hết bao nhiêu?" -> Không route public_tariff
def test_kwh_calculation_not_public_tariff():
    assert route('350 kWh hết bao nhiêu?') != 'public_tariff'
    assert route('tính hóa đơn tháng này 350 kWh') != 'public_tariff'

# Test 5: "giá điện tháng 8/2025" -> Historical tariff
def test_historical_tariff_args():
    args = extract_tariff_args("giá điện tháng 8/2025")
    assert args['utility'] == 'ELECTRICITY'
    assert args['target_date'] == '2025-08-01'
    assert args['query_type'] == 'HISTORICAL_TARIFF'

# Test 6: Search 200 + grounding hợp lệ -> grounded=True
def test_grounding_valid():
    result = GeminiProvider.parse(payload(), '2026-09-07')
    assert result['metadata']['grounded'] is True
    assert len(result['sources']) == 1
    assert result['sources'][0]['url'].startswith('https://')

# Test 7: Search 200 nhưng không có groundingSupports -> grounded=False
def test_grounding_missing_supports():
    data = payload()
    data['candidates'][0]['groundingMetadata']['groundingSupports'] = []
    result = GeminiProvider.parse(data, '2026-09-07')
    assert result['metadata']['grounded'] is False
    assert result['sources'] == []
    assert 'Chưa xác minh được thông tin' in result['message']

# Test 8: Search 429 -> không fallback model memory, trả về thông báo giới hạn trực tuyến
def test_search_429_returns_limited_message(monkeypatch):
    monkeypatch.setattr(settings, 'gemini_api_key', 'test-key')
    monkeypatch.setattr(settings, 'llm_provider', 'gemini')
    monkeypatch.setattr(httpx, 'post', lambda *a, **k: httpx.Response(429, json={'error': {'message': 'Quota exceeded'}}))
    res = GeminiProvider().search_tariff(utility='ELECTRICITY', day='2026-09-07')
    assert res['metadata']['grounded'] is False
    assert 'Tra cứu nguồn trực tuyến hiện đang tạm thời bị giới hạn' in res['message']

# Test 9: Invalid URL -> reject source
def test_invalid_url_rejected():
    data = payload()
    data['candidates'][0]['groundingMetadata']['groundingChunks'][0]['web']['uri'] = 'javascript:alert(1)'
    result = GeminiProvider.parse(data, '2026-09-07')
    assert result['metadata']['grounded'] is False
    assert result['sources'] == []

# Test 10: Canonical search prompt không chứa private household data
def test_canonical_prompt_no_private_data(client, monkeypatch):
    headers = register(client)
    setup_house(client, headers)
    monkeypatch.setattr(settings, 'llm_provider', 'gemini')
    monkeypatch.setattr(settings, 'gemini_api_key', 'test-key')
    captured = []
    def post(url, **kwargs):
        captured.append(kwargs)
        return httpx.Response(200, json=payload())
    monkeypatch.setattr(httpx, 'post', post)
    r = client.post('/api/ai/chat', headers=headers, json={'message': 'Giá điện thái nguyên hôm nay? secret=private-val customer_id=12345'})
    assert r.status_code == 200
    assert r.json()['intent'] == 'PUBLIC_TARIFF'
    sent_payload = str(captured[0]['json'])
    assert 'private-val' not in sent_payload
    assert '12345' not in sent_payload
    assert 'Thái Nguyên' in sent_payload

# Existing route & error tests
@pytest.mark.parametrize('question', ['GIÁ TIỀN ĐIỆN HIỆN NAY LÀ BAO NHIÊU', 'gia dien hien nay', 'Biểu giá điện', 'giá nước thái nguyên', 'TIỀN ĐIỆN HIỆN NAY'])
def test_tariff_route(question):
    assert route(question) == 'public_tariff'

def test_search_missing_key(monkeypatch):
    monkeypatch.setattr(settings, 'gemini_api_key', '')
    monkeypatch.setattr(settings, 'llm_api_key', '')
    with pytest.raises(DomainError) as exc:
        GeminiProvider().search_tariff('ELECTRICITY', '2026-09-07')
    assert exc.value.code == 'GEMINI_KEY_REQUIRED'
