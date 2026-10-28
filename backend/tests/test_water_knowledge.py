from app.knowledge.service import seed_documents
from app.knowledge.crawler import extract
import pytest


def test_local_water_article_keeps_regional_tables_in_order():
    body='''<html><body><nav>Navigation</nav><td class="news_detail_detail">
    <p>Khu vực A: kể từ ngày 15/10/2026</p><table><tr><td>Giá A</td><td>1.000 đồng/m3</td></tr></table>
    <p>Khu vực B</p><table><tr><td>Giá B</td><td>2.000 đồng/m3</td></tr></table></td></body></html>'''.encode()
    text,_,_=extract(body,'text/html')
    assert text.index('Khu vực A') < text.index('Giá A') < text.index('Khu vực B') < text.index('Giá B')
    assert 'Navigation' not in text


def test_effective_date_ke_tu_is_explicit_evidence_not_publication_date():
    from app.knowledge.service import validate_metadata
    text='Thông báo giá bán nước sạch sinh hoạt kể từ ngày 15/10/2026.'
    result=validate_metadata({'effective_from':'2026-10-15','effective_quote':text},text)
    assert result['effective_from']=='2026-10-15'
    result=validate_metadata({'effective_from':'2026-10-16','effective_quote':text},text)
    assert result['effective_from'] is None


def test_faq_fragment_indexes_only_selected_answer_with_question():
    body=b'<html><body><div class="accordion-item"><h2>Meter replacement</h2><div id="meter">Free replacement for broken meters.</div></div><div class="accordion-item"><h2>Prices</h2><div id="prices">Unverified tariff image</div></div></body></html>'
    text,_,_=extract(body,'text/html',fragment='meter')
    assert 'Meter replacement' in text and 'Free replacement' in text
    assert 'Unverified tariff' not in text
    assert seed_documents(body,'https://example.com/faq#meter',{'seed_mode':'DOCUMENT','name':'Water'})=={'https://example.com/faq#meter':'Meter replacement'}
    with pytest.raises(ValueError,match='DOCUMENT_SECTION_NOT_FOUND'):
        extract(body,'text/html',fragment='missing')


def test_water_faq_keeps_questions_lists_and_prices():
    body='''<html><body><nav>Navigation</nav><div class="accordion-item">
    <h2><button>Giá nước áp dụng thế nào?</button></h2><div class="accordion-body"><ul>
    <li>Áp dụng từ 01/01/2026 tại Hà Nội.</li><li>Mức 10 m³: 8.500 đồng/m³.</li>
    </ul></div></div></body></html>'''.encode()
    text,_,_=extract(body,'text/html')
    assert 'Giá nước áp dụng thế nào?' in text
    assert 'Áp dụng từ 01/01/2026' in text
    assert '8.500 đồng/m³' in text
    assert 'Navigation' not in text


def test_water_price_section_keeps_effective_date_and_customer_conditions():
    body='''<html><body><section class="wp-section"><h1>Giá nước Hà Nội</h1>
    <div>Hiệu lực từ: 01/01/2026</div><table><tr><td>Hộ dân cư khác</td><td>8.500 đồng/m³</td></tr></table>
    <p>Chưa bao gồm thuế và phí.</p></section><div>Login form</div></body></html>'''.encode()
    text,blocks,_=extract(body,'text/html')
    assert 'Hiệu lực từ: 01/01/2026' in text
    assert 'Hộ dân cư khác' in text and 'Chưa bao gồm thuế và phí.' in text
    assert 'Login form' not in text
    assert any('<table' in b for b in blocks)

def test_direct_water_document_is_not_restricted_to_evn_paths():
    body=b'<html><head><meta property="og:title" content="SAWACO customer guidance"></head><body><main>Water guidance</main></body></html>'
    url='https://cskh.sawaco.com.vn/ho_tro/hoi_dap'
    assert seed_documents(body,url,{'seed_mode':'DOCUMENT','name':'SAWACO'})=={url:'SAWACO customer guidance'}
    assert seed_documents(body,url,{'seed_mode':'LISTING','name':'SAWACO'})=={}
