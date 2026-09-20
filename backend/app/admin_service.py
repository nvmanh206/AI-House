from app.models import User, Household, Bill, UtilityAccount, Tariff, TariffTier, AIAnalysis, AuditLog
from app.security import admin, DomainError
from app.services import public

class AdminService:
    def __init__(self,repo,auth): admin(auth); self.repo,self.auth=repo,auth
    def overview(self):
        analyses=self.repo.all(AIAnalysis)
        return {'users':len(self.repo.all(User)),'households':len(self.repo.all(Household)),'bills':len(self.repo.all(Bill)),'active_accounts':len(self.repo.all(UtilityAccount,is_active=True)),'ai_requests':len(analyses),'ai_errors':sum(a.result_json.get('status')=='error' for a in analyses),'ai_usage':[public(a) for a in analyses[-50:]]}
    def users(self): return [public(u) for u in self.repo.all(User)]
    def update_user(self,id,data):
        user=self.repo.get(User,id)
        if not user: raise DomainError('NOT_FOUND','Không tìm thấy người dùng.',404)
        if user.id==self.auth[0].id: raise DomainError('SELF_DISABLE','Không thể tự khóa tài khoản.')
        user.is_active=data.is_active
        self.repo.audit(self.auth[0].id,None,'UPDATE_USER',user)
        return public(user)
    def tariff(self,data):
        tariff=self.repo.add(Tariff,**data.model_dump(exclude={'tiers'}))
        for index,tier in enumerate(data.tiers): self.repo.add(TariffTier,tariff_id=tariff.id,order_index=index,**tier.model_dump())
        self.repo.audit(self.auth[0].id,None,'CREATE_TARIFF_VERSION',tariff)
        return public(tariff)
    def audit(self): return [public(a) for a in self.repo.all(AuditLog)[-200:][::-1]]
