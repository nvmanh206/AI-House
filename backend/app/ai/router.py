import re
import unicodedata
from app.security import today

def normalize_message(message):
    return ''.join(c for c in unicodedata.normalize('NFD', message.lower().replace('đ', 'd')) if unicodedata.category(c) != 'Mn')

def has_phrase(text, phrase):
    """Check if phrase exists as whole words in text (preventing substring collisions like 'anh' in 'sanh')."""
    return bool(re.search(r'(?:\b|^)' + re.escape(phrase) + r'(?:\b|$)', text))


def route(message):
    text = normalize_message(message)
    
    if any(has_phrase(text, w) for w in ('ban la ai','ban ten gi','gioi thieu ban','xin chao','hello','chao ban')):
        return 'assistant_identity'
    if (has_phrase(text, 'bieu gia') and any(has_phrase(text, w) for w in ('trong he thong','da luu','cau hinh'))) or has_phrase(text, 'gia demo'):
        return 'configured_tariff'
    if has_phrase(text, 'gia') and any(has_phrase(text, w) for w in ('dien','nuoc')) and any(has_phrase(text, w) for w in ('moi nhat','hien hanh')):
        return 'public_tariff'
    # Stable explanations do not need a household history or live Search.
    if not any(has_phrase(text, w) for w in ('hien nay','hien tai','moi nhat','thang nay','thang toi')) and any(has_phrase(text, w) for w in (
        'kwh la gi','so dien la gi','cach doc cong to','doc chi so cong to',
        'cach tinh tien dien','cach tinh tien nuoc','tinh theo bac thang',
        'bac thang la gi','bac thang nhu the nao','lam sao tiet kiem','cach tiet kiem')):
        return 'basic_knowledge'
    if (has_phrase(text, 'dien') or has_phrase(text, 'nuoc')) and any(has_phrase(text, w) for w in ('giup','ho tro','tra cuu','xem')) and not any(has_phrase(text, w) for w in ('hoa don','nha toi','nha minh','tieu thu','chi so','thang nay')):
        return 'public_tariff'
    # Non-tariff household calculations / individual bill analysis / comparison
    is_calculation_or_forecast = any(has_phrase(text, w) for w in ('het bao nhieu', 'tinh hoa don', 'du doan', 'so sanh', 'kwh', '350', 'thang nay het'))
    
    if not is_calculation_or_forecast:
        tariff_keywords = (
            'gia dien', 'gia tien dien', 'bieu gia', 'gia nuoc', 'gia tien nuoc',
            'tien dien hien nay', 'may bac', 'co vat chua', 'ap dung tu ngay',
            'ngay hieu luc', 'tang gia dien', 'dieu chinh gia'
        )
        if any(has_phrase(text, w) for w in tariff_keywords):
            return 'public_tariff'

    for words, intent in [
        (['anh hoa don', 'hoa don ocr', 'doc hoa don', 'quet hoa don', 'phan tich hoa don', 'ocr hoa don', 'upload hoa don', 'anh qua hoa don'], 'ocr_bill_analysis'),
        (['thang toi', 'du bao', 'uoc tinh'], 'bill_forecast'),
        (['tiet kiem'], 'saving_recommendation'),
        (['bat thuong'], 'anomaly_detection'),
        (['so sanh'], 'consumption_comparison'),
        (['chua thanh toan', 'tra tien', 'thanh toan'], 'payment_assistant'),
        (['tai sao', 'hoa don', 'tien dien'], 'bill_analysis'),
        (['giai thich'], 'explain_result'),
        (['bao nhieu', 'tieu thu'], 'consumption_analysis'),
    ]:
        if any(has_phrase(text, w) for w in words):
            return intent
            
    if any(has_phrase(text, w) for w in ('tong quan','ho gia dinh','nha toi','nha minh')):
        return 'household_overview'
    return 'general_chat'


PROVINCES_CITIES = [
    'Thái Nguyên', 'Hà Nội', 'TP.HCM', 'TP HCM', 'Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ',
    'An Giang', 'Bà Rịa - Vũng Tàu', 'Bà Rịa Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu',
    'Bắc Ninh', 'Bến Tre', 'Bình Định', 'Bình Dương', 'Bình Phước', 'Bình Thuận', 'Cà Mau',
    'Cao Bằng', 'Đắk Lắk', 'Đắk Nông', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai',
    'Hà Giang', 'Hà Nam', 'Hà Tĩnh', 'Hải Dương', 'Hậu Giang', 'Hòa Bình', 'Hưng Yên',
    'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Lào Cai',
    'Long An', 'Nam Định', 'Nghệ An', 'Ninh Bình', 'Ninh Thuận', 'Phú Thọ', 'Phú Yên',
    'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị', 'Sóc Trăng',
    'Sơn La', 'Tây Ninh', 'Thái Bình', 'Thanh Hóa', 'Thừa Thiên Huế', 'Tiền Giang',
    'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái'
]

def extract_tariff_args(message: str) -> dict:
    norm = normalize_message(message)
    utility = 'WATER' if 'nuoc' in norm else 'ELECTRICITY'
    location = None
    msg_lower = message.lower()
    for p in PROVINCES_CITIES:
        if p.lower() in msg_lower:
            location = p
            break
    if not location:
        for p in PROVINCES_CITIES:
            p_norm = ''.join(c for c in unicodedata.normalize('NFD', p.lower().replace('đ', 'd')) if unicodedata.category(c) != 'Mn')
            if p_norm in norm:
                location = p
                break
    customer_group = 'BUSINESS' if 'kinh doanh' in norm else ('PRODUCTION' if 'san xuat' in norm else 'HOUSEHOLD')
    target_date = str(today())
    query_type = 'CURRENT_TARIFF'
    month_match = re.search(r'thang\s*(\d{1,2})[\/\-](\d{4})', norm) or re.search(r'(\d{1,2})[\/\-](\d{4})', norm)
    if month_match:
        m, y = int(month_match.group(1)), int(month_match.group(2))
        target_date = f"{y:04d}-{m:02d}-01"
        query_type = 'HISTORICAL_TARIFF'
    elif any(w in norm for w in ('may bac', 'bac', 'cau truc')):
        query_type = 'TARIFF_STRUCTURE'
    elif any(w in norm for w in ('tang gia', 'dieu chinh', 'thay doi')):
        query_type = 'TARIFF_CHANGE'
    elif 'vat' in norm:
        query_type = 'VAT_INFORMATION'
    elif any(w in norm for w in ('ngay ap dung', 'ngay hieu luc', 'ap dung tu')):
        query_type = 'EFFECTIVE_DATE'
    return {
        'utility': utility,
        'location': location,
        'customer_group': customer_group,
        'target_date': target_date,
        'query_type': query_type
    }
