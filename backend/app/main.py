import logging, secrets, time
from collections import defaultdict, deque
from datetime import date,datetime,timezone
from typing import Annotated
from fastapi import FastAPI, Depends, Request, Response, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.db import get_db
from app.models import *
from app.schemas import *
from app.repository import Repository
from app.security import authenticate, DomainError, digest, utc, tokens, admin
from app.services import AuthService, HouseholdService, public, hasher, verify
from app.admin_service import AdminService
from app.ai.context import build_context
from app.ai.agent import Agent

app=FastAPI(title='Nhà Mình · Household Utility API',version='1.0.0')
from app.knowledge.api import router as knowledge_router
app.include_router(knowledge_router)
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_url],allow_credentials=True,allow_methods=['GET','POST','PATCH','DELETE'],allow_headers=['Authorization','Content-Type'],expose_headers=['Content-Disposition'])
log=logging.getLogger('utility')
@app.exception_handler(DomainError)
async def domain_error(request,exc):
    retry=getattr(exc,'retry_after',None)
    return JSONResponse(status_code=exc.status,content={'error':{'code':exc.code,'message':exc.message,**({'retry_after':retry} if retry else {})}},headers={'Retry-After':str(retry)} if retry else None)
@app.exception_handler(RequestValidationError)
async def validation_error(request,exc): return JSONResponse(status_code=422,content={'error':{'code':'VALIDATION_ERROR','message':'Dữ liệu không hợp lệ. Kiểm tra các trường và định dạng.','fields':[{'field':'.'.join(map(str,e['loc'])),'message':e['msg']} for e in exc.errors()]}})
@app.exception_handler(IntegrityError)
async def conflict(request,exc): return JSONResponse(status_code=409,content={'error':{'code':'CONFLICT','message':'Dữ liệu trùng hoặc liên kết không hợp lệ.'}})
@app.exception_handler(HTTPException)
async def http_error(request,exc): return JSONResponse(status_code=exc.status_code,content={'error':{'code':'HTTP_ERROR','message':str(exc.detail)}})
@app.exception_handler(Exception)
async def unexpected(request,exc):
    # Do not log exception text: SQL parameters can contain sensitive input.
    log.error('Unhandled error type=%s path=%s',type(exc).__name__,request.url.path)
    return JSONResponse(status_code=500,content={'error':{'code':'INTERNAL_ERROR','message':'Có lỗi hệ thống. Vui lòng thử lại sau.'}})

attempts=defaultdict(deque)
@app.middleware('http')
async def controls(request,call_next):
    if settings.rate_limit_enabled and request.url.path in ('/api/auth/login','/api/auth/register','/api/auth/refresh'):
        key=(request.client.host if request.client else 'unknown', request.url.path)
        now=time.monotonic()
        bucket=attempts[key]
        while bucket and bucket[0]<now-60: bucket.popleft()
        limit=settings.rate_limit_refresh_per_min if request.url.path=='/api/auth/refresh' else settings.rate_limit_auth_per_min
        if len(bucket)>=limit: return JSONResponse(status_code=429,headers={'Retry-After':'60'},content={'error':{'code':'RATE_LIMITED','message':'Thử lại sau một phút.'}})
        bucket.append(now)
        if len(attempts)>10000:
            for k in list(attempts):
                if not attempts[k] or attempts[k][-1]<now-60: del attempts[k]
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Cache-Control']='no-store'
    return response

def repo(db=Depends(get_db)): return Repository(db)
def service(r=Depends(repo),auth=Depends(authenticate)): return HouseholdService(r,auth)
def admin_service(r=Depends(repo),auth=Depends(authenticate)): return AdminService(r,auth)
R=Annotated[Repository,Depends(repo)]
S=Annotated[HouseholdService,Depends(service)]
A=Annotated[AdminService,Depends(admin_service)]
Auth=Annotated[tuple,Depends(authenticate)]

def set_tokens(response,payload):
    response.set_cookie(settings.refresh_cookie_name,payload.pop('refresh_token'),httponly=True,secure=settings.app_env=='production',samesite='strict',path='/api/auth',max_age=settings.refresh_token_expire_days*86400)
    return payload
