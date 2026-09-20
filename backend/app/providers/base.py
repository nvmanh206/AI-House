from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(frozen=True)
class ProviderBill:
    billing_period: str
    consumption: Decimal
    amount: Decimal
    due_date: date
    source: str = 'PROVIDER_API'

class ProviderAdapter(ABC):
    @abstractmethod
    def get_provider_bill(self, customer_code: str) -> ProviderBill: ...
    def sync_provider_bill(self, customer_code: str):
        raise NotImplementedError('Chưa có workflow xác nhận và đồng bộ provider trong V1')
