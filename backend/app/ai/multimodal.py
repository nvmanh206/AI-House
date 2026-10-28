"""Authenticated, read-only multimodal conversation pipeline."""
import base64
import binascii
from decimal import Decimal
from io import BytesIO
import logging
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select

from app.ai.contracts import Extraction
from app.config import settings
from app.ai.gemini_structured import StructuredGemini
from app.ai.gemini import GeminiProvider
from app.ai.router import route, normalize_message, extract_tariff_args
from app.ai.validators import sanitize
from app.models import AIAnalysis
from app.security import DomainError, today

MAX_IMAGE_BYTES = 10 * 1024 * 1024
log = logging.getLogger('utility')


def validate_image(value):
    encoded = value.split(',', 1)[-1] if value.startswith('data:') else value
    if len(encoded) > (MAX_IMAGE_BYTES + 2) // 3 * 4:
        raise DomainError('IMAGE_TOO_LARGE', 'Ảnh vượt quá giới hạn 10 MB.', 413)
    try:
        content = base64.b64decode(encoded, validate=True)
        if len(content) > MAX_IMAGE_BYTES:
            raise DomainError('IMAGE_TOO_LARGE', 'Ảnh vượt quá giới hạn 10 MB.', 413)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as probe:
                fmt = probe.format
                if fmt not in ('JPEG', 'PNG', 'WEBP') or getattr(probe, 'n_frames', 1) != 1:
                    raise ValueError('Unsupported or animated image')
                if probe.width * probe.height > 25_000_000:
                    raise ValueError('Too many pixels')
                probe.verify()
            with Image.open(BytesIO(content)) as decoded:
                decoded.load()
                clean = ImageOps.exif_transpose(decoded).convert('RGB')
                output = BytesIO()
                clean.save(output, format=fmt)
        if len(output.getvalue()) > MAX_IMAGE_BYTES:
            raise DomainError('IMAGE_TOO_LARGE', 'Ảnh sau xử lý vượt quá giới hạn 10 MB.', 413)
        return {'mimeType': {'JPEG':'image/jpeg', 'PNG':'image/png', 'WEBP':'image/webp'}[fmt],
                'data': base64.b64encode(output.getvalue()).decode('ascii')}
    except DomainError:
        raise
    except (ValueError, OSError, SyntaxError, binascii.Error, UnidentifiedImageError,
            Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise DomainError('INVALID_IMAGE', 'Ảnh hỏng hoặc không phải JPEG, PNG, WebP hợp lệ.', 422) from None


def overview(service):
    accounts, meters, readings, bills = service.accounts(), service.meters(), service.history(), service.bills()
    periods = sorted({r['period'] for r in readings} | {b['period'] for b in bills}, reverse=True)[:6]
    def take(row, keys):
        return {k: row.get(k) for k in keys}
    account_fields = ('id','utility_type','provider_name','customer_code','tariff_category','province','is_active')
    meter_fields = ('id','utility_account_id','utility_type','meter_code','unit','initial_reading','is_active')
    reading_fields = ('id','meter_id','period','utility_type','previous_reading','current_reading','consumption','unit','source')
    bill_fields = ('id','utility_account_id','period','utility_type','consumption','final_amount','status','due_date','source')
    def bill_context(b):
        return {**take(b,bill_fields),'tax_note':b.get('bill_detail_snapshot',{}).get('tax_note'),
                'tariff_source':b.get('tariff_version_snapshot',{}).get('source')}
    unpaid = [b for b in bills if b['status'] in ('UNPAID','OVERDUE','PENDING')]
    recent_bills = [b for b in bills if b['period'] in periods]
    recent_readings = [r for r in readings if r['period'] in periods]
    monthly = {}
    for bill in recent_bills:
        if bill['status'] == 'CANCELLED':
            continue
        key = bill['period'] + ':' + bill['utility_type']
        monthly[key] = monthly.get(key, Decimal(0)) + Decimal(str(bill['final_amount']))
    data = {'as_of': str(today()), 'periods': periods,
            'accounts': [take(a, account_fields) for a in accounts],
            'meters': [take(m, meter_fields) for m in meters],
            'readings': [take(r, reading_fields) for r in recent_readings],
            'bills': [bill_context(b) for b in recent_bills],
            'monthly_costs': {k:str(v) for k,v in monthly.items()},
            'unpaid_bills': [bill_context(b) for b in unpaid[:50]],
            'unpaid_count': len(unpaid), 'unpaid_has_more': len(unpaid) > 50,
            'total_unpaid': str(sum((Decimal(str(b['final_amount'])) for b in unpaid), Decimal(0))),
            'coverage': 'Chỉ chi tiết 6 kỳ được liệt kê; không suy diễn các kỳ khác.'}
    refs = {'overview:total_unpaid', 'overview:monthly_costs'}
    for prefix, rows in [('account', accounts), ('meter', meters), ('reading', recent_readings), ('bill', recent_bills + unpaid[:50])]:
        refs.update(f"{prefix}:{r['id']}" for r in rows)
    return data, refs


def verify_extraction(service, extraction):
    fields = extraction.extracted_data
    result = {'consistency': [], 'reading': {'status':'UNKNOWN'}, 'amount': {'status':'UNKNOWN'}}
    utility = {'ELECTRICITY_BILL':'ELECTRICITY', 'WATER_BILL':'WATER'}.get(extraction.document_type)
    if not utility:
        result['reading']['reason'] = result['amount']['reason'] = 'DOCUMENT_UNRESOLVED'
        return result
    if fields.unit and fields.unit != ('kWh' if utility == 'ELECTRICITY' else 'm³'):
        result['consistency'].append('UNIT_MISMATCH')
    if fields.current_reading is not None and fields.previous_reading is not None:
        consumption = Decimal(fields.current_reading) - Decimal(fields.previous_reading)
        if consumption < 0:
            result['consistency'].append('READING_DECREASE')
        elif fields.consumption is not None and Decimal(fields.consumption) != consumption:
            result['consistency'].append('CONSUMPTION_MISMATCH')
        else:
            result['calculated_consumption'] = str(consumption)
    accounts = [a for a in service.accounts() if a['utility_type'] == utility]
    if fields.customer_code:
        accounts = [a for a in accounts if a.get('customer_code') == fields.customer_code]
    meters = [m for m in service.meters() if m['utility_account_id'] in {a['id'] for a in accounts}]
    if fields.meter_code:
        meters = [m for m in meters if m.get('meter_code') == fields.meter_code]
        accounts = [a for a in accounts if a['id'] in {m['utility_account_id'] for m in meters}]
    if len(accounts) != 1 or not fields.billing_period:
        reason = 'ACCOUNT_NOT_FOUND' if not accounts else ('ACCOUNT_AMBIGUOUS' if len(accounts) != 1 else 'PERIOD_MISSING')
        result['reading']['reason'] = result['amount']['reason'] = reason
        return result
    account = accounts[0]
    meter_ids = {m['id'] for m in meters}
    candidates = [r for r in service.history() if r['meter_id'] in meter_ids and r['period'] == fields.billing_period]
    if len(candidates) == 1 and fields.current_reading is not None and not result['consistency']:
        observed = Decimal(str(candidates[0]['current_reading']))
        delta = Decimal(fields.current_reading) - observed
        result['reading'] = {'status':'MATCH' if delta == 0 else 'MISMATCH', 'database_reading':str(observed),
            'difference':str(delta), 'period':fields.billing_period, 'meter_id':candidates[0]['meter_id'], 'reading_id':candidates[0]['id']}
    else:
        result['reading']['reason'] = 'INCONSISTENT_OR_MISSING_READING' if len(candidates) <= 1 else 'READING_AMBIGUOUS'
    candidates = [b for b in service.bills() if b['utility_account_id'] == account['id']
                  and b['period'] == fields.billing_period and b['status'] != 'CANCELLED']
    if len(candidates) == 1 and fields.total_amount is not None and not (fields.meter_code and not meters):
        bill = candidates[0]
        amount = Decimal(str(bill['final_amount']))
        delta = Decimal(fields.total_amount) - amount
        result['amount'] = {'status':'MATCH' if delta == 0 else 'MISMATCH', 'database_amount':str(amount),
            'difference':str(delta), 'source':bill['source'], 'bill_id':bill['id'], 'period':fields.billing_period}
    else:
        result['amount']['reason'] = 'BILL_OR_AMOUNT_MISSING_OR_AMBIGUOUS'
    return result


# Public search failures may produce empty evidence for Gemini, never a local answer.
RETRIEVAL_ERRORS = {'GEMINI_QUOTA','GEMINI_UNAVAILABLE','GEMINI_TIMEOUT','GEMINI_KEY_REQUIRED','GEMINI_INVALID_RESPONSE',
              'GEMINI_MODEL_INVALID','GEMINI_INVALID_EVIDENCE','GEMINI_UNSUPPORTED_CONCLUSION'}
GEMINI_HISTORY_TURNS = 8


def conversation_for(service, context, conversation_id, lock=False):
    query = select(AIAnalysis).where(AIAnalysis.id == str(conversation_id), AIAnalysis.user_id == context.user_id,
        AIAnalysis.household_id == context.household_id, AIAnalysis.analysis_type == 'CHAT_CONTEXT')
    conversation = service.repo.db.scalar(query.with_for_update() if lock else query)
    if not conversation:
        raise DomainError('CONVERSATION_NOT_FOUND', 'Không tìm thấy cuộc trò chuyện trong hộ đang chọn.', 404)
    return conversation


def check_reply(reply, refs, knowledge, public_tariff, extraction, verification, has_new_input):
    if not set(reply.evidence_refs).issubset(refs):
        raise DomainError('GEMINI_INVALID_EVIDENCE', 'Gemini viện dẫn dữ liệu không thuộc ngữ cảnh hiện tại.', 502)
    if knowledge and reply.status == 'ANSWERED':
        if not knowledge['documents'] or not any(ref.startswith('knowledge:') for ref in reply.evidence_refs):
            raise DomainError('GEMINI_UNSUPPORTED_CONCLUSION','Câu trả lời kiến thức công khai chưa có nguồn hợp lệ.',502)
    if public_tariff is not None and reply.status == 'ANSWERED':
        if not public_tariff['grounded'] or not any(ref.startswith('public_tariff:') for ref in reply.evidence_refs):
            raise DomainError('GEMINI_UNSUPPORTED_CONCLUSION', 'Chưa có nguồn xác minh giá công khai cho câu trả lời này.', 502)
    if extraction and reply.status == 'ANSWERED':
        task = extraction.requested_task if has_new_input else reply.requested_task
        comparison = 'reading' if task == 'COMPARE_READING' else ('amount' if task == 'COMPARE_AMOUNT' else None)
        if comparison and (verification[comparison]['status'] == 'UNKNOWN' or 'verification:' + comparison not in reply.evidence_refs):
            raise DomainError('GEMINI_UNSUPPORTED_CONCLUSION', 'Gemini chưa có căn cứ đối chiếu hợp lệ. Vui lòng làm rõ tài khoản hoặc kỳ.', 502)


def chat(service, context, message, *, image_base64=None, raw_ocr_text=None, conversation_id=None):
    message = sanitize(message)
    image = validate_image(image_base64) if image_base64 else None
    new_input = bool(image or raw_ocr_text)
    # Read without a row lock: the lock is taken only when saving, not while Gemini is answering.
    saved = conversation_for(service, context, conversation_id).result_json if conversation_id else {}
    history = saved.get('history', [])[-20:]
    prior = saved.get('extraction')
    provider = StructuredGemini()
    extraction = Extraction.model_validate(prior) if prior and not new_input else None
    if new_input:
        extraction = provider.extract(message=message, image=image, raw_text=raw_ocr_text)
    verification = verify_extraction(service, extraction) if extraction else None
    household_overview, refs = overview(service)
    public_tariff = None
    web_sources = []
    knowledge = None
    if settings.knowledge_rag_enabled:
        from app.knowledge.service import public_query, retrieve
        query = public_query(message, history)
        if query.needs_public_knowledge:
            try:
                knowledge = retrieve(query)
            except DomainError as exc:
                knowledge = {'mode':'UNAVAILABLE','status':'EMPTY','warnings':[exc.code],
                             'current_price':query.current_price,'documents':[]}
            for index, document in enumerate(knowledge['documents'],1):
                document['index'] = index
                refs.add(document['ref'])
                web_sources.append({'type':'knowledge','index':index,'ref':document['ref'],
                    'url':document['url'],'title':document['title'],'version':document['version_id'],
                    'section':document['position'],'effective_from':document['metadata'].get('effective_from'),
                    'checked_at':str(document['checked_at'])})
            household_overview['public_knowledge'] = knowledge
    # Routing chooses a data source, never a canned answer. Search gets only
    # canonical public arguments, not the household overview or chat history.
    if not settings.knowledge_rag_enabled and not new_input and route(message) == 'public_tariff':
        args = extract_tariff_args(message)
        normalized = normalize_message(message)
        both_utilities = 'dien' in normalized and 'nuoc' in normalized
        if not both_utilities and (args['utility'] != 'WATER' or args['location']):
            try:
                lookup = GeminiProvider().search_tariff(utility=args['utility'],day=args['target_date'],
                    location=args['location'],customer_group=args['customer_group'],query_type=args['query_type'])
            except DomainError as exc:
                if exc.code not in RETRIEVAL_ERRORS:
                    raise
                lookup = {'sources':[],'metadata':{'grounded':False,'error_code':exc.code}}
            grounded = bool(lookup.get('metadata',{}).get('grounded') and lookup.get('sources'))
            web_sources = lookup.get('sources',[]) if grounded else []
            public_tariff = {'grounded':grounded,'query':args,'sources':web_sources,
                'retrieved_at':lookup.get('metadata',{}).get('retrieved_at'),
                'error_code':lookup.get('metadata',{}).get('error_code')}
            if grounded:
                public_tariff['findings'] = lookup['message']
                refs.update('public_tariff:' + str(s['index']) for s in web_sources)
            household_overview['public_tariff'] = public_tariff
    for turn in history:
        historical = turn.get('extraction')
        if historical and turn.get('request_id'):
            refs.update('image:' + turn['request_id'] + ':' + name
                        for name,value in historical['extracted_data'].items() if value is not None)
    if extraction:
        refs.update('image:' + name for name,value in extraction.extracted_data.model_dump().items() if value is not None)
        if verification['consistency']:
            refs.add('verification:consistency')
        for kind in ('reading','amount'):
            if verification[kind]['status'] in ('MATCH','MISMATCH'):
                refs.add('verification:' + kind)
    reply = provider.respond(message=message, overview=household_overview, history=history[-GEMINI_HISTORY_TURNS:],
        extraction=extraction.model_dump(mode='json') if extraction else None,
        verification=verification, evidence_refs=sorted(refs))
    check_reply(reply, refs, knowledge, public_tariff, extraction, verification, new_input)
    text, status, evidence_refs = reply.message, reply.status, reply.evidence_refs
    sources = [s for s in web_sources if s.get('ref') in evidence_refs] if knowledge else web_sources
    extraction_state = extraction.model_dump(mode='json') if extraction else None
    turns = [{'role':'user','message':message, 'has_image':bool(image), 'request_id':context.request_id,
              'extraction':extraction_state if new_input else None}, {'role':'assistant','message':text}]
    if conversation_id:
        # Append to the latest saved history so a concurrent turn is not overwritten.
        conversation = conversation_for(service, context, conversation_id, lock=True)
        latest = conversation.result_json or {}
        conversation.result_json = {'history':[*latest.get('history', []), *turns][-20:], 'extraction':extraction_state}
    else:
        conversation = service.repo.add(AIAnalysis, household_id=context.household_id, user_id=context.user_id,
            analysis_type='CHAT_CONTEXT', model_name='gemini', result_json={'history':turns, 'extraction':extraction_state})
    reply_fields = reply.model_dump()
    result = {**reply_fields, 'extracted_data':extraction.extracted_data.model_dump() if extraction else None,
              'extraction':extraction_state, 'verification':verification}
    warnings = knowledge['warnings'] if knowledge else []
    return {'message':text, 'status':status, 'intent':'MULTIMODAL_CHAT' if extraction else 'GEMINI_CHAT',
            'sources':sources + [{'type':'evidence','ref':ref} for ref in evidence_refs],
            'metadata': {'provider':'gemini', 'degraded':False,
                         'read_only':True, 'request_id':context.request_id,
                         'public_tariff':public_tariff,
                         'retrieval':{k:v for k,v in knowledge.items() if k != 'documents'} if knowledge else None,
                         'sources':sources,
                         'warnings':warnings,
                         'conversation_id':conversation.id, 'result':result}}
