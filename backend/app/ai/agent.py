from decimal import Decimal
from app.ai.context import build_context
from app.ai.router import route
from app.ai.registry import SKILLS,TOOLS,instructions
from app.ai.validators import sanitize
from app.ai.provider import get_provider
from app.anomaly_service import AnomalyService
import re
import unicodedata
from app.security import DomainError, today
from app.ai.tools.knowledge import basic_explanation, configured_tariff_text

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
    norm = ''.join(c for c in unicodedata.normalize('NFD', message.lower().replace('đ', 'd')) if unicodedata.category(c) != 'Mn')
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

class Agent:
    def __init__(self,context,service): self.context,self.service=context,service
    def chat(self,message):
        # Recheck authorization at execution, never accept IDs from chat/provider.
        member=self.service.member()
        if member.household_id!=self.context.household_id or member.user_id!=self.context.user_id:
            raise DomainError('FORBIDDEN','Ngữ cảnh truy cập không hợp lệ.',403)
        intent=route(message)
        if intent in ('basic_knowledge','configured_tariff'):
            if intent=='basic_knowledge':
                response=basic_explanation(message); details=[]
            else:
                response,details=configured_tariff_text(self.service,extract_tariff_args(message)['utility'])
            return {'message':response,'intent':intent.upper(),'sources':[],'metadata':{'provider':'deterministic','read_only':True,'configured_tariffs':details,'request_id':self.context.request_id}}
        if intent=='assistant_identity':
            return {'message':'Mình là trợ lý Nhà Mình. Mình giúp bạn xem chỉ số, hóa đơn, so sánh tiêu thụ và dự báo chi phí của gia đình. Mình cũng hỗ trợ tra giá điện/nước theo địa phương qua Gemini + Google Search khi dịch vụ còn hạn mức. Bạn muốn mình giúp việc gì?', 'intent':'ASSISTANT_IDENTITY','sources':[], 'metadata':{'provider':'deterministic','read_only':True,'request_id':self.context.request_id}}
        if intent=='general_chat':
            try:
                provider=get_provider()
                if hasattr(provider,'chat_general'):
                    answer=provider.chat_general(message)
                else:
                    answer={'message':'Mình hỗ trợ điện, nước và hóa đơn gia đình. Bạn có thể hỏi “giá điện Thái Nguyên”, “hóa đơn nào chưa thanh toán?” hoặc “tháng tới tiền điện khoảng bao nhiêu?”.','sources':[],'metadata':{'provider':'deterministic','read_only':True}}
            except DomainError as e:
                answer={'message':'Mình là Trợ lý AI "Nhà Mình", được thiết kế chuyên biệt để hỗ trợ quản lý hóa đơn điện nước và chi tiêu gia đình. Mình chưa thể hỗ trợ các thắc mắc ngoài lĩnh vực năng lượng & gia đình. Bạn hãy hỏi mình về tiền điện, tiền nước hoặc cách tiết kiệm chi phí nhé!','sources':[],'metadata':{'provider':'deterministic','read_only':True,'note':str(e)}}
            answer['intent']='GENERAL_CHAT';answer['metadata']['request_id']=self.context.request_id
            return answer
        if intent=='public_tariff':
            args = extract_tariff_args(message)
            normalized=''.join(c for c in unicodedata.normalize('NFD',message.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')
            if re.search(r'\bdien\b',normalized) and re.search(r'\bnuoc\b',normalized):
                place=f" tại {args['location']}" if args['location'] else ''
                return {'message':f'Mình có thể giúp tra cả điện và nước{place}. Bạn muốn xem loại nào trước? Hãy hỏi “giá điện{place}” hoặc “giá nước{place}” để mình tra riêng từng biểu giá.', 'intent':'PUBLIC_TARIFF','sources':[],'metadata':{'provider':'deterministic','read_only':True,'request_id':self.context.request_id}}
            if args['utility'] == 'WATER' and not args['location']:
                return {
                    'message': 'Bạn muốn tra giá nước tại tỉnh/thành phố nào?',
                    'intent': 'PUBLIC_TARIFF',
                    'sources': [],
                    'metadata': {'request_id': self.context.request_id, 'provider': 'deterministic', 'grounded': False, 'read_only': True}
                }
            answer = TOOLS['get_public_tariff'](
                self.service,
                utility=args['utility'],
                day=args['target_date'],
                location=args['location'],
                customer_group=args['customer_group'],
                query_type=args['query_type'],
            )
            answer['intent']='PUBLIC_TARIFF'
            answer['metadata']['request_id']=self.context.request_id
            return answer
        data=sanitize({name:TOOLS[name](self.service) for name in SKILLS[intent]})
        history=data.get('get_consumption_history',[])
        utility='WATER' if 'nước' in message.lower() else 'ELECTRICITY'
        history=[r for r in history if r['utility_type']==utility]
        unit='m³' if utility=='WATER' else 'kWh'
        label='nước' if utility=='WATER' else 'điện'
        sources=[{'type':'reading','period':r['period'],'source':r['source']} for r in history[-3:]]
        response='Chưa đủ dữ liệu để trả lời. Bạn hãy nhập chỉ số và tạo hóa đơn trước.'
        result={}
        if intent=='bill_forecast':
            periods=len({r['period'] for r in history})
            if periods<2:
                response=f'Hộ đang chọn có {periods} kỳ chỉ số {label}; cần ít nhất 2 kỳ để dự báo. Bạn cần nhập thêm {2-periods} kỳ tại trang Nhập chỉ số. Nếu đã nhập ở hộ khác, hãy chuyển đúng hộ tại trang Hộ gia đình. Mình chưa thể đưa ra số tiền dự báo khi thiếu dữ liệu.'
                result={'available':False,'source':'FORECAST','period_count':periods,'required_periods':2}
            else:
                result=self.service.forecast(utility)
                response=f"Ước tính kỳ tới: {result['predicted_consumption']} {unit}, khoảng {Decimal(result['predicted_amount']):,.0f} VND. Dùng trung bình trọng số {result['period_count']} kỳ; độ tin cậy {result['confidence']}. Đây là FORECAST, không phải hóa đơn chính thức; chưa gồm thuế/phí." if result.get('available') else result['reason']
            return {'message':response,'intent':'BILL_FORECAST','sources':sources,'metadata':{'provider':'deterministic','read_only':True,'result':result,'request_id':self.context.request_id}}
        if intent=='payment_assistant':
            bills=data['get_payment_status']; unpaid=[b for b in bills if b['status'] in ('UNPAID','OVERDUE','PENDING')]
            response='Chưa có hóa đơn.' if not bills else ('Không có hóa đơn chưa thanh toán.' if not unpaid else 'Hóa đơn chưa thanh toán: '+ '; '.join(f"kỳ {b['period']}: {Decimal(b['final_amount']):,.0f} VND, hạn dự kiến {b['due_date']}" for b in unpaid)+'. Ngày cấu hình không phải hạn chính thức từ nhà cung cấp. Bạn có thể ghi nhận thanh toán tại trang Hóa đơn.')
            sources=[{'type':'bill','period':b['period']} for b in unpaid]
        elif history:
            latest=history[-1]
            response=f"Kỳ {latest['period']}, tiêu thụ {label} là {Decimal(latest['consumption']):,.3f} {unit}. Nguồn: {latest['source']} (người dùng tự nhập nếu MANUAL)."
            if intent in ('consumption_comparison','bill_analysis','household_overview') and len(history)>=2:
                previous=Decimal(history[-2]['consumption']); change=(Decimal(latest['consumption'])-previous)/previous*100 if previous else None
                response+=f' So với kỳ trước: {change:+.1f}%.' if change is not None else ' Kỳ trước bằng 0 nên không tính tỷ lệ thay đổi.'
                response+=' Không đủ dữ liệu thiết bị để kết luận nguyên nhân.'
            if intent=='consumption_comparison':
                recent=history[-3:]
                if 'tiền' in message.lower():
                    bills=[b for b in data.get('get_bill_history',[]) if b['utility_type']==utility][:3]
                    response='So sánh tiền '+label+' các kỳ có dữ liệu: '+ '; '.join(f"{b['period']}: {Decimal(b['final_amount']):,.0f} VND ({b['source']})" for b in reversed(bills))+'.' if bills else 'Chưa có hóa đơn để so sánh tiền.'
                    sources=[{'type':'bill','period':b['period'],'source':b['source']} for b in bills]
                else:
                    response='Tiêu thụ '+label+' các kỳ có dữ liệu: '+ '; '.join(f"{r['period']}: {Decimal(r['consumption']):,.3f} {unit} ({r['source']})" for r in recent)+'.'
                response+=' Đây là các kỳ đã nhập gần nhất; không coi kỳ thiếu dữ liệu là 0.'
            if intent in ('bill_analysis','explain_result'):
                bills=[b for b in data.get('get_bill_history',[]) if b['utility_type']==utility]
                if bills:
                    bill=bills[0]; response+=f" Hóa đơn ước tính {Decimal(bill['final_amount']):,.0f} VND, biểu giá phiên bản {bill['tariff_version_snapshot']['version']}; tính theo lượng dùng từng bậc × đơn giá. Chưa gồm thuế/phí."
                    sources.append({'type':'bill','period':bill['period'],'source':bill['source']})
            if intent in ('anomaly_detection','saving_recommendation'):
                result=AnomalyService.detect(latest['consumption'],[r['consumption'] for r in history[:-1]])
                if result.get('available'):
                    deviation=result['deviation_percent']
                    response+=f' Chênh lệch so với trung bình các kỳ trước: {deviation}%.' if deviation is not None else ' Trung bình trước bằng 0, chưa thể tính phần trăm.'
                if intent=='saving_recommendation': response+=' Gợi ý chung: kiểm tra thiết bị công suất lớn hoặc rò rỉ nước, ghi chỉ số đều đặn. Đây là khuyến nghị chung, không phải bằng chứng thiết bị cụ thể gây tăng tiêu thụ.'
        response=get_provider().explain(instructions=instructions(intent),evidence=data,grounded_response=response)
        return {'message':sanitize(response),'intent':intent.upper(),'sources':sources,'metadata':{'request_id':self.context.request_id,'provider':'deterministic','result':result,'read_only':True}}
