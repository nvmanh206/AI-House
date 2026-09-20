from sqlalchemy import select
from app.models import *

class Repository:
    def __init__(self, db): self.db = db
    def get(self, model, id, lock=False):
        stmt = select(model).where(model.id == id)
        if lock: stmt = stmt.with_for_update()
        return self.db.scalar(stmt)
    def one(self, model, **filters):
        return self.db.scalar(select(model).filter_by(**filters))
    def all(self, model, **filters):
        return list(self.db.scalars(select(model).filter_by(**filters).order_by(model.created_at, model.id)))
    def add(self, model, **data):
        item = model(**data); self.db.add(item); self.db.flush(); return item
    def delete(self, item): self.db.delete(item); self.db.flush()
    def flush(self): self.db.flush()
    def readings(self, household_id):
        stmt = select(MeterReading, Meter, BillingPeriod).join(Meter, Meter.id == MeterReading.meter_id).join(BillingPeriod, BillingPeriod.id == MeterReading.billing_period_id).where(Meter.household_id == household_id).order_by(BillingPeriod.year, BillingPeriod.month)
        return list(self.db.execute(stmt))
    def audit(self, user, household, action, entity):
        self.add(AuditLog, user_id=user, household_id=household, action=action, entity_type=entity.__tablename__, entity_id=entity.id)
