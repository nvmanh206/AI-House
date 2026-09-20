import hashlib, secrets
from datetime import datetime, timedelta, timezone, date
from calendar import monthrange
from zoneinfo import ZoneInfo
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, VerificationError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings
from app.db import get_db
from app.repository import Repository
from app.models import User, AuthSession, HouseholdMember

def today(): return datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()
def day_in_month(year,month,day): return date(year,month,min(day,monthrange(year,month)[1]))

class DomainError(Exception):
    def __init__(self, code, message, status=400): self.code, self.message, self.status = code, message, status

hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)
def verify(password, encoded):
    try: return hasher.verify(encoded,password)
    except (VerifyMismatchError,InvalidHashError,VerificationError): return False
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def utc(value): return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
def issue(repo, user):
    refresh = secrets.token_urlsafe(48)
    member = repo.one(HouseholdMember,user_id=user.id)
    session = repo.add(AuthSession,user_id=user.id,household_id=member.household_id if member else None,
        refresh_hash=digest(refresh),expires_at=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_expire_days))
    return tokens(session,user,refresh)
def tokens(session,user,refresh):
    token = jwt.encode({'sub':user.id,'sid':session.id,'exp':datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes),'iat':datetime.now(timezone.utc),'iss':'utility-api','aud':'utility-web'},settings.jwt_secret,algorithm=settings.jwt_algorithm)
    return {'access_token':token,'refresh_token':session.id+'.'+refresh,'token_type':'bearer'}
def authenticate(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_db)):
    try:
        if not credentials: raise ValueError()
        data = jwt.decode(credentials.credentials,settings.jwt_secret,algorithms=[settings.jwt_algorithm],issuer='utility-api',audience='utility-web',options={'require':['sub','sid','exp','iat']})
        repo = Repository(db)
        session = repo.get(AuthSession,data['sid'])
        user = repo.get(User,data['sub'])
        if not session or session.revoked or session.user_id != data['sub'] or utc(session.expires_at) <= datetime.now(timezone.utc) or not user or not user.is_active: raise ValueError()
        return user,session
    except (jwt.InvalidTokenError,ValueError,KeyError):
        raise DomainError('UNAUTHORIZED','Vui lòng đăng nhập lại.',401)

def household_context(auth,repo,permission=None):
    user,session = auth
    member = repo.one(HouseholdMember, household_id=session.household_id,user_id=user.id) if session.household_id else None
    if not member: raise DomainError('HOUSEHOLD_REQUIRED','Bạn chưa chọn hộ gia đình hợp lệ.',403)
    if permission and member.role != 'OWNER' and permission not in member.permissions:
        raise DomainError('FORBIDDEN','Bạn không có quyền thực hiện thao tác này.',403)
    return member
def admin(auth):
    if auth[0].role != 'ADMIN': raise DomainError('FORBIDDEN','Chỉ quản trị viên được truy cập.',403)
