import unicodedata

def route(message):
    text = ''.join(c for c in unicodedata.normalize('NFD', message.lower().replace('đ', 'd')) if unicodedata.category(c) != 'Mn')
    
    if any(w in text for w in ('ban la ai','ban ten gi','gioi thieu ban','xin chao','hello','chao ban')):
        return 'assistant_identity'
    if ('bieu gia' in text and any(w in text for w in ('trong he thong','da luu','cau hinh'))) or 'gia demo' in text:
        return 'configured_tariff'
    if 'gia' in text and any(w in text for w in ('dien','nuoc')) and any(w in text for w in ('moi nhat','hien hanh')):
        return 'public_tariff'
    # Stable explanations do not need a household history or live Search.
    if not any(w in text for w in ('hien nay','hien tai','moi nhat','thang nay','thang toi')) and any(w in text for w in (
        'kwh la gi','so dien la gi','cach doc cong to','doc chi so cong to',
        'cach tinh tien dien','cach tinh tien nuoc','tinh theo bac thang',
        'bac thang la gi','bac thang nhu the nao','lam sao tiet kiem','cach tiet kiem')):
        return 'basic_knowledge'
    if ('dien' in text or 'nuoc' in text) and any(w in text for w in ('giup','ho tro','tra cuu','xem')) and not any(w in text for w in ('hoa don','nha toi','nha minh','tieu thu','chi so','thang nay')):
        return 'public_tariff'
    # Non-tariff household calculations / individual bill analysis / comparison
    is_calculation_or_forecast = any(w in text for w in ('het bao nhieu', 'tinh hoa don', 'du doan', 'so sanh', 'kwh', '350', 'thang nay het'))
    
    if not is_calculation_or_forecast:
        tariff_keywords = (
            'gia dien', 'gia tien dien', 'bieu gia', 'gia nuoc', 'gia tien nuoc',
            'tien dien hien nay', 'may bac', 'co vat chua', 'ap dung tu ngay',
            'ngay hieu luc', 'tang gia dien', 'dieu chinh gia'
        )
        if any(w in text for w in tariff_keywords):
            return 'public_tariff'

    for words, intent in [
        (['thang toi', 'du bao', 'uoc tinh'], 'bill_forecast'),
        (['tiet kiem'], 'saving_recommendation'),
        (['bat thuong'], 'anomaly_detection'),
        (['so sanh'], 'consumption_comparison'),
        (['chua thanh toan', 'tra tien', 'thanh toan'], 'payment_assistant'),
        (['tai sao', 'hoa don', 'tien dien'], 'bill_analysis'),
        (['giai thich'], 'explain_result'),
        (['bao nhieu', 'tieu thu'], 'consumption_analysis'),
    ]:
        if any(w in text for w in words):
            return intent
            
    if any(w in text for w in ('tong quan','ho gia dinh','nha toi','nha minh')):
        return 'household_overview'
    return 'general_chat'
