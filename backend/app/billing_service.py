from decimal import Decimal, ROUND_HALF_UP
from app.security import DomainError, day_in_month
from app.models import Tariff, TariffTier, Household, Bill

def calculate_tiers(consumption, tiers):
    consumption = Decimal(consumption)
    if consumption < 0: raise DomainError('INVALID_CONSUMPTION','Tiêu thụ không được âm.')
    total, lines = Decimal(0), []
    for tier in tiers:
        lower = Decimal(tier.from_value)
        upper = Decimal(tier.to_value) if tier.to_value is not None else consumption
        quantity = max(Decimal(0),min(consumption,upper)-lower)
        amount = quantity * Decimal(tier.unit_price)
        if quantity:
            lines.append({'from':str(lower),'to':str(tier.to_value) if tier.to_value is not None else None,'quantity':str(quantity),'unit_price':str(tier.unit_price),'amount':str(amount)})
            total += amount
    return total.quantize(Decimal('1'),rounding=ROUND_HALF_UP),lines

class BillingService:
    def __init__(self,repo): self.repo=repo
    def tariff(self, account, day):
        
        active = [t for t in self.repo.all(Tariff, utility_type=account.utility_type) if t.is_active and t.effective_from <= day and (t.effective_to is None or t.effective_to >= day)]
        if not active:
            raise DomainError('TARIFF_NOT_FOUND', 'Chưa có biểu giá phù hợp. Hãy nhờ quản trị viên cấu hình.', 409)

        household = self.repo.get(Household, account.household_id) if getattr(account, 'household_id', None) else None
        user_province = (getattr(account, 'province', None) or (household.province if household else None) or '').strip()
        account_category = getattr(account, 'tariff_category', None) or ('RESIDENTIAL_1PHASE' if account.utility_type == 'ELECTRICITY' else 'RESIDENTIAL')

        # Level 1: Match provider_name + category + province
        matches = [t for t in active if t.provider_name == account.provider_name and getattr(t, 'tariff_category', 'RESIDENTIAL_1PHASE') == account_category and t.province and t.province.strip().lower() == user_province.lower()]

        # Level 2: Match provider_name + category (Nationwide / province is None or empty)
        if not matches:
            matches = [t for t in active if t.provider_name == account.provider_name and getattr(t, 'tariff_category', 'RESIDENTIAL_1PHASE') == account_category and not t.province]

        # Level 3: Match provider_name + default category ('RESIDENTIAL_1PHASE' or 'RESIDENTIAL')
        if not matches:
            default_cat = 'RESIDENTIAL_1PHASE' if account.utility_type == 'ELECTRICITY' else 'RESIDENTIAL'
            matches = [t for t in active if t.provider_name == account.provider_name and getattr(t, 'tariff_category', 'RESIDENTIAL_1PHASE') == default_cat]

        # Level 4: Match provider_name regardless of category/province
        if not matches:
            matches = [t for t in active if t.provider_name == account.provider_name]

        # Level 5: Ultimate fallback to any active tariff for the utility_type if provider name differs
        if not matches:
            matches = active

        tariff = max(matches, key=lambda t: (t.effective_from, t.created_at))
        tiers = sorted(self.repo.all(TariffTier, tariff_id=tariff.id), key=lambda t: t.order_index)
        return tariff, tiers
    def create(self,household,account,period,reading):
        if self.repo.one(Bill,utility_account_id=account.id,billing_period_id=period.id):
            raise DomainError('DUPLICATE_BILL','Tài khoản đã có hóa đơn trong kỳ này.',409)
        tariff,tiers = self.tariff(account,period.end_date)
        amount,lines = calculate_tiers(reading.consumption,tiers)
        due = day_in_month(period.year,period.month,account.due_day)
        if due < reading.reading_date:
            month = period.month % 12 + 1
            due = day_in_month(period.year + (period.month==12),month,account.due_day)
        return self.repo.add(Bill,household_id=household,utility_account_id=account.id,billing_period_id=period.id,
            bill_code=f'{period.year}{period.month:02}-{account.id[:8]}',consumption=reading.consumption,
            estimated_amount=amount,final_amount=amount,due_date=due,
            tariff_version_snapshot={'id':tariff.id,'version':tariff.version,'name':tariff.name,'effective_from':str(tariff.effective_from)},
            bill_detail_snapshot={'tiers':lines,'previous_reading':str(reading.previous_reading),'current_reading':str(reading.current_reading),'reading_source':reading.source,'due_date_source':'CONFIGURED_ESTIMATE','tax_note':'Chưa gồm thuế/phí; biểu giá do quản trị viên cấu hình.'})
