"""Additional REAL Gemini acceptance cases using generated disposable images."""
import base64
import json
from pathlib import Path
import sys

import httpx
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parents[1]
state = json.loads((root / '.local/system-test-state.json').read_text())
fixture = json.loads((root / '.local/multimodal-browser-state.json').read_text())
database = make_url(state['database_url']).database
assert database.startswith('utility_system_') and database.endswith('_test')
image = Image.open(root / '.local/multimodal-test-invoice.png').convert('RGB')
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
foreign = image.copy()
draw = ImageDraw.Draw(foreign)
draw.rectangle((0,260,1000,325),fill='white')
draw.text((35,265),'Ma KH / Customer code: PD00000000',font=font,fill='black')
other = Image.new('RGB',(800,500),'white')
ImageDraw.Draw(other).text((40,100),'MEETING AGENDA\nProject meeting at 9 AM',font=font,fill='black')
water = Image.new('RGB',(900,700),'white')
ImageDraw.Draw(water).multiline_text((35,40),f'WATER BILL - TEST FIXTURE\nCustomer code: W12345\nBilling period: {fixture["period"]}\nPrevious reading: 12\nCurrent reading: 15\nConsumption: 3 m³\nTotal amount: 10000 VND',font=font,fill='black',spacing=25)
cases = {
    'cropped': (image.crop((0,0,1000,400)), 'Đọc chỉ số mới trên ảnh giúp tôi.'),
    'blurred': (image.filter(ImageFilter.GaussianBlur(18)), 'Ảnh này đọc được chỉ số mới không? Đừng đoán nếu mờ.'),
    'not-invoice': (other, 'Đây có phải hóa đơn điện nước không?'),
    'foreign-account': (foreign, 'Đối chiếu chỉ số mới trên ảnh với dữ liệu tài khoản của tôi.'),
    'water': (water, 'Đối chiếu chỉ số nước trên ảnh với dữ liệu của tôi.'),
}
engine = create_engine(state['database_url'])
def counts():
    with engine.connect() as connection:
        return [connection.execute(text('SELECT count(*) FROM '+table)).scalar_one() for table in ('meter_readings','bills','payments')]
before = counts()
results = {}
with httpx.Client(base_url='http://127.0.0.1:8110/api',timeout=150) as client:
    auth = client.post('/auth/login',json={'email':fixture['email'],'password':fixture['password']})
    assert auth.status_code == 200
    client.headers['Authorization'] = 'Bearer ' + auth.json()['access_token']
    for name,(picture,message) in cases.items():
        path = root / ('.local/multimodal-' + name + '.png')
        picture.save(path)
        response = client.post('/ai/chat',json={'message':message,'image_base64':'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()})
        assert response.status_code == 200, f'{name}: HTTP {response.status_code}'
        body = response.json()
        result = body['metadata']['result']
        if name in ('cropped','blurred'):
            assert result['extracted_data']['current_reading'] is None, name
        if name == 'not-invoice':
            assert result['extraction']['document_type'] in ('OTHER','UNKNOWN')
        if name == 'water':
            assert result['extraction']['document_type'] == 'WATER_BILL'
            assert result['extracted_data']['unit'] == 'm³'
        assert result['verification']['reading']['status'] == 'UNKNOWN', name
        results[name] = body
        print(name + ': PASS (' + body['status'] + ')',flush=True)
        (root / '.local/multimodal-live-variants.json').write_text(json.dumps(results,ensure_ascii=False),encoding='utf-8')
assert counts() == before
engine.dispose()
print('PASS: all variants use REAL Gemini; business records unchanged.')
