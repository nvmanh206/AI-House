from abc import ABC,abstractmethod
from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class OCRResult:
    value: Decimal | None
    confidence: float
    raw_text: str
class OCRService(ABC):
    @abstractmethod
    def extract(self,image: bytes) -> OCRResult:
        """Extract only; caller must validate and request user confirmation before saving."""
