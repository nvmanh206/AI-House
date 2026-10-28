from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

Utility = Literal['ELECTRICITY','WATER']
class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, validate_default=True)
class Register(Input):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
class Profile(Input):
    full_name: str = Field(min_length=2, max_length=120)
class Password(Input):
    old_password: str = Field(max_length=128)
    new_password: str = Field(min_length=10, max_length=128)
class HouseholdInput(Input):
    name: str = Field(min_length=2, max_length=120)
    address: str = Field(default='', max_length=500)
    province: str = Field(default='', max_length=120)
    district: str = Field(default='', max_length=120)
    ward: str = Field(default='', max_length=120)
    member_count: int = Field(default=1, ge=1, le=100)
class AccountInput(Input):
    utility_type: Utility
    provider_name: str = Field(min_length=2, max_length=120)
    provider_code: str = Field(default='', max_length=80)
    customer_code: str = Field(default='', max_length=80)
    tariff_category: str = Field(default='RESIDENTIAL_1PHASE', max_length=40)
    province: str = Field(default='', max_length=120)
    billing_day: int = Field(default=25, ge=1, le=31)
    due_day: int = Field(default=28, ge=1, le=31)
    reminder_days_before: int = Field(default=3, ge=0, le=14)
class SetupAccount(AccountInput):
    initial_reading: Decimal = Field(default=0, ge=0, max_digits=14, decimal_places=3)
class Onboarding(HouseholdInput):
    accounts: list[SetupAccount] = Field(min_length=1, max_length=2)
    @model_validator(mode='after')
    def utilities(self):
        kinds = [a.utility_type for a in self.accounts]
        if 'ELECTRICITY' not in kinds or len(kinds) != len(set(kinds)):
            raise ValueError('Cần tài khoản điện; không lặp loại tiện ích')
        return self
class MemberInput(Input):
    email: EmailStr
    permissions: list[Literal['write','pay']] = Field(default_factory=list)
class MeterInput(Input):
    utility_account_id: str
    name: str = Field(min_length=2, max_length=120)
    meter_code: str = Field(default='', max_length=80)
    initial_reading: Decimal = Field(default=0, ge=0, max_digits=14, decimal_places=3)
class MeterUpdate(Input):
    name: str = Field(min_length=2, max_length=120)
    meter_code: str = Field(default='', max_length=80)
    is_active: bool = True
class ReadingInput(Input):
    meter_id: str
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    current_reading: Decimal = Field(ge=0, max_digits=14, decimal_places=3)
    reading_date: date
    @model_validator(mode='after')
    def period_date(self):
        if (self.reading_date.year,self.reading_date.month) != (self.year,self.month):
            raise ValueError('Ngày ghi phải thuộc kỳ hóa đơn')
        return self
class ReadingUpdate(Input):
    current_reading: Decimal = Field(ge=0, max_digits=14, decimal_places=3)
    reading_date: date | None = None
class TierInput(Input):
    from_value: Decimal = Field(ge=0, max_digits=14, decimal_places=3)
    to_value: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=3)
    unit_price: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
class TariffInput(Input):
    utility_type: Utility
    provider_name: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=120)
    version: str = Field(min_length=1, max_length=40)
    tariff_category: str = Field(default='RESIDENTIAL_1PHASE', max_length=40)
    province: str | None = Field(default=None, max_length=120)
    rate_type: str = Field(default='TIERED', max_length=20)
    effective_from: date
    effective_to: date | None = None
    tiers: list[TierInput] = Field(min_length=1, max_length=20)
    @model_validator(mode='after')
    def continuous(self):
        start = Decimal(0)
        for i,t in enumerate(self.tiers):
            if t.from_value != start or (t.to_value is not None and t.to_value <= t.from_value):
                raise ValueError('Các bậc giá phải liên tục, bắt đầu từ 0')
            if (t.to_value is None) != (i == len(self.tiers)-1):
                raise ValueError('Bậc cuối phải không có giới hạn trên')
            start = t.to_value
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValueError('Khoảng hiệu lực không hợp lệ')
        return self
class PaymentInput(Input):
    bill_id: str
    reference: str = Field(default='', max_length=120)
class ChatInput(Input):
    conversation_id: UUID | None = None
    message: str | None = Field(default='', max_length=2000)
    image_base64: str | None = Field(default=None, max_length=15000000)
    raw_ocr_text: str | None = Field(default=None, max_length=10000)
    @model_validator(mode='after')
    def check_input(self):
        has_msg = bool(self.message and self.message.strip())
        has_img = bool(self.image_base64 and self.image_base64.strip())
        has_ocr = bool(self.raw_ocr_text and self.raw_ocr_text.strip())
        if not (has_msg or has_img or has_ocr):
            raise ValueError('Cần cung cấp tin nhắn, ảnh hóa đơn hoặc văn bản OCR')
        return self
class UserUpdate(Input):
    is_active: bool
