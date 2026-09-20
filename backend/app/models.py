from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Numeric, ForeignKey, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
from app.enums import DataSource

def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid4())

class Identity:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Updated:
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class User(Identity, Updated, Base):
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(16), default='USER')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Household(Identity, Updated, Base):
    __tablename__ = 'households'
    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(500), default='')
    province: Mapped[str] = mapped_column(String(120), default='')
    district: Mapped[str] = mapped_column(String(120), default='')
    ward: Mapped[str] = mapped_column(String(120), default='')
    member_count: Mapped[int] = mapped_column(Integer, default=1)
    owner_user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))

class HouseholdMember(Identity, Base):
    __tablename__ = 'household_members'
    __table_args__ = (UniqueConstraint('household_id','user_id'),)
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    role: Mapped[str] = mapped_column(String(16), default='MEMBER')
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuthSession(Identity, Base):
    __tablename__ = 'auth_sessions'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    household_id: Mapped[str | None] = mapped_column(ForeignKey('households.id'), nullable=True)
    refresh_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

class UtilityAccount(Identity, Updated, Base):
    __tablename__ = 'utility_accounts'
    __table_args__ = (CheckConstraint("utility_type IN ('ELECTRICITY','WATER')"),)
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'), index=True)
    utility_type: Mapped[str] = mapped_column(String(16))
    provider_name: Mapped[str] = mapped_column(String(120))
    provider_code: Mapped[str] = mapped_column(String(80), default='')
    customer_code: Mapped[str] = mapped_column(String(80), default='')
    tariff_category: Mapped[str] = mapped_column(String(40), default='RESIDENTIAL_1PHASE')
    province: Mapped[str | None] = mapped_column(String(120), nullable=True)
    billing_day: Mapped[int] = mapped_column(Integer, default=25)
    due_day: Mapped[int] = mapped_column(Integer, default=28)
    reminder_days_before: Mapped[int] = mapped_column(Integer, default=3)
    data_source: Mapped[str] = mapped_column(String(20), default=DataSource.MANUAL)
    external_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    external_last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Meter(Identity, Updated, Base):
    __tablename__ = 'meters'
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'), index=True)
    utility_account_id: Mapped[str] = mapped_column(ForeignKey('utility_accounts.id'))
    name: Mapped[str] = mapped_column(String(120))
    meter_code: Mapped[str] = mapped_column(String(80), default='')
    utility_type: Mapped[str] = mapped_column(String(16))
    unit: Mapped[str] = mapped_column(String(8))
    initial_reading: Mapped[Decimal] = mapped_column(Numeric(14,3), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class BillingPeriod(Identity, Base):
    __tablename__ = 'billing_periods'
    __table_args__ = (UniqueConstraint('household_id','year','month'), CheckConstraint('month BETWEEN 1 AND 12'))
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'), index=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[datetime] = mapped_column(Date)
    end_date: Mapped[datetime] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default='OPEN')

class MeterReading(Identity, Updated, Base):
    __tablename__ = 'meter_readings'
    __table_args__ = (UniqueConstraint('meter_id','billing_period_id'), CheckConstraint('current_reading >= previous_reading'), CheckConstraint('consumption >= 0'))
    meter_id: Mapped[str] = mapped_column(ForeignKey('meters.id'), index=True)
    billing_period_id: Mapped[str] = mapped_column(ForeignKey('billing_periods.id'))
    previous_reading: Mapped[Decimal] = mapped_column(Numeric(14,3))
    current_reading: Mapped[Decimal] = mapped_column(Numeric(14,3))
    consumption: Mapped[Decimal] = mapped_column(Numeric(14,3))
    reading_date: Mapped[datetime] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20), default=DataSource.MANUAL)
    source_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5,4), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str] = mapped_column(ForeignKey('users.id'))

class Tariff(Identity, Updated, Base):
    __tablename__ = 'tariffs'
    __table_args__ = (UniqueConstraint('utility_type','provider_name','tariff_category','version'),)
    utility_type: Mapped[str] = mapped_column(String(16))
    provider_name: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(40))
    tariff_category: Mapped[str] = mapped_column(String(40), default='RESIDENTIAL_1PHASE')
    province: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rate_type: Mapped[str] = mapped_column(String(20), default='TIERED')
    effective_from: Mapped[datetime] = mapped_column(Date)
    effective_to: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class TariffTier(Identity, Base):
    __tablename__ = 'tariff_tiers'
    __table_args__ = (UniqueConstraint('tariff_id','order_index'), CheckConstraint('unit_price >= 0'))
    tariff_id: Mapped[str] = mapped_column(ForeignKey('tariffs.id'), index=True)
    from_value: Mapped[Decimal] = mapped_column(Numeric(14,3))
    to_value: Mapped[Decimal | None] = mapped_column(Numeric(14,3), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14,2))
    order_index: Mapped[int] = mapped_column(Integer)

class Bill(Identity, Updated, Base):
    __tablename__ = 'bills'
    __table_args__ = (UniqueConstraint('utility_account_id','billing_period_id'), CheckConstraint('final_amount >= 0'))
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'), index=True)
    utility_account_id: Mapped[str] = mapped_column(ForeignKey('utility_accounts.id'))
    billing_period_id: Mapped[str] = mapped_column(ForeignKey('billing_periods.id'))
    bill_code: Mapped[str] = mapped_column(String(80), unique=True)
    consumption: Mapped[Decimal] = mapped_column(Numeric(14,3))
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    official_amount: Mapped[Decimal | None] = mapped_column(Numeric(14,2), nullable=True)
    final_amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    due_date: Mapped[datetime] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default='UNPAID')
    source: Mapped[str] = mapped_column(String(20), default='SYSTEM_ESTIMATE')
    tariff_version_snapshot: Mapped[dict] = mapped_column(JSON)
    bill_detail_snapshot: Mapped[dict] = mapped_column(JSON)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Payment(Identity, Base):
    __tablename__ = 'payments'
    bill_id: Mapped[str] = mapped_column(ForeignKey('bills.id'), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    method: Mapped[str] = mapped_column(String(30), default='MANUAL')
    reference: Mapped[str] = mapped_column(String(120), default='')
    status: Mapped[str] = mapped_column(String(16), default='SUCCESS')
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Notification(Identity, Base):
    __tablename__ = 'notifications'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'))
    type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(String(1000))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    dedupe_key: Mapped[str] = mapped_column(String(255), unique=True)

class AIAnalysis(Identity, Base):
    __tablename__ = 'ai_analyses'
    household_id: Mapped[str] = mapped_column(ForeignKey('households.id'))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    analysis_type: Mapped[str] = mapped_column(String(40))
    input_period: Mapped[str] = mapped_column(String(40), default='latest')
    result_json: Mapped[dict] = mapped_column(JSON)
    model_name: Mapped[str] = mapped_column(String(80))

class AuditLog(Identity, Base):
    __tablename__ = 'audit_logs'
    user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    household_id: Mapped[str | None] = mapped_column(ForeignKey('households.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36))
    details: Mapped[dict] = mapped_column('metadata', JSON, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