@app.get('/api/health')
def health(r:R): r.db.execute(text('SELECT 1')); return {'status':'ok'}
@app.post('/api/auth/register',status_code=201)
def register(data:Register,response:Response,r:R): return set_tokens(response,AuthService(r).register(data))
@app.post('/api/auth/login')
def login(data:Login,response:Response,r:R): return set_tokens(response,AuthService(r).login(data))
@app.post('/api/auth/refresh')
def refresh(request:Request,response:Response,r:R):
    if request.headers.get('origin') not in (None,settings.frontend_url): raise DomainError('FORBIDDEN','Origin không hợp lệ.',403)
    raw=request.cookies.get(settings.refresh_cookie_name,'')
    sid,separator,secret=raw.partition('.')
    session=r.get(AuthSession,sid,lock=True) if separator else None
    if not session or session.revoked or utc(session.expires_at)<=datetime.now(timezone.utc) or not secrets.compare_digest(session.refresh_hash,digest(secret)):
        raise DomainError('UNAUTHORIZED','Phiên đăng nhập hết hạn.',401)
    user=r.get(User,session.user_id)
    if not user.is_active: raise DomainError('UNAUTHORIZED','Tài khoản đã bị khóa.',401)
    fresh=secrets.token_urlsafe(48); session.refresh_hash=digest(fresh)
    return set_tokens(response,tokens(session,user,fresh))
@app.post('/api/auth/logout')
def logout(response:Response,auth:Auth):
    auth[1].revoked=True; response.delete_cookie(settings.refresh_cookie_name,path='/api/auth'); return {'ok':True}
@app.get('/api/auth/me')
def me(auth:Auth,r:R):
    member=r.one(HouseholdMember,user_id=auth[0].id,household_id=auth[1].household_id)
    return {**public(auth[0]),'household_id':auth[1].household_id if member else None,'membership_role':member.role if member else None,'permissions':member.permissions if member else []}
@app.patch('/api/auth/me')
def update_profile(data:Profile,auth:Auth,r:R):
    auth[0].full_name=data.full_name; r.audit(auth[0].id,None,'UPDATE_PROFILE',auth[0]); return public(auth[0])
@app.post('/api/auth/password')
def password(data:Password,auth:Auth,r:R):
    if not verify(data.old_password,auth[0].password_hash): raise DomainError('INVALID_PASSWORD','Mật khẩu hiện tại không đúng.')
    auth[0].password_hash=hasher.hash(data.new_password)
    for session in r.all(AuthSession,user_id=auth[0].id): session.revoked=True
    r.audit(auth[0].id,None,'CHANGE_PASSWORD',auth[0]); return {'ok':True}
@app.get('/api/households')
def households(s:S): return s.households()
@app.post('/api/households',status_code=201)
def onboarding(data:Onboarding,s:S): return s.onboard(data)
@app.post('/api/households/{id}/select')
def select_household(id:str,s:S): return s.select(id)
@app.get('/api/households/current')
def household(s:S): return s.profile()
@app.patch('/api/households/current')
def update_household(data:HouseholdInput,s:S): return s.update(data)
@app.get('/api/households/{id}')
def get_household(id:str,s:S): return public(s.scope(Household,id))
@app.get('/api/members')
def members(s:S): return s.members()
@app.post('/api/members',status_code=201)
def add_member(data:MemberInput,s:S): return s.add_member(data)
@app.delete('/api/members/{id}')
def remove_member(id:str,s:S): return s.remove_member(id)
@app.get('/api/utility-accounts')
def accounts(s:S): return s.accounts()
@app.post('/api/utility-accounts',status_code=201)
def add_account(data:AccountInput,s:S): return s.account(data)
@app.patch('/api/utility-accounts/{id}')
def update_account(id:str,data:AccountInput,s:S): return s.account(data,id)
@app.get('/api/meters')
def meters(s:S): return s.meters()
@app.post('/api/meters',status_code=201)
def add_meter(data:MeterInput,s:S): return s.meter(data)
@app.patch('/api/meters/{id}')
def update_meter(id:str,data:MeterUpdate,s:S): return s.meter(data,id)
@app.get('/api/readings')
def readings(s:S): return s.history()
@app.post('/api/readings',status_code=201)
def add_reading(data:ReadingInput,s:S): return s.reading(data)
@app.patch('/api/readings/{id}')
def update_reading(id:str,data:ReadingUpdate,s:S): return s.update_reading(id,data)
@app.delete('/api/readings/{id}')
def delete_reading(id:str,s:S): return s.delete_reading(id)
@app.get('/api/bills')
def bills(s:S,period:str|None=None,status:str|None=None,utility_type:Utility|None=None): return [b for b in s.bills() if (not period or b['period']==period) and (not status or b['status']==status) and (not utility_type or b['utility_type']==utility_type)]
@app.post('/api/bills/generate')
def generate_bills(s:S):return s.generate_bills()
@app.get('/api/bills/{id}')
def bill(id:str,s:S): return s.bill(id)
@app.post('/api/payments')
def pay(data:PaymentInput,s:S): return s.pay(data)
@app.get('/api/payments')
def payments(s:S):
    bill_ids={b['id'] for b in s.bills()}; return [public(p) for p in s.repo.all(Payment) if p.bill_id in bill_ids]
