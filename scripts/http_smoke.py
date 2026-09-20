"""Read-only HTTP smoke test against an explicitly seeded local backend."""
import json,urllib.request,http.cookiejar
base='http://127.0.0.1:8000/api'
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
token=None
def request(path,body=None):
    headers={'Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    with opener.open(req,timeout=15) as response: return json.load(response)
assert request('/health')['status']=='ok'
token=request('/auth/login',{'email':'demo@example.com','password':'DemoHouse123!'})['access_token']
assert request('/auth/me')['household_id']
for path in ['/households/current','/meters','/readings','/bills','/statistics','/notifications','/tariffs']:
    result=request(path);print('PASS',path,len(result))
assert len(request('/readings'))==24
assert len(request('/bills'))==24
chat=request('/ai/chat',{'message':'Tháng tới tiền điện khoảng bao nhiêu?'})
assert chat['metadata']['result']['source']=='FORECAST'
assert 'Ước tính' in chat['message']
print('PASS /ai/chat grounded forecast')
print('PASS HTTP startup and seeded application flow')
