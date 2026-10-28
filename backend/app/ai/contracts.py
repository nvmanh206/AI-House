"""Wire contracts: values read from an image are never filled from household data."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Task = Literal['READ_INFO', 'EXPLAIN', 'COMPARE_READING', 'COMPARE_AMOUNT', 'ANALYZE_TREND', 'OTHER']


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class InvoiceFields(Contract):
    provider_name: str | None = Field(default=None, max_length=120)
    customer_code: str | None = Field(default=None, max_length=80)
    meter_code: str | None = Field(default=None, max_length=80)
    billing_period: str | None = Field(default=None, pattern=r'^\d{4}-(0[1-9]|1[0-2])$')
    previous_reading: str | None = Field(default=None, pattern=r'^\d{1,11}(\.\d{1,3})?$')
    current_reading: str | None = Field(default=None, pattern=r'^\d{1,11}(\.\d{1,3})?$')
    consumption: str | None = Field(default=None, pattern=r'^\d{1,11}(\.\d{1,3})?$')
    unit: Literal['kWh', 'm³'] | None = None
    total_amount: str | None = Field(default=None, pattern=r'^\d{1,12}(\.\d{1,2})?$')
    currency: Literal['VND'] | None = None
    due_date: str | None = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2}$')

    @model_validator(mode='after')
    def calendar_date(self):
        if self.due_date:
            date.fromisoformat(self.due_date)
        return self


class Extraction(Contract):
    document_status: Literal['READABLE', 'PARTIAL', 'UNREADABLE']
    document_type: Literal['ELECTRICITY_BILL', 'WATER_BILL', 'OTHER', 'UNKNOWN']
    requested_task: Task
    extracted_data: InvoiceFields
    uncertain_fields: list[str] = Field(max_length=12)
    missing_fields: list[str] = Field(max_length=12)

    @model_validator(mode='after')
    def uncertainty(self):
        names = set(InvoiceFields.model_fields)
        for name in self.uncertain_fields + self.missing_fields:
            if name not in names or getattr(self.extracted_data, name) is not None:
                raise ValueError('Missing/uncertain fields must be known fields with null values.')
        if set(self.uncertain_fields) & set(self.missing_fields):
            raise ValueError('A field cannot be both absent and unreadable.')
        return self


class Reply(Contract):
    requested_task: Task
    status: Literal['ANSWERED', 'OUT_OF_SCOPE', 'INSUFFICIENT_DATA', 'NEEDS_CLARIFICATION']
    message: str = Field(min_length=1, max_length=12000)
    evidence_refs: list[str] = Field(max_length=100)

    @model_validator(mode='after')
    def nonblank(self):
        if not self.message.strip():
            raise ValueError('Empty answer.')
        return self
