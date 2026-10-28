import base64
import logging
from decimal import Decimal
from app.security import DomainError
from app.ai.tools.ocr_parser import parse_ocr_text, mask_customer_code, OCRBillData
from app.ai.gemini import GeminiProvider

logger = logging.getLogger('utility')

def analyze_bill_ocr(
    service,
    image_base64: str | None = None,
    raw_ocr_text: str | None = None,
    instruction: str | None = None,
    *args,
    **kwargs
) -> dict:
    """
    EXEC Tool for AI Agent: Analyze OCR Bill Image or Text.
    Strictly isolated to authenticated member's household context.
    Never accepts household_id or user_id as arguments.
    """
    # 1. Security Authorization Recheck (Context Locking)
    member = service.member()
    if not member or not member.household_id:
        raise DomainError('UNAUTHORIZED', 'Không xác định được ngữ cảnh hộ gia đình hợp lệ.', 401)
    
    # 2. Input Handling & Base64 Image Validation
    ocr_text = raw_ocr_text or ''
    valid_image_b64 = None
    if image_base64:
        clean_b64 = image_base64.split(',', 1)[-1] if ',' in image_base64 else image_base64
        try:
            image_bytes = base64.b64decode(clean_b64, validate=True)
            if len(image_bytes) > 10 * 1024 * 1024:
                return {'status': 'invalid_input', 'error': 'Dung lượng ảnh vượt quá giới hạn 10MB.'}
            valid_image_b64 = image_base64
        except Exception as e:
            logger.warning("Failed to process base64 image: %s", type(e).__name__)
            return {'status': 'invalid_input', 'error': 'Định dạng ảnh Base64 không hợp lệ.'}

    if not ocr_text.strip() and not valid_image_b64:
        return {'status': 'invalid_input', 'error': 'Cần tải lên ảnh hóa đơn hoặc cung cấp văn bản OCR.'}

    # 3. OCR Parsing & Gemini Vision Multimodal Extraction Pipeline
    # Prepare household context for Gemini API
    household_context = {}
    try:
        household_context = {
            'accounts': service.accounts(),
            'meters': service.meters(),
            'latest_readings': service.history()[-3:] if hasattr(service, 'history') else []
        }
    except Exception as e:
        logger.debug("Failed to build household_context for Gemini: %s", type(e).__name__)

    # Call Gemini API to extract structured JSON from Base64 Image + RAW OCR TEXT + instruction + household_context
    gemini_json = GeminiProvider().analyze_ocr_with_gemini(
        raw_ocr_text=ocr_text,
        image_base64=valid_image_b64,
        user_instruction=instruction,
        household_context=household_context
    )

    # Fallback to local regex parser if OCR raw text is provided and Gemini is unavailable
    regex_data: OCRBillData = parse_ocr_text(ocr_text) if ocr_text.strip() else OCRBillData()

    # Prefer Gemini API structured JSON fields if valid, fallback to regex_data
    bill_type = (gemini_json.get('bill_type') if gemini_json and gemini_json.get('bill_type') in ('ELECTRICITY', 'WATER') else regex_data.bill_type)
    customer_code = (gemini_json.get('customer_code') if gemini_json and gemini_json.get('customer_code') else regex_data.customer_code)
    billing_period = (gemini_json.get('billing_period') if gemini_json and gemini_json.get('billing_period') else regex_data.billing_period)
    previous_reading = (gemini_json.get('previous_reading') if gemini_json and gemini_json.get('previous_reading') is not None else regex_data.previous_reading)
    current_reading = (gemini_json.get('current_reading') if gemini_json and gemini_json.get('current_reading') is not None else regex_data.current_reading)
    consumption = (gemini_json.get('consumption') if gemini_json and gemini_json.get('consumption') is not None else regex_data.consumption)
    amount = (gemini_json.get('amount') if gemini_json and gemini_json.get('amount') is not None else regex_data.amount)

    if bill_type == 'UNKNOWN':
        # Smart utility type inference from user instruction or household account context
        text_lower = (instruction or '').lower() + ' ' + ocr_text.lower()
        if 'nước' in text_lower or 'cap nuoc' in text_lower or 'sawaco' in text_lower:
            bill_type = 'WATER'
        elif 'điện' in text_lower or 'evn' in text_lower or 'kwh' in text_lower:
            bill_type = 'ELECTRICITY'
        elif valid_image_b64:
            # For image uploads, infer from household's active accounts
            accounts = household_context.get('accounts', [])
            if accounts and isinstance(accounts[0], dict):
                bill_type = accounts[0].get('utility_type', 'ELECTRICITY')
            else:
                bill_type = 'ELECTRICITY'

    if bill_type == 'UNKNOWN' and not amount and not consumption and current_reading is None and not valid_image_b64:
        return {
            'status': 'unsupported_document',
            'message': 'Không nhận diện được đây là hóa đơn điện hoặc nước. Vui lòng tải ảnh hóa đơn rõ nét hơn.'
        }

    utility = bill_type if bill_type in ('ELECTRICITY', 'WATER') else 'ELECTRICITY'
    unit = 'kWh' if utility == 'ELECTRICITY' else 'm³'

    # Create normalized ocr_data object
    ocr_data = OCRBillData(
        bill_type=bill_type,
        customer_code=customer_code,
        billing_period=billing_period,
        previous_reading=previous_reading,
        current_reading=current_reading,
        consumption=consumption,
        amount=amount,
        due_date=regex_data.due_date,
        invoice_code=regex_data.invoice_code,
        meter_code=regex_data.meter_code
    )

    # 4. Load Authenticated Household Meter Reading from DB
    # Context Isolation: Strictly scoped to authenticated_household_id via service
    db_meter_reading: float | None = None
    accounts, meters, matching_history = [], [], []
    history = []
    try:
        accounts = [a for a in service.accounts() if a.get('utility_type') == utility]
        if customer_code:
            accounts = [a for a in accounts if a.get('customer_code') == customer_code]
        account_ids = {a['id'] for a in accounts}
        meters = [m for m in service.meters() if m.get('utility_account_id') in account_ids]
        if ocr_data.meter_code:
            meters = [m for m in meters if m.get('meter_code') == ocr_data.meter_code]
        meter_ids = {m['id'] for m in meters}
        history = service.history()
        matching_history = [r for r in history if r.get('utility_type') == utility
                            and r.get('meter_id') in meter_ids and r.get('period') == billing_period]
        # Missing identifiers or ambiguous observations cannot prove a match.
        if len(accounts) == 1 and billing_period and len(matching_history) == 1:
            db_meter_reading = float(matching_history[0]['current_reading'])
    except Exception as e:
        logger.warning("Failed to query DB meter reading: %s", type(e).__name__)

    # Compare recorded observations only after resolving account and period.
    ocr_reading = ocr_data.current_reading
    
    meter_status: str = "UNKNOWN"
    difference: float | None = None

    if ocr_reading is not None and db_meter_reading is not None:
        calc_diff = Decimal(str(ocr_reading)) - Decimal(str(db_meter_reading))
        if abs(calc_diff) == 0:
            meter_status = "MATCH"
            difference = 0.0
        else:
            meter_status = "MISMATCH"
            difference = float(calc_diff)
    else:
        meter_status = "UNKNOWN"
        difference = None

    meter_verification = {
        'status': meter_status,
        'ocr_reading': ocr_reading,
        'database_reading': db_meter_reading,
        'difference': difference,
        'unit': unit
    }

    # Warnings specifically for meter verification
    warnings = []
    if meter_status == 'MISMATCH':
        warnings.append({
            'code': 'METER_READING_MISMATCH',
            'severity': 'high',
            'message': f"Chỉ số công tơ trên hóa đơn ({ocr_reading} {unit}) không trùng khớp với dữ liệu hệ thống ({db_meter_reading} {unit}). Sai lệch: {difference:+} {unit}."
        })
    elif meter_status == 'UNKNOWN':
        warnings.append({
            'code': 'METER_READING_UNKNOWN',
            'severity': 'info',
            'message': 'Chưa đủ dữ liệu để đối chiếu đúng tài khoản, công tơ và kỳ hóa đơn. Vui lòng kiểm tra mã khách hàng, kỳ và chỉ số đã ghi.'
        })

    # 6. Optional Display Data (Consumption, Comparison, Amount, Forecast)
    resolved_account = accounts[0] if len(accounts) == 1 and billing_period else None
    resolved_meter_id = None
    if resolved_account:
        if len(matching_history) == 1:
            resolved_meter_id = matching_history[0]['meter_id']
        elif len(meters) == 1:
            resolved_meter_id = meters[0]['id']
    consumption_history = sorted(
        [r for r in history if resolved_meter_id and r.get('meter_id') == resolved_meter_id
         and r.get('utility_type') == utility and r.get('period', '') < billing_period],
        key=lambda r: r['period'],
    )
    bill_history = [b for b in service.bills() if resolved_account
                    and b.get('utility_account_id') == resolved_account['id']
                    and b.get('utility_type') == utility and b.get('period') == billing_period
                    and b.get('status') != 'CANCELLED']

    current_cons = ocr_data.consumption
    if current_cons is None and ocr_data.previous_reading is not None and ocr_data.current_reading is not None:
        current_cons = round(ocr_data.current_reading - ocr_data.previous_reading, 3)

    comparison = {
        'previous_3_period_average': None,
        'current_consumption': current_cons,
        'difference_percent': None,
        'trend': 'unknown'
    }

    if current_cons is not None and len(consumption_history) >= 1:
        past_3 = [float(r['consumption']) for r in consumption_history[-3:]]
        avg_past = sum(past_3) / len(past_3)
        comparison['previous_3_period_average'] = round(avg_past, 3)

        if avg_past > 0:
            diff_pct = round(((current_cons - avg_past) / avg_past) * 100, 1)
            comparison['difference_percent'] = diff_pct
            if diff_pct > 5:
                comparison['trend'] = 'increasing'
            elif diff_pct < -5:
                comparison['trend'] = 'decreasing'
            else:
                comparison['trend'] = 'stable'

    # 7. Amount Analysis (Optional Display Info)
    amount_analysis = {
        'ocr_amount': ocr_data.amount,
        'expected_amount': None,
        'difference': None,
        'difference_percent': None
    }

    if len(bill_history) == 1 and bill_history[0].get('final_amount') is not None:
        recorded_bill = bill_history[0]
        recorded_amount = Decimal(str(recorded_bill['final_amount']))
        amount_analysis['expected_amount'] = float(recorded_amount)
        amount_analysis['source'] = recorded_bill.get('source')
        amount_analysis['bill_id'] = recorded_bill['id']
        if ocr_data.amount is not None:
            delta = Decimal(str(ocr_data.amount)) - recorded_amount
            amount_analysis['difference'] = float(delta)
            if recorded_amount > 0:
                amount_analysis['difference_percent'] = round(float(delta / recorded_amount * 100), 1)

    # 8. Forecast Next Period (Optional Display Info)
    forecast_data = {
        'next_period_consumption': None,
        'estimated_amount': None,
        'trend': comparison['trend'],
        'confidence': 'low',
        'available': False,
        'reason': 'Chưa có dự báo được tính theo đúng tài khoản và kỳ hóa đơn OCR.'
    }

    # The general forecast is anchored to today, not the OCR billing period.

    # 9. Return Structured Result
    return {
        'status': 'success',
        'bill': {
            'type': utility.lower(),
            'period': ocr_data.billing_period,
            'customer_code': mask_customer_code(ocr_data.customer_code),
            'previous_reading': ocr_data.previous_reading,
            'current_reading': ocr_data.current_reading,
            'consumption': current_cons,
            'amount': ocr_data.amount,
            'due_date': str(ocr_data.due_date) if ocr_data.due_date else None,
            'invoice_code': ocr_data.invoice_code,
            'meter_code': ocr_data.meter_code
        },
        'meter_verification': meter_verification,
        'comparison': comparison,
        'amount_analysis': amount_analysis,
        'warnings': warnings,
        'forecast': forecast_data
    }
