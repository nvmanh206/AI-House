from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect
from app.models import *
from app.security import DomainError, household_context, hasher, verify, issue, today, day_in_month
from app.billing_service import BillingService, calculate_tiers
from app.anomaly_service import AnomalyService
from app.notification_service import NotificationService
from app.providers.payment import ManualPaymentProvider
from app.forecast_service import ForecastService

def today(): return datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()
def day_in_month(year,month,day): return date(year,month,min(day,monthrange(year,month)[1]))
def public(item):
    excluded={'password_hash','refresh_hash'}
    return jsonable_encoder({a.key:getattr(item,a.key) for a in inspect(item).mapper.column_attrs if a.key not in excluded},custom_encoder={Decimal:str})

class AuthService:
    def __init__(self,repo): self.repo=repo
    def register(self,data):
        from app.config import settings
        first_admin=False
        if settings.bootstrap_first_user_admin and settings.app_env=='development':
            from sqlalchemy import text
            if self.repo.db.bind.dialect.name=='postgresql':self.repo.db.execute(text('SELECT pg_advisory_xact_lock(7410829)'))
            first_admin=not self.repo.all(User)
        if self.repo.one(User,email=data.email.lower()): raise DomainError('EMAIL_EXISTS','Email đã được sử dụng.',409)
        user=self.repo.add(User,email=data.email.lower(),full_name=data.full_name,password_hash=hasher.hash(data.password))
        if first_admin:user.role='ADMIN'
        self.repo.audit(user.id,None,'REGISTER',user)
        return issue(self.repo,user)
    def login(self,data):
        user=self.repo.one(User,email=data.email.lower())
        if not user or not verify(data.password,user.password_hash) or not user.is_active:
            raise DomainError('INVALID_CREDENTIALS','Email hoặc mật khẩu không đúng.',401)
        self.repo.audit(user.id,None,'LOGIN',user)
        return issue(self.repo,user)

