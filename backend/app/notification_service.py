from datetime import timedelta
from sqlalchemy.exc import IntegrityError
from app.models import Notification, HouseholdMember, UtilityAccount, Bill, Meter, MeterReading, BillingPeriod
from app.security import today, day_in_month

class NotificationService:
    def __init__(self,repo): self.repo=repo
    def emit(self,household,kind,key,title,message):
        for member in self.repo.all(HouseholdMember,household_id=household):
            dedupe=f'{key}:{member.user_id}'
            if self.repo.one(Notification,dedupe_key=dedupe): continue
            try:
                with self.repo.db.begin_nested():
                    self.repo.add(Notification,user_id=member.user_id,household_id=household,type=kind,title=title,message=message,dedupe_key=dedupe)
            except IntegrityError as exc:
                if not self.repo.one(Notification,dedupe_key=dedupe): raise exc
    def run(self,day=None):
        day=day or today()
        for a in self.repo.all(UtilityAccount,is_active=True):
            # Include next month's event for reminders crossing month boundaries.
            for offset in (0,1):
                index=day.year*12+day.month-1+offset
                year,month=index//12,index%12+1
                billing=day_in_month(year,month,a.billing_day)
                if billing-timedelta(days=a.reminder_days_before)<=day<=billing:
                    period=self.repo.one(BillingPeriod,household_id=a.household_id,year=year,month=month)
                    has_reading=period and any(self.repo.one(MeterReading,meter_id=m.id,billing_period_id=period.id) for m in self.repo.all(Meter,utility_account_id=a.id))
                    if not has_reading: self.emit(a.household_id,'METER_READING_REMINDER',f'reading:{a.id}:{year}-{month}','Sắp đến kỳ ghi chỉ số',f'Ngày dự kiến {billing:%d/%m/%Y}; hãy nhập chỉ số {a.utility_type}.')
                due=day_in_month(year,month,a.due_day)
                if due-timedelta(days=a.reminder_days_before)<=day<=due and not any(b.due_date.year==year and b.due_date.month==month for b in self.repo.all(Bill,utility_account_id=a.id)):
                    self.emit(a.household_id,'PAYMENT_REMINDER',f'configured:{a.id}:{year}-{month}','Lịch thanh toán dự kiến',f'Ngày cấu hình {due:%d/%m/%Y}; chưa có hóa đơn. Đây không phải hạn chính thức từ nhà cung cấp.')
        for b in self.repo.all(Bill):
            if b.status not in ('UNPAID','OVERDUE'): continue
            account=self.repo.get(UtilityAccount,b.utility_account_id)
            if b.due_date<day:
                b.status='OVERDUE'
                self.emit(b.household_id,'PAYMENT_OVERDUE',f'overdue:{b.id}','Hóa đơn quá hạn dự kiến',f'Hóa đơn {b.bill_code} đã qua ngày {b.due_date:%d/%m/%Y}.')
            elif (b.due_date-day).days<=account.reminder_days_before:
                self.emit(b.household_id,'PAYMENT_REMINDER',f'due:{b.id}','Hóa đơn sắp đến hạn',f'Hóa đơn {b.bill_code} đến hạn dự kiến {b.due_date:%d/%m/%Y}.')
