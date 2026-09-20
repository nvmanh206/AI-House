from abc import ABC,abstractmethod
class PaymentProvider(ABC):
    @abstractmethod
    def record(self,amount,reference): ...
class ManualPaymentProvider(PaymentProvider):
    def record(self,amount,reference):
        return {'status':'SUCCESS','method':'MANUAL','bank_verified':False}
