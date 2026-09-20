from app.providers.base import ProviderAdapter
class EvnAdapter(ProviderAdapter):
    def get_provider_bill(self,customer_code):
        raise NotImplementedError('Provider chưa tích hợp; không có endpoint giả định.')
