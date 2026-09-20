from abc import ABC,abstractmethod
from app.config import settings
from app.security import DomainError

class LLMProvider(ABC):
    @abstractmethod
    def explain(self, *, instructions: str, evidence: dict, grounded_response: str) -> str: ...

class DeterministicProvider(LLMProvider):
    def explain(self,*,instructions,evidence,grounded_response): return grounded_response

from app.ai.gemini import GeminiProvider
PROVIDERS={'deterministic':DeterministicProvider,'gemini':GeminiProvider}
def get_provider():
    factory=PROVIDERS.get(settings.llm_provider)
    if not factory: raise DomainError('LLM_NOT_CONFIGURED','LLM provider chưa được cài đặt. Chọn deterministic để demo offline.',503)
    return factory()
