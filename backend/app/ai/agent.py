from decimal import Decimal
from app.ai.context import build_context
from app.ai.router import route, normalize_message, extract_tariff_args, PROVINCES_CITIES
from app.ai.registry import SKILLS,TOOLS,instructions
from app.ai.validators import sanitize
from app.ai.provider import get_provider
from app.ai.gemini import GeminiProvider
from app.anomaly_service import AnomalyService
import re
import unicodedata
from app.security import DomainError, today
from app.ai.tools.knowledge import basic_explanation, configured_tariff_text

from app.config import settings
from app.ai.overview import build_user_overview, format_user_overview_text, deterministic_reply_with_overview

class Agent:
    def __init__(self, context, service):
        self.context, self.service = context, service

    def chat(self, message, image_base64=None, raw_ocr_text=None, conversation_id=None):
        # 1. Recheck authorization at execution, never accept IDs from chat/provider.
        member = self.service.member()
        if member.household_id != self.context.household_id or member.user_id != self.context.user_id:
            raise DomainError('FORBIDDEN', 'Ngữ cảnh truy cập không hợp lệ.', 403)

        # Canned deterministic behavior is retained only for explicit offline tests.
        if settings.app_env != 'test' or settings.llm_provider == 'gemini':
            from app.ai.multimodal import chat
            return chat(self.service, self.context, message or '', image_base64=image_base64,
                        raw_ocr_text=raw_ocr_text, conversation_id=conversation_id)

        # 2. Extract complete user & household overview data
        user_overview = build_user_overview(self.service)
        context_text = format_user_overview_text(user_overview)

        intent = route(message) if message else 'general_chat'

        # 3. Handle OCR / Bill Image Upload if provided or requested with actual invoice content
        has_invoice_content = bool(raw_ocr_text) or bool(
            message and '\n' in message and any(k in normalize_message(message) for k in ('ky:', 'chi so', 'ma kh', 'tong tien', 'san luong'))
        )
        if image_base64 or raw_ocr_text or (intent == 'ocr_bill_analysis' and has_invoice_content):
            ocr_text = raw_ocr_text or (message if not image_base64 else None)
            if not message or not message.strip():
                message = 'Phân tích ảnh/hóa đơn này và cho tôi biết các thông tin quan trọng.'
            result = TOOLS['analyze_bill_ocr'](
                self.service,
                image_base64=image_base64,
                raw_ocr_text=ocr_text,
                instruction=message
            )
            if result.get('status') in ('invalid_input', 'unsupported_document'):
                err_msg = result.get('error') or result.get('message') or 'Hiện tại tính năng ảnh của Trợ lý AI hỗ trợ phân tích hóa đơn điện/nước. Ảnh bạn gửi không được nhận diện là hóa đơn phù hợp.'
                return {'message': err_msg, 'intent': 'OCR_BILL_ANALYSIS', 'sources': [], 'metadata': {'provider': 'deterministic', 'read_only': True, 'result': result, 'request_id': self.context.request_id}}
            b = result.get('bill', {})
            ver = result.get('meter_verification', {})
            status = ver.get('status', 'UNKNOWN')
            ocr_r = ver.get('ocr_reading')
            db_r = ver.get('database_reading')
            diff = ver.get('difference')
            unit = ver.get('unit', 'm³')

            if status == 'MATCH':
                fallback_text = f"Chỉ số công tơ trên hóa đơn trùng khớp với dữ liệu hiện tại trong hệ thống: {db_r} {unit}."
            elif status == 'MISMATCH':
                fallback_text = f"Chỉ số công tơ trên hóa đơn ({ocr_r} {unit}) không trùng với dữ liệu trong hệ thống ({db_r} {unit}), chênh lệch {diff:+} {unit}. Bạn nên kiểm tra lại chỉ số công tơ hoặc hóa đơn."
            else:
                fallback_text = "Chưa đủ dữ liệu để đối chiếu đúng tài khoản, công tơ và kỳ hóa đơn. Bạn hãy kiểm tra mã khách hàng, kỳ và chỉ số đã ghi; nếu thiếu chỉ số, hãy gửi ảnh rõ hơn."

            gemini_msg = GeminiProvider().explain_ocr_analysis(result, instruction=message)
            final_msg = gemini_msg if gemini_msg else fallback_text
            provider_name = 'gemini' if gemini_msg else 'deterministic'
            return {'message': final_msg, 'intent': 'OCR_BILL_ANALYSIS', 'sources': [{'type': 'ocr_bill', 'period': b.get('period')}], 'metadata': {'provider': provider_name, 'read_only': True, 'result': result, 'request_id': self.context.request_id}}

        # 4. Handle Stable Basic Knowledge (does not require household context or web search)
        if intent == 'basic_knowledge':
            return {
                'message': basic_explanation(message),
                'intent': 'BASIC_KNOWLEDGE',
                'sources': [],
                'metadata': {
                    'provider': 'deterministic',
                    'read_only': True,
                    'request_id': self.context.request_id
                }
            }

        # 5. Handle Public Tariff inquiries (requiring external grounding search)
        if intent == 'public_tariff':
            args = extract_tariff_args(message)
            normalized = ''.join(c for c in unicodedata.normalize('NFD', message.lower().replace('đ', 'd')) if unicodedata.category(c) != 'Mn')
            if re.search(r'\bdien\b', normalized) and re.search(r'\bnuoc\b', normalized):
                place = f" tại {args['location']}" if args['location'] else ''
                return {'message': f'Mình có thể giúp tra cả điện và nước{place}. Bạn muốn xem loại nào trước? Hãy hỏi “giá điện{place}” hoặc “giá nước{place}” để mình tra riêng từng biểu giá.', 'intent': 'PUBLIC_TARIFF', 'sources': [], 'metadata': {'provider': 'deterministic', 'read_only': True, 'request_id': self.context.request_id}}
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
            answer['intent'] = 'PUBLIC_TARIFF'
            answer['metadata']['request_id'] = self.context.request_id
            return answer

        if intent == 'configured_tariff':
            response, details = configured_tariff_text(self.service, extract_tariff_args(message)['utility'])
            return {'message': response, 'intent': 'CONFIGURED_TARIFF', 'sources': [], 'metadata': {'provider': 'deterministic', 'read_only': True, 'configured_tariffs': details, 'request_id': self.context.request_id}}

        # 6. Core AI Interaction: Provide user overview data + question directly to AI
        has_gemini_key = bool(settings.gemini_api_key or settings.llm_api_key)
        if settings.llm_provider == 'gemini' and has_gemini_key:
            try:
                answer = GeminiProvider().chat_with_context(message=message, context_text=context_text, image_base64=image_base64)
                answer['intent'] = intent.upper() if intent else 'GENERAL_CHAT'
                answer['metadata']['request_id'] = self.context.request_id
                return answer
            except DomainError as e:
                if e.code not in ('GEMINI_KEY_REQUIRED', 'GEMINI_TIMEOUT', 'GEMINI_UNAVAILABLE', 'GEMINI_QUOTA', 'GEMINI_CONFIGURATION'):
                    raise

        # 7. Deterministic context-augmented fallback (for offline, missing API key, or automated tests)
        reply = deterministic_reply_with_overview(message, user_overview, self.service)
        return {
            'message': sanitize(reply['message']),
            'intent': reply.get('intent', intent.upper() if intent else 'GENERAL_CHAT'),
            'sources': reply.get('sources', []),
            'metadata': {
                'request_id': self.context.request_id,
                'provider': 'deterministic',
                'result': reply.get('result', {}),
                'read_only': True
            }
        }
