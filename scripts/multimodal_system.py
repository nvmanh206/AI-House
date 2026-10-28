"""Real Gemini + isolated PostgreSQL acceptance. No app database writes.

Use system_test.py prepare first if no isolated System state exists.
Run `serve`, then `exercise`. Generated invoice is explicitly a test fixture.
"""
import argparse
import base64
import json
import os
from datetime import date
from pathlib import Path
import sys
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

root = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
state = json.loads((root / '.local/system-test-state.json').read_text())
config = dotenv_values(root / 'backend/.env')
test_db = make_url(state['database_url']).database
assert test_db != make_url(config['DATABASE_URL']).database
assert test_db.startswith('utility_system_') and test_db.endswith('_test')
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['serve', 'exercise'])
parser.add_argument('--model', default=None)
args = parser.parse_args()
action = args.action
if action == 'serve':
    os.environ.update({k:v for k,v in config.items() if v is not None})
    if args.model:
        os.environ['GEMINI_MODEL'] = args.model
    os.environ.update(DATABASE_URL=state['database_url'], JWT_SECRET=state['jwt_secret'],
        APP_ENV='test', LLM_PROVIDER='gemini', FRONTEND_URL='http://127.0.0.1:3110',
        REFRESH_COOKIE_NAME='utility_multimodal_refresh', RATE_LIMIT_ENABLED='false')
    sys.path.insert(0, str(root / 'backend'))
    os.chdir(root / 'backend')
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=8110)
else:
    import httpx
    from PIL import Image, ImageDraw, ImageFont
    from sqlalchemy import create_engine, text
    fixture = {'email':'vision-' + uuid4().hex[:12] + '@example.com', 'password':'SystemTestOnly2026!'}
    with httpx.Client(base_url='http://127.0.0.1:8110/api', timeout=150) as client:
        def call(method, path, data=None, expected=200):
            response = client.request(method, path, json=data)
            if response.status_code != expected:
                body = response.json()
                error = body.get('error', body)
                print('HTTP acceptance stopped:', response.status_code, str(error)[:400])
                raise SystemExit(1)
            return response.json()
        call('POST','/auth/register',{**fixture,'full_name':'Multimodal Test'},201)
        auth = call('POST','/auth/login',fixture)
        client.headers['Authorization'] = 'Bearer ' + auth['access_token']
        call('POST','/households',{'name':'Gemini image acceptance','province':state['account']['province'],
            'accounts':[{**state['account'],'customer_code':'PD12345678','initial_reading':'100'}]},201)
        meter = call('GET','/meters')[0]
        now = date.today()
        day = date(now.year - (now.month == 1), 12 if now.month == 1 else now.month-1, 1)
        recorded = call('POST','/readings',{'meter_id':meter['id'],'year':day.year,'month':day.month,
            'reading_date':str(day),'current_reading':'150'},201)
        image = Image.new('RGB',(1000,900),'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
        lines = ['HOA DON TIEN DIEN / ELECTRICITY BILL', 'TEST FIXTURE - NOT A REAL INVOICE',
            'Provider: ' + state['account']['provider_name'], 'Ma KH / Customer code: PD12345678',
            f'Ky / Billing period: {day.month:02}/{day.year}', 'Chi so cu / Previous reading: 100',
            'Chi so moi / Current reading: 150', 'San luong / Consumption: 50 kWh',
            'Tong tien / Total amount: ' + str(recorded['bill']['final_amount']) + ' VND']
        for index,line in enumerate(lines): draw.text((35,40+index*75),line,font=font,fill='black')
        path = root / '.local/multimodal-test-invoice.png'
        image.save(path)
        fixture.update(image_path=str(path),database=test_db,period=day.strftime('%Y-%m'))
        (root / '.local/multimodal-browser-state.json').write_text(json.dumps(fixture),encoding='utf-8')
        encoded = 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()
        engine = create_engine(state['database_url'])
        def counts():
            with engine.connect() as connection:
                return [connection.execute(text('SELECT count(*) FROM '+table)).scalar_one() for table in ('meter_readings','bills','payments')]
        before = counts()
        result = call('POST','/ai/chat',{'message':'Đối chiếu chỉ số mới trên hóa đơn này với bản ghi của tôi.', 'image_base64':encoded})
        structured = result['metadata']['result']
        assert result['metadata']['provider'] == 'gemini'
        assert structured['extracted_data']['current_reading'] in ('150','150.0','150.000')
        assert structured['verification']['reading']['status'] == 'MATCH'
        conversation = result['metadata']['conversation_id']
        follow = call('POST','/ai/chat',{'message':'Ảnh đó ghi bao nhiêu kWh?', 'conversation_id':conversation})
        assert follow['metadata']['result']['extracted_data'] == structured['extracted_data']
        outside = call('POST','/ai/chat',{'message':'Hãy viết giúp tôi một chương trình chơi cờ vua.'})
        assert outside['status'] == 'OUT_OF_SCOPE'
        assert counts() == before
        engine.dispose()
        (root / '.local/multimodal-live-result.json').write_text(json.dumps({'image':result,'followup':follow,'outside':outside},ensure_ascii=False),encoding='utf-8')
        print('PASS: REAL Gemini image extraction -> backend verification -> natural answer -> follow-up -> scope rejection; business rows unchanged.')
        print('Browser fixture email:',fixture['email'])
