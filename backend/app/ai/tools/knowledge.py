import unicodedata
from decimal import Decimal
from app.ai.provider import get_provider
from app.config import settings
from app.security import today, DomainError
from app.ai.validators import sanitize

def basic_explanation(message):
    text=''.join(c for c in unicodedata.normalize('NFD',message.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')
    if 'tiet kiem' in text:
        return 'Bạn có thể tiết kiệm điện/nước bằng cách tắt thiết bị khi không dùng, chọn chế độ tiết kiệm phù hợp, kiểm tra vòi nước rò rỉ và ghi chỉ số đều đặn. Đây là gợi ý chung; mình chưa có bằng chứng thiết bị nào trong nhà bạn đang tiêu thụ nhiều.'
    if 'cong to' in text:
        return 'Đọc chỉ số tổng tích lũy trên công tơ đúng loại và đơn vị (điện: kWh; nước: m³). Lượng dùng trong kỳ = chỉ số mới − chỉ số trước. Trong ứng dụng, vào Nhập chỉ số, chọn công tơ và kỳ rồi nhập chỉ số hiện tại; hệ thống tự tính lượng dùng. Nếu công tơ đã thay hoặc chỉ số quay về thấp hơn, không nhập như một kỳ bình thường.'
    if 'la gi' in text and ('kwh' in text or 'so dien' in text):
        return 'kWh là đơn vị điện năng; 1 số điện tương ứng 1 kWh. Ví dụ, thiết bị dùng công suất 1 kW liên tục trong 1 giờ tiêu thụ 1 kWh. Lượng điện = công suất (kW) × thời gian (giờ). Số tiền còn phụ thuộc biểu giá, các bậc và thuế/phí áp dụng.'
    return 'Giá bậc thang nghĩa là lượng dùng được chia vào từng khoảng tiêu thụ. Tiền trước thuế/phí = tổng (lượng dùng trong từng bậc × đơn giá của bậc đó), không lấy toàn bộ lượng dùng nhân với giá bậc cao nhất. Lượng dùng = chỉ số mới − chỉ số trước. Mức giá cụ thể phải xem biểu giá và ngày hiệu lực; đây là cách tính chung, không phải xác nhận giá hiện hành.'

def configured_tariff_text(service,utility):
    service.member()
    tariffs=[t for t in service.tariffs_for_agent() if t['utility_type']==utility and t.get('tiers')]
    if not tariffs:
        return 'Hộ đang chọn chưa có biểu giá phù hợp được cấu hình. Bạn có thể nhờ admin thêm biểu giá có nguồn và ngày hiệu lực.', []
    unit='kWh' if utility=='ELECTRICITY' else 'm³'
    parts=['BIỂU GIÁ ĐÃ CẤU HÌNH CHO HỘ ĐANG CHỌN — không phải kết quả tra giá chính thức theo địa phương bạn hỏi.']
    summaries=[]
    for tariff in tariffs:
        demo='demo' in (tariff.get('name','')+' '+tariff.get('provider_name','')+' '+tariff['version']).lower()
        parts.append(f"{tariff.get('name','Biểu giá')} · {tariff.get('provider_name','')} · phiên bản {tariff['version']} · hiệu lực ghi trong hệ thống từ {tariff.get('effective_from','chưa rõ')}." + (' DỮ LIỆU DEMO, chỉ để minh họa.' if demo else ' Chưa xác minh với nhà cung cấp.'))
        for tier in tariff['tiers']:
            lower=Decimal(tier['from_value']);upper=tier['to_value']
            interval=f'trên {lower:g} đến {Decimal(upper):g}' if upper is not None else f'trên {lower:g}'
            parts.append(f"- {interval} {unit}: {Decimal(tier['unit_price']):,.0f} VND/{unit}.")
        summaries.append({'version':tariff['version'],'source':'CONFIGURED','is_demo':demo})
    parts.append('Các đơn giá cấu hình dùng tính ước tính trong ứng dụng, chưa gồm thuế/phí. Mình không thay đổi biểu giá hoặc hóa đơn.')
    return sanitize('\n'.join(parts)),summaries

def useful_fallback(service,utility,answer):
    local,summaries=configured_tariff_text(service,utility)
    # Keep the failure signal for monitoring, without treating local configuration as web evidence.
    answer['message']='Mình chưa xác minh được giá chính thức từ Internet lúc này.\n\n'+basic_explanation('cách tính theo bậc thang')+'\n\n'+local+'\n\nBạn vẫn có thể hỏi “kWh là gì?” hoặc “cách đọc công tơ?” mà không cần tra web.'
    if answer.get('metadata',{}).get('error_code')=='GEMINI_SEARCH_QUOTA':
        answer['message']+=' Phần tra giá mới nhất cần quota Google Search hoạt động trở lại.'
    answer['sources']=[]
    answer.setdefault('metadata',{}).update({'grounded':False,'fallback':'LOCAL_HELP','configured_tariffs':summaries})
    return answer

def get_public_tariff(service, *, utility, day=None, location=None, customer_group="HOUSEHOLD", query_type="CURRENT_TARIFF"):
    service.member()
    day = day or today()
    if settings.llm_provider == 'gemini':
        try:
            answer=get_provider().search_tariff(utility=utility,day=day,location=location,customer_group=customer_group,query_type=query_type)
        except DomainError as exc:
            if not exc.code.startswith(('GEMINI_','SEARCH_')): raise
            answer={'message':exc.message,'sources':[],'metadata':{'provider':'gemini','error_code':exc.code,'grounded':False,'read_only':True}}
        if answer.get('metadata',{}).get('grounded'): return answer
        answer.setdefault('metadata',{}).setdefault('error_code','SEARCH_UNVERIFIED')
    else:
        answer={'message':'Trợ lý đang offline.','sources':[], 'metadata':{'provider':'deterministic','grounded':False,'read_only':True}}
    return useful_fallback(service,utility,answer)
