"""Shared admission/cooldown for backend and ingestion workers; stores no prompts or keys."""
import hashlib
import math
from psycopg.types.json import Jsonb
from app.config import settings
from app.knowledge.store import connection
from app.security import DomainError

def scope():
    key=settings.gemini_api_key or settings.llm_api_key
    return hashlib.sha256((key+'|'+settings.gemini_model).encode()).hexdigest()

def failure(seconds):
    seconds=max(1,math.ceil(seconds))
    error=DomainError('GEMINI_COOLDOWN',f'Đang chờ hạn mức Gemini. Có thể thử gửi lại sau {seconds} giây.',429)
    error.retry_after=seconds
    return error

def transition(state,now,limit,pause=0):
    """Pure rolling window policy. Rejected calls never reserve another provider request."""
    state={'calls':[t for t in state.get('calls',[]) if t>now-60], 'until':state.get('until',0)}
    if pause:
        state['until']=max(state['until'],now+pause);return state,0
    wait=max(state['until']-now,0)
    if len(state['calls'])>=limit:wait=max(wait,state['calls'][0]+60-now)
    if wait>0:return state,math.ceil(wait)
    state['calls'].append(now)
    return state,0

def guard(pause=0):
    if not settings.gemini_quota_guard_enabled:return
    name=scope()
    with connection() as db:
        db.execute('SELECT pg_advisory_xact_lock(hashtext(%s))',(name,))
        row=db.execute('SELECT state FROM provider_limits WHERE scope=%s',(name,)).fetchone()
        now=float(db.execute('SELECT extract(epoch FROM clock_timestamp()) AS now').fetchone()['now'])
        state,wait=transition(row['state'] if row else {},now,settings.gemini_requests_per_minute,pause)
        db.execute('INSERT INTO provider_limits(scope,state) VALUES(%s,%s) ON CONFLICT(scope) DO UPDATE SET state=EXCLUDED.state',(name,Jsonb(state)))
    if wait:raise failure(wait)

def quota_details(response):
    seconds=60;kind='UNKNOWN'
    header=response.headers.get('Retry-After','')
    if header.isdigit():seconds=int(header)
    try:
        for detail in response.json().get('error',{}).get('details',[]):
            if detail.get('@type','').endswith('RetryInfo'):
                value=detail.get('retryDelay','')
                if value.endswith('s'):seconds=math.ceil(float(value[:-1]))
            for item in detail.get('violations',[]):
                metric=item.get('quotaId','')
                if 'PerDay' in metric:kind='DAILY'
                elif 'Tokens' in metric and kind!='DAILY':kind='TOKENS'
                elif 'PerMinute' in metric and kind=='UNKNOWN':kind='REQUESTS'
    except (ValueError,TypeError,AttributeError,OverflowError):pass
    return max(1,min(seconds,86400)),kind
