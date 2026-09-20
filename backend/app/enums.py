from enum import StrEnum

class DataSource(StrEnum):
    MANUAL='MANUAL'
    OCR='OCR'
    PROVIDER_API='PROVIDER_API'
    IOT='IOT'

class UtilityType(StrEnum):
    ELECTRICITY='ELECTRICITY'
    WATER='WATER'

class BillStatus(StrEnum):
    DRAFT='DRAFT'
    UNPAID='UNPAID'
    PENDING='PENDING'
    PAID='PAID'
    OVERDUE='OVERDUE'
    CANCELLED='CANCELLED'

class BillSource(StrEnum):
    MANUAL='MANUAL'
    OCR='OCR'
    PROVIDER_API='PROVIDER_API'
    SYSTEM_ESTIMATE='SYSTEM_ESTIMATE'