class HouseholdService:
    def __init__(self,repo,auth): self.repo,self.auth=repo,auth
    def member(self,permission=None): return household_context(self.auth,self.repo,permission)
    def scope(self,model,id,permission=None,lock=False):
        membership=self.member(permission)
        item=self.repo.get(model,id,lock)
        if not item or getattr(item,'household_id',item.id if model is Household else None)!=membership.household_id:
            raise DomainError('NOT_FOUND','Không tìm thấy dữ liệu trong hộ gia đình.',404)
        return item
    def households(self):
        return [public(self.repo.get(Household,m.household_id)) for m in self.repo.all(HouseholdMember,user_id=self.auth[0].id)]
    def select(self,id):
        if not self.repo.one(HouseholdMember,user_id=self.auth[0].id,household_id=id): raise DomainError('FORBIDDEN','Bạn không thuộc hộ gia đình này.',403)
        self.auth[1].household_id=id
        return {'household_id':id}
    def onboard(self,data):
        household=self.repo.add(Household,**data.model_dump(exclude={'accounts'}),owner_user_id=self.auth[0].id)
        self.repo.add(HouseholdMember,household_id=household.id,user_id=self.auth[0].id,role='OWNER',permissions=['write','pay','members'])
        self.auth[1].household_id=household.id
        for a in data.accounts:
            account=self.repo.add(UtilityAccount,household_id=household.id,**a.model_dump(exclude={'initial_reading'}))
            self.repo.add(Meter,household_id=household.id,utility_account_id=account.id,name='Công tơ điện' if a.utility_type=='ELECTRICITY' else 'Đồng hồ nước',utility_type=a.utility_type,unit='kWh' if a.utility_type=='ELECTRICITY' else 'm³',initial_reading=a.initial_reading)
        self.repo.audit(self.auth[0].id,household.id,'ONBOARD',household)
        return public(household)
    def profile(self): return public(self.repo.get(Household,self.member().household_id))
    def update(self,data):
        m=self.member('members'); h=self.repo.get(Household,m.household_id)
        for k,v in data.model_dump().items(): setattr(h,k,v)
        self.repo.audit(self.auth[0].id,h.id,'UPDATE',h)
        return public(h)
    def members(self):
        return [{**public(m),'full_name':self.repo.get(User,m.user_id).full_name,'email':self.repo.get(User,m.user_id).email} for m in self.repo.all(HouseholdMember,household_id=self.member().household_id)]
    def add_member(self,data):
        m=self.member('members'); user=self.repo.one(User,email=data.email.lower())
        if not user or not user.is_active: raise DomainError('USER_NOT_FOUND','Thành viên cần đăng ký tài khoản trước.',404)
        if self.repo.one(HouseholdMember,household_id=m.household_id,user_id=user.id): raise DomainError('DUPLICATE_MEMBER','Thành viên đã thuộc hộ.',409)
        item=self.repo.add(HouseholdMember,household_id=m.household_id,user_id=user.id,permissions=list(set(data.permissions)))
        self.repo.audit(self.auth[0].id,m.household_id,'ADD_MEMBER',item)
        return public(item)
    def remove_member(self,id):
        item=self.scope(HouseholdMember,id,'members')
        if item.role=='OWNER': raise DomainError('OWNER_REQUIRED','Không được xóa chủ hộ.',409)
        self.repo.audit(self.auth[0].id,item.household_id,'REMOVE_MEMBER',item)
        self.repo.delete(item)
        return {'ok':True}
    def accounts(self): return [public(a) for a in self.repo.all(UtilityAccount,household_id=self.member().household_id)]
    def account(self,data,id=None):
        if id:
            item=self.scope(UtilityAccount,id,'write')
            if data.utility_type!=item.utility_type: raise DomainError('INVALID_UTILITY','Không thể đổi loại tài khoản.')
            for k,v in data.model_dump().items(): setattr(item,k,v)
        else: item=self.repo.add(UtilityAccount,household_id=self.member('write').household_id,**data.model_dump())
        self.repo.audit(self.auth[0].id,item.household_id,'SAVE_ACCOUNT',item)
        return public(item)
    def meters(self): return [public(m) for m in self.repo.all(Meter,household_id=self.member().household_id)]
    def meter(self,data,id=None):
        if id:
            item=self.scope(Meter,id,'write')
            self.repo.get(UtilityAccount,item.utility_account_id,lock=True)
            if data.is_active and any(m.is_active and m.id!=item.id for m in self.repo.all(Meter,utility_account_id=item.utility_account_id)):
                raise DomainError('ACTIVE_METER_EXISTS','Tài khoản đã có công tơ hoạt động khác.',409)
            for k,v in data.model_dump().items(): setattr(item,k,v)
        else:
            account=self.scope(UtilityAccount,data.utility_account_id,'write',lock=True)
            if any(m.is_active for m in self.repo.all(Meter,utility_account_id=account.id)):
                raise DomainError('ACTIVE_METER_EXISTS','V1 hỗ trợ một công tơ hoạt động mỗi tài khoản; hãy vô hiệu hóa công tơ cũ.',409)
            item=self.repo.add(Meter,household_id=account.household_id,utility_type=account.utility_type,unit='kWh' if account.utility_type=='ELECTRICITY' else 'm³',**data.model_dump())
        self.repo.audit(self.auth[0].id,item.household_id,'SAVE_METER',item)
        return public(item)
    def history(self):
        return [{**public(r),'utility_type':m.utility_type,'meter_name':m.name,'unit':m.unit,'period':f'{p.year}-{p.month:02}'} for r,m,p in self.repo.readings(self.member().household_id)]

    def _cascade_update_next(self, account, next_reading, next_period, new_previous):
        if next_reading.current_reading < new_previous:
            raise DomainError('INVALID_METER_READING', f'Chỉ số kỳ sau ({next_reading.current_reading}) không được nhỏ hơn chỉ số kỳ này ({new_previous}).')
        next_reading.previous_reading = new_previous
        next_reading.consumption = next_reading.current_reading - new_previous
        bill = self.repo.one(Bill, utility_account_id=account.id, billing_period_id=next_period.id)
        if bill:
            tariff, tiers = BillingService(self.repo).tariff(account, next_period.end_date)
            amount, lines = calculate_tiers(next_reading.consumption, tiers)
            bill.consumption = next_reading.consumption
            bill.estimated_amount = amount
            bill.final_amount = amount
            bill.bill_detail_snapshot = {**bill.bill_detail_snapshot, 'tiers': lines, 'previous_reading': str(next_reading.previous_reading), 'current_reading': str(next_reading.current_reading)}

    def reading(self, data):
        meter = self.scope(Meter, data.meter_id, 'write', lock=True)
        if not meter.is_active: raise DomainError('METER_DISABLED', 'Công tơ đã ngừng hoạt động.')
        if data.reading_date > today(): raise DomainError('FUTURE_READING', 'Không nhập chỉ số trong tương lai.')
        account = self.repo.get(UtilityAccount, meter.utility_account_id, lock=True)

        self.repo.get(Household, meter.household_id, lock=True)
        period = self.repo.one(BillingPeriod, household_id=meter.household_id, year=data.year, month=data.month)

        # Check if bill for this account and period already exists
        if period and self.repo.one(Bill, utility_account_id=account.id, billing_period_id=period.id):
            raise DomainError('DUPLICATE_PERIOD', 'Kỳ này đã có chỉ số và hóa đơn. Vui lòng dùng chức năng Sửa trong lịch sử nếu muốn điều chỉnh.', 409)

        # Check if reading for this meter and period already exists
        if period and self.repo.one(MeterReading, meter_id=meter.id, billing_period_id=period.id):
            raise DomainError('DUPLICATE_PERIOD', 'Kỳ này đã có chỉ số. Vui lòng dùng chức năng Sửa trong lịch sử nếu muốn điều chỉnh.', 409)

        history = [(r, p) for r, m, p in self.repo.readings(meter.household_id) if m.id == meter.id]
        prev_item = next(((r, p) for r, p in reversed(history) if (p.year, p.month) < (data.year, data.month)), None)
        previous = prev_item[0].current_reading if prev_item else meter.initial_reading
        next_item = next(((r, p) for r, p in history if (p.year, p.month) > (data.year, data.month)), None)

        if data.current_reading < previous:
            raise DomainError('INVALID_METER_READING', f'Chỉ số mới ({data.current_reading}) không được nhỏ hơn chỉ số kỳ trước ({previous}).')
        if next_item and data.current_reading > next_item[0].current_reading:
            raise DomainError('INVALID_METER_READING', f'Không thể ghi kỳ {data.month:02}/{data.year}: chỉ số {data.current_reading} lớn hơn chỉ số kỳ {next_item[1].month:02}/{next_item[1].year} đã ghi ({next_item[0].current_reading}). Hãy kiểm tra lại chỉ số hai kỳ; chỉ số kỳ trước không được lớn hơn kỳ sau.')

        if not period:
            period = self.repo.add(BillingPeriod, household_id=meter.household_id, year=data.year, month=data.month, start_date=date(data.year, data.month, 1), end_date=day_in_month(data.year, data.month, 31))

        reading = self.repo.add(MeterReading, meter_id=meter.id, billing_period_id=period.id, previous_reading=previous, current_reading=data.current_reading, consumption=data.current_reading - previous, reading_date=data.reading_date, created_by=self.auth[0].id)
        bill = None
        try:
            bill = BillingService(self.repo).create(meter.household_id, account, period, reading)
        except DomainError as exc:
            if exc.code != 'TARIFF_NOT_FOUND': raise

        if next_item:
            self._cascade_update_next(account, next_item[0], next_item[1], reading.current_reading)

        anomaly = AnomalyService.detect(reading.consumption, [r.consumption for r, p in history if r.id != reading.id])
        notifications = NotificationService(self.repo)
        if bill:
            notifications.emit(meter.household_id, 'BILL_CREATED', f'bill:{bill.id}', 'Đã tạo hóa đơn ước tính', f'Kỳ {data.month}/{data.year}: {bill.final_amount:,.0f} VND.')
        if anomaly['is_anomaly']:
            notifications.emit(meter.household_id, 'ABNORMAL_CONSUMPTION', f'anomaly:{reading.id}', 'Tiêu thụ tăng bất thường', f'Tăng {anomaly["deviation_percent"]}% so với trung bình các kỳ trước.')
        self.repo.audit(self.auth[0].id, meter.household_id, 'CREATE_READING', reading)
        return {'reading': public(reading), 'bill': public(bill) if bill else None, 'anomaly': anomaly,
                'billing_status': 'CREATED' if bill else 'TARIFF_NOT_FOUND'}

    def generate_bills(self):
        member=self.member('write')
        created=[];skipped=[]
        for reading,meter,period in self.repo.readings(member.household_id):
            account=self.repo.get(UtilityAccount,meter.utility_account_id,lock=True)
            if self.repo.one(Bill,utility_account_id=account.id,billing_period_id=period.id):continue
            try:
                bill=BillingService(self.repo).create(member.household_id,account,period,reading)
            except DomainError as exc:
                if exc.code not in ('TARIFF_NOT_FOUND','TARIFF_AMBIGUOUS'):raise
                skipped.append({'reading_id':reading.id,'period':f'{period.year}-{period.month:02}','provider':account.provider_name,'code':exc.code,'message':exc.message})
                continue
            self.repo.audit(self.auth[0].id,member.household_id,'GENERATE_BILL_FROM_READING',bill)
            created.append(public(bill))
        return {'created':created,'skipped':skipped}

    def update_reading(self, id, data):
        reading = self.repo.get(MeterReading, id, lock=True)
        if not reading: raise DomainError('NOT_FOUND', 'Không tìm thấy bản ghi chỉ số.', 404)
        meter = self.scope(Meter, reading.meter_id, 'write', lock=True)
        period = self.repo.get(BillingPeriod, reading.billing_period_id)
        account = self.repo.get(UtilityAccount, meter.utility_account_id, lock=True)

        bill = self.repo.one(Bill, utility_account_id=account.id, billing_period_id=period.id)
        if bill and (bill.status == 'PAID' or self.repo.one(Payment, bill_id=bill.id)):
            raise DomainError('BILL_PAID', 'Không thể sửa chỉ số của kỳ đã thanh toán hóa đơn.', 400)

        history = [(r, p) for r, m, p in self.repo.readings(meter.household_id) if m.id == meter.id]
        prev_item = next(((r, p) for r, p in reversed(history) if (p.year, p.month) < (period.year, period.month)), None)
        previous = prev_item[0].current_reading if prev_item else meter.initial_reading
        next_item = next(((r, p) for r, p in history if (p.year, p.month) > (period.year, period.month)), None)

        if data.current_reading < previous:
            raise DomainError('INVALID_METER_READING', f'Chỉ số mới ({data.current_reading}) không được nhỏ hơn chỉ số kỳ trước ({previous}).')
        if next_item and data.current_reading > next_item[0].current_reading:
            raise DomainError('INVALID_METER_READING', f'Chỉ số mới ({data.current_reading}) không được lớn hơn chỉ số kỳ sau ({next_item[0].current_reading}).')

        reading.previous_reading = previous
        reading.current_reading = data.current_reading
        reading.consumption = data.current_reading - previous
        if data.reading_date:
            if (data.reading_date.year, data.reading_date.month) != (period.year, period.month):
                raise DomainError('INVALID_DATE', 'Ngày ghi phải thuộc kỳ hóa đơn.', 422)
            if data.reading_date > today():
                raise DomainError('FUTURE_READING', 'Không nhập chỉ số trong tương lai.', 400)
            reading.reading_date = data.reading_date

        if bill:
            tariff, tiers = BillingService(self.repo).tariff(account, period.end_date)
            amount, lines = calculate_tiers(reading.consumption, tiers)
            bill.consumption = reading.consumption
            bill.estimated_amount = amount
            bill.final_amount = amount
            bill.bill_detail_snapshot = {**bill.bill_detail_snapshot, 'tiers': lines, 'previous_reading': str(reading.previous_reading), 'current_reading': str(reading.current_reading)}

        if next_item:
            self._cascade_update_next(account, next_item[0], next_item[1], reading.current_reading)

        self.repo.audit(self.auth[0].id, meter.household_id, 'UPDATE_READING', reading)
        return {'reading': public(reading), 'bill': public(bill) if bill else None}

    def delete_reading(self, id):
        reading = self.repo.get(MeterReading, id, lock=True)
        if not reading: raise DomainError('NOT_FOUND', 'Không tìm thấy bản ghi chỉ số.', 404)
        meter = self.scope(Meter, reading.meter_id, 'write', lock=True)
        period = self.repo.get(BillingPeriod, reading.billing_period_id)
        account = self.repo.get(UtilityAccount, meter.utility_account_id, lock=True)

        bill = self.repo.one(Bill, utility_account_id=account.id, billing_period_id=period.id)
        if bill:
            if bill.status == 'PAID' or self.repo.one(Payment, bill_id=bill.id):
                raise DomainError('BILL_PAID', 'Không thể xóa chỉ số của kỳ đã thanh toán hóa đơn.', 400)
            self.repo.delete(bill)

        history = [(r, p) for r, m, p in self.repo.readings(meter.household_id) if m.id == meter.id]
        prev_item = next(((r, p) for r, p in reversed(history) if (p.year, p.month) < (period.year, period.month)), None)
        previous = prev_item[0].current_reading if prev_item else meter.initial_reading
        next_item = next(((r, p) for r, p in history if (p.year, p.month) > (period.year, period.month)), None)

        if next_item:
            self._cascade_update_next(account, next_item[0], next_item[1], previous)

        self.repo.delete(reading)
        self.repo.audit(self.auth[0].id, meter.household_id, 'DELETE_READING', reading)
        return {'ok': True}
    def bills(self):
        result=[]
        for b in self.repo.all(Bill,household_id=self.member().household_id):
            account=self.repo.get(UtilityAccount,b.utility_account_id); period=self.repo.get(BillingPeriod,b.billing_period_id)
            result.append({**public(b),'utility_type':account.utility_type,'period':f'{period.year}-{period.month:02}','status':'OVERDUE' if b.status=='UNPAID' and b.due_date<today() else b.status})
        return sorted(result,key=lambda b:b['period'],reverse=True)
    def bill(self,id):
        self.scope(Bill,id)
        return next(b for b in self.bills() if b['id']==id)
    def pay(self,data):
        bill=self.scope(Bill,data.bill_id,'pay',lock=True)
        existing=self.repo.one(Payment,bill_id=bill.id)
        if existing: return public(existing)
        if bill.status not in ('UNPAID','OVERDUE'): raise DomainError('INVALID_BILL_STATUS','Hóa đơn không thể thanh toán.',409)
        result=ManualPaymentProvider().record(bill.final_amount,data.reference)
        payment=self.repo.add(Payment,bill_id=bill.id,amount=bill.final_amount,reference=data.reference,status=result['status'])
        bill.status='PAID'; bill.paid_at=now()
        NotificationService(self.repo).emit(bill.household_id,'PAYMENT_SUCCESS',f'paid:{bill.id}','Đã ghi nhận thanh toán','Bạn đã đánh dấu thanh toán thủ công. Đây không phải xác nhận từ ngân hàng.')
        self.repo.audit(self.auth[0].id,bill.household_id,'MANUAL_PAYMENT',bill)
        return public(payment)
    def statistics(self,months=6,start=None,end=None):
        history=self.history(); current=today()
        first_index=current.year*12+current.month-1-(months-1)
        first=start or date(first_index//12,first_index%12+1,1)
        last=end or current
        if first>last: raise DomainError('INVALID_RANGE','Ngày bắt đầu phải trước ngày kết thúc.')
        rows={}
        for r in history:
            year,month=map(int,r['period'].split('-'))
            if (first.year,first.month)<=(year,month)<=(last.year,last.month):
                row=rows.setdefault(r['period'],{'period':r['period'],'ELECTRICITY':None,'WATER':None,'ELECTRICITY_COST':None,'WATER_COST':None,'cost':None})
                row[r['utility_type']]=(row[r['utility_type']] or 0)+float(r['consumption'])
        for b in self.bills():
            if b['period'] in rows and b['status']!='CANCELLED':
                row=rows[b['period']]
                amount=Decimal(b['final_amount'])
                row['cost']=(row['cost'] or Decimal(0))+amount
                key=b['utility_type']+'_COST'
                row[key]=(row[key] or Decimal(0))+amount
        series=[rows[k] for k in sorted(rows)]
        for row in series:
            for key in ('cost','ELECTRICITY_COST','WATER_COST'):
                if row[key] is not None: row[key]=float(row[key])
        summaries={}
        for key in ('ELECTRICITY','WATER','cost'):
            values=[r[key] for r in series if r[key] is not None]
            summaries[key]={'average':sum(values)/len(values) if values else None,'highest':max(values) if values else None,'lowest':min(values) if values else None}
        return {'series':series,'summary':summaries,'start':str(first),'end':str(last),'note':'Thống kê các kỳ đã nhập; kỳ thiếu không được coi là tiêu thụ bằng 0.'}
    def tariffs_for_agent(self):
        result=[]
        for a in self.repo.all(UtilityAccount,household_id=self.member().household_id,is_active=True):
            try:
                tariff,tiers=BillingService(self.repo).tariff(a,today())
                result.append({'utility_type':a.utility_type,'version':tariff.version,'name':tariff.name,'provider_name':tariff.provider_name,'effective_from':str(tariff.effective_from),'effective_to':str(tariff.effective_to) if tariff.effective_to else None,'source':'CONFIGURED','tiers':[public(t) for t in tiers]})
            except DomainError as exc:
                if exc.code!='TARIFF_NOT_FOUND': raise
                result.append({'utility_type':a.utility_type,'available':False})
        return result
    def forecast(self,utility):
        member=self.member()
        accounts=self.repo.all(UtilityAccount,household_id=member.household_id,utility_type=utility,is_active=True)
        if len(accounts)!=1: return {'available':False,'reason':'Dự báo V1 cần đúng một tài khoản hoạt động cho loại tiện ích này.','source':'FORECAST'}
        day=today(); next_index=day.year*12+day.month
        forecast_day=day_in_month(next_index//12,next_index%12+1,31)
        try: tariff,tiers=BillingService(self.repo).tariff(accounts[0],forecast_day)
        except DomainError as exc:
            if exc.code!='TARIFF_NOT_FOUND': raise
            return {'available':False,'reason':exc.message,'source':'FORECAST'}
        # Aggregate multiple meter records in the same month before forecasting.
        monthly={}
        for r,m,p in self.repo.readings(member.household_id):
            if m.utility_account_id==accounts[0].id: monthly[(p.year,p.month)]=monthly.get((p.year,p.month),Decimal(0))+r.consumption
        return ForecastService.predict([monthly[k] for k in sorted(monthly)],tiers)
    def agent_notifications(self):
        return [{'type':n.type,'scheduled_at':str(n.scheduled_at),'is_read':n.is_read} for n in self.repo.all(Notification,user_id=self.auth[0].id,household_id=self.member().household_id)[-10:]]
