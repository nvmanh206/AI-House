from app.providers.base import ProviderAdapter
class MockProviderAdapter(ProviderAdapter):
    """Explicit fixture injection for tests, never registered as a real provider."""
    def __init__(self,fixture): self.fixture=fixture
    def get_provider_bill(self,customer_code): return self.fixture
