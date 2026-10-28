import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

BillType = Literal['ELECTRICITY', 'WATER', 'UNKNOWN']

class OCRBillData(BaseModel):
    bill_type: BillType = 'UNKNOWN'
    customer_code: str | None = None
    billing_period: str | None = None  # Format: YYYY-MM
    previous_reading: float | None = None
    current_reading: float | None = None
    consumption: float | None = None
    amount: float | None = None
    due_date: date | None = None
    invoice_code: str | None = None
    meter_code: str | None = None
    confidence: float | None = Field(default=0.95, ge=0.0, le=1.0)
    raw_text: str = ''

def normalize_text(text: str) -> str:
    """Strip accents and lower case for keyword matching."""
    text_clean = text.lower().replace('đ', 'd')
    return ''.join(c for c in unicodedata.normalize('NFD', text_clean) if unicodedata.category(c) != 'Mn')

def mask_customer_code(code: str | None) -> str | None:
    """Mask customer code for privacy (e.g., PD12003123 -> PD****3123)."""
    if not code or len(code) <= 5:
        return code
    prefix = code[:2]
    suffix = code[-4:]
    return f"{prefix}{'*' * (len(code) - 6)}{suffix}"

def parse_number(num_str: str) -> float | None:
    """Convert Vietnamese number string (e.g. 512.340, 1.250,50) to float."""
    if not num_str:
        return None
    cleaned = num_str.strip().replace(' ', '')
    if ',' in cleaned and '.' in cleaned:
        cleaned = cleaned.replace('.', '').replace(',', '.')
    elif '.' in cleaned and len(cleaned.split('.')[-1]) in (3, 6):
        cleaned = cleaned.replace('.', '')
    elif ',' in cleaned:
        cleaned = cleaned.replace(',', '.')
    try:
        val = float(cleaned)
        return val if val >= 0 else None
    except ValueError:
        return None

def parse_ocr_text(raw_text: str) -> OCRBillData:
    """Deterministic parser for Vietnamese utility bills."""
    if not raw_text or not raw_text.strip():
        return OCRBillData(bill_type='UNKNOWN', raw_text=raw_text)

    normalized = normalize_text(raw_text)

    # Reject explicitly non-bill text
    if any(w in normalized for w in ('khong phai hoa don', 'anh chup phong cảnh', 'van ban ghi chu')):
        return OCRBillData(bill_type='UNKNOWN', raw_text=raw_text)

    # 1. Detect Bill Type
    bill_type: BillType = 'UNKNOWN'
    if re.search(r'\b(evn|kwh|cong to dien|tien dien|dien luc)\b', normalized):
        bill_type = 'ELECTRICITY'
    elif re.search(r'\b(cap nuoc|m3|m³|dong ho nuoc|tien nuoc)\b', normalized):
        bill_type = 'WATER'
    elif re.search(r'\bdien\b', normalized) and any(w in normalized for w in ('san luong', 'chi so', 'ma kh', 'cuoi ky', 'dau ky')):
        bill_type = 'ELECTRICITY'
    elif re.search(r'\bnuoc\b', normalized) and any(w in normalized for w in ('khoi', 'chi so', 'ma kh', 'cuoi ky', 'dau ky')):
        bill_type = 'WATER'

    # 2. Extract Customer Code
    customer_code = None
    cc_match = re.search(r'(?:ma\s*kh|mkh|ma\s*khach\s*hang|khach\s*hang)[:\s]*([a-zA-Z0-9]{4,20})', normalized)
    if cc_match:
        customer_code = cc_match.group(1).upper()
    else:
        standalone_match = re.search(r'\b(P[D|E|A|B|C|H|L|M|N|K][A-Za-z0-9]{6,14}|N[0-9]{6,12})\b', raw_text)
        if standalone_match:
            customer_code = standalone_match.group(1).upper()

    # 3. Extract Billing Period (YYYY-MM)
    billing_period = None
    period_match = re.search(r'(?:ky|thang|thoi\s*gian)[:\s]*(\d{1,2})[\/\-](\d{4})', normalized)
    if period_match:
        m, y = int(period_match.group(1)), int(period_match.group(2))
        billing_period = f"{y:04d}-{m:02d}"
    else:
        ym_match = re.search(r'\b(\d{4})[\/\-](\d{1,2})\b', normalized)
        if ym_match:
            y, m = int(ym_match.group(1)), int(ym_match.group(2))
            billing_period = f"{y:04d}-{m:02d}"

    # 4. Extract Meter Readings
    previous_reading = None
    current_reading = None

    prev_match = re.search(r'(?:chi\s*so\s*cu|cs\s*cu|dau\s*ky)[:\s]*([0-9\.\,]+)', normalized)
    if prev_match:
        previous_reading = parse_number(prev_match.group(1))

    curr_match = re.search(r'(?:chi\s*so\s*moi|cs\s*moi|cuoi\s*ky)[:\s]*([0-9\.\,]+)', normalized)
    if curr_match:
        current_reading = parse_number(curr_match.group(1))

    if previous_reading is None or current_reading is None:
        range_match = re.search(r'([0-9\.\,]+)\s*(?:->|den|-)\s*([0-9\.\,]+)', normalized)
        if range_match:
            r1 = parse_number(range_match.group(1))
            r2 = parse_number(range_match.group(2))
            if r1 is not None and r2 is not None and r2 >= r1:
                previous_reading, current_reading = r1, r2

    # 5. Extract Consumption
    consumption = None
    cons_match = re.search(r'(?:san\s*luong|tieu\s*thu|luong\s*dung|dien\s*nang|khoi)[:\s]*([0-9\.\,]+)', normalized)
    if cons_match:
        consumption = parse_number(cons_match.group(1))
    elif previous_reading is not None and current_reading is not None:
        consumption = round(current_reading - previous_reading, 3)

    # 6. Extract Amount
    amount = None
    amt_match = re.search(r'(?:tong\s*cong|tong\s*tien|thanh\s*tien|so\s*tien|phai\s*thanhti|tong\s*thanh\s*toan)[:\s]*([0-9\.\,]+)', normalized)
    if amt_match:
        amount = parse_number(amt_match.group(1))
    else:
        curr_amt_match = re.search(r'([0-9\.\,]{4,12})\s*(?:vnd|vnd|dong|d|d)\b', normalized)
        if curr_amt_match:
            amount = parse_number(curr_amt_match.group(1))

    # 7. Extract Due Date
    due_date = None
    due_match = re.search(r'(?:han\s*thanh\s*toan|han\s*tra|han\s*dong)[:\s]*(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', normalized)
    if due_match:
        d, m, y = int(due_match.group(1)), int(due_match.group(2)), int(due_match.group(3))
        try:
            due_date = date(y, m, d)
        except ValueError:
            pass

    invoice_code = None
    inv_match = re.search(r'(?:so\s*hoa\s*don|shd|ma\s*hd)[:\s]*([a-zA-Z0-9]+)', normalized)
    if inv_match:
        invoice_code = inv_match.group(1).upper()

    meter_code = None
    mc_match = re.search(r'(?:so\s*cong\s*to|ma\s*cong\s*to|so\s*dong\s*ho)[:\s]*([a-zA-Z0-9]+)', normalized)
    if mc_match:
        meter_code = mc_match.group(1).upper()

    return OCRBillData(
        bill_type=bill_type,
        customer_code=customer_code,
        billing_period=billing_period,
        previous_reading=previous_reading,
        current_reading=current_reading,
        consumption=consumption,
        amount=amount,
        due_date=due_date,
        invoice_code=invoice_code,
        meter_code=meter_code,
        confidence=0.95,
        raw_text=raw_text
    )