@app.get('/api/tariffs')
def tariffs(auth:Auth,r:R): return [{**public(t),'tiers':[public(x) for x in sorted(r.all(TariffTier,tariff_id=t.id),key=lambda x:x.order_index)]} for t in r.all(Tariff)]
@app.get('/api/notifications')
def notifications(s:S): return [public(n) for n in s.repo.all(Notification,user_id=s.auth[0].id,household_id=s.member().household_id)][::-1]
@app.post('/api/notifications/read-all')
def read_all_notifications(s:S):
    notes = s.repo.all(Notification, user_id=s.auth[0].id, household_id=s.member().household_id, is_read=False)
    for n in notes: n.is_read = True
    return {'ok': True, 'count': len(notes)}
@app.patch('/api/notifications/{id}/read')
def read_notification(id:str,s:S):
    n=s.scope(Notification,id)
    if n.user_id!=s.auth[0].id: raise DomainError('NOT_FOUND','Không tìm thấy thông báo.',404)
    n.is_read=True; return public(n)
@app.get('/api/statistics')
def statistics(s:S,months:int=Query(6,ge=1,le=12),start:date|None=None,end:date|None=None): return s.statistics(months,start,end)
@app.get('/api/statistics/forecast')
def forecast(s:S,utility_type:Utility='ELECTRICITY'): return s.forecast(utility_type)
@app.post('/api/ai/chat')
def chat(data:ChatInput,s:S):
    context=build_context(s.auth,s.repo)
    try:
        result=Agent(context,s).chat(data.message,image_base64=data.image_base64,raw_ocr_text=data.raw_ocr_text,conversation_id=data.conversation_id)
    except DomainError as exc:
        log.warning('AI request failed code=%s request_id=%s',exc.code,context.request_id)
        s.repo.add(AIAnalysis,household_id=context.household_id,user_id=context.user_id,analysis_type='ERROR',result_json={'status':'error','code':exc.code,'request_id':context.request_id},model_name=settings.llm_provider)
        s.repo.db.commit()
        raise
    error_code=result.get('metadata',{}).get('error_code')
    s.repo.add(AIAnalysis,household_id=context.household_id,user_id=context.user_id,analysis_type=result['intent'],result_json={'status':'error' if error_code else 'success','source_count':len(result['sources']),'error_code':error_code},model_name=settings.llm_provider)
    return result
@app.get('/api/admin')
def admin_overview(a:A): return a.overview()
@app.get('/api/admin/users')
def admin_users(a:A): return a.users()
@app.patch('/api/admin/users/{id}')
def admin_user(id:str,data:UserUpdate,a:A): return a.update_user(id,data)
@app.post('/api/admin/tariffs',status_code=201)
def admin_tariff(data:TariffInput,a:A): return a.tariff(data)
@app.get('/api/admin/audit')
def audit(a:A): return a.audit()
