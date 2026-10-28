import httpx
from app.ai.quota import transition,quota_details

def test_window_rejects_duplicates_without_burning_provider_slots():
    state={}
    for _ in range(12):state,wait=transition(state,100,12);assert wait==0
    for _ in range(5):state,wait=transition(state,101,12);assert wait==59
    assert len(state['calls'])==12
    state,wait=transition(state,161,12);assert wait==0 and len(state['calls'])==1

def test_provider_cooldown_survives_later_attempts_and_expires():
    state,_=transition({},100,12,pause=45)
    state,wait=transition(state,110,12);assert wait==35 and state['calls']==[]
    state,wait=transition(state,145,12);assert wait==0

def test_google_retry_info_and_daily_quota_are_parsed_without_raw_error_logging():
    response=httpx.Response(429,json={'error':{'details':[{'@type':'type.googleapis.com/google.rpc.RetryInfo','retryDelay':'38.2s'},
        {'@type':'type.googleapis.com/google.rpc.QuotaFailure','violations':[{'quotaId':'GenerateRequestsPerDayPerProjectPerModel-FreeTier'}]}]}})
    assert quota_details(response)==(39,'DAILY')
