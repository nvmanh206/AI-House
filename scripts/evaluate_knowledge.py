"""50 human-authored retrieval cases tied to two official source documents.

This acceptance set measures retrieval, NOT nationwide knowledge coverage or
Gemini answer correctness. No answers from this fixture enter production prompts.
"""
import json,os,sys,time
from pathlib import Path
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
for k,v in dotenv_values(ROOT/'backend/.env').items():
    if v is not None: os.environ[k]=v
sys.path.insert(0,str(ROOT/'backend'))
from app.knowledge.service import retrieve,KnowledgeQuery
from app.knowledge.store import connection

VNEID='https://www.evn.com.vn/d/vi-VN/news/Chinh-thuc-trien-khai-12-dich-vu-cong-nganh-Dien-tren-ung-dung-VNeID-pham-vi-toan-quoc--60-134-510085'
SAFETY='https://www.evn.com.vn/d/vi-VN/news/Nhan-thong-bao-no-tien-dien-xac-minh-the-nao-60-134-509453'
services=[
 ('Cấp điện mới từ lưới điện hạ áp','Đăng ký cấp điện hạ áp có trong dịch vụ VNeID không?','Xin điện mới hạ áp qua VNeID được hỗ trợ chứ?'),
 ('Cấp điện mới từ lưới điện trung áp','VNeID có hỗ trợ cấp điện mới trung áp không?','Tôi muốn xin điện từ lưới trung áp bằng VNeID, có dịch vụ không?'),
 ('Thay đổi chủ thể hợp đồng','Có thể đổi chủ thể hợp đồng điện trên VNeID không?','Sang tên hợp đồng mua bán điện qua VNeID được không?'),
 ('Thay đổi mục đích sử dụng điện','Đổi mục đích dùng điện qua VNeID được không?','VNeID hỗ trợ thay đổi mục đích sử dụng điện chứ?'),
 ('Thay đổi định mức sử dụng điện','Định mức điện có thể thay đổi qua VNeID không?','Xin đổi định mức sử dụng điện trên VNeID có trong danh sách không?'),
 ('Gia hạn hợp đồng','VNeID có dịch vụ gia hạn hợp đồng điện không?','Tôi cần kéo dài hợp đồng mua bán điện trên VNeID, có hỗ trợ không?'),
 ('Chấm dứt hợp đồng','Chấm dứt hợp đồng điện qua VNeID được không?','VNeID có thể tiếp nhận việc kết thúc hợp đồng mua bán điện không?'),
 ('Thay đổi vị trí thiết bị đo đếm','VNeID có dịch vụ đổi vị trí thiết bị đo đếm không?','Muốn chuyển vị trí công tơ điện, VNeID có hỗ trợ dịch vụ này không?'),
 ('Thay đổi công suất sử dụng điện','Có thể đăng ký thay đổi công suất điện trên VNeID không?','VNeID có hỗ trợ điều chỉnh công suất sử dụng điện chứ?'),
 ('Thay đổi thông tin đã đăng ký','Sửa thông tin hợp đồng điện đã đăng ký qua VNeID được không?','VNeID có mục thay đổi thông tin trên hợp đồng mua bán điện không?'),
 ('Ngừng cấp điện theo yêu cầu','Có dịch vụ ngừng cấp điện theo yêu cầu trên VNeID không?','Tôi muốn tạm ngừng cấp điện qua VNeID, có hỗ trợ không?'),
 ('Cấp điện trở lại theo yêu cầu','Có thể yêu cầu cấp điện trở lại qua VNeID không?','VNeID có dịch vụ khôi phục cấp điện theo yêu cầu không?'),
]
safety=[
 ('không nên gọi lại số điện thoại','Nhận tin nhắn nợ tiền điện lạ, có nên gọi lại số trong tin không?','Muốn xác minh nợ tiền điện có nên gọi số người gửi tin lạ không?'),
 ('quét mã QR','Có nên quét mã QR trong thông báo nợ điện chưa xác minh không?','Người lạ báo nợ tiền điện gửi QR, tôi nên xử lý thế nào?'),
 ('không chuyển tiền, cung cấp mã OTP','Người tự xưng điện lực đòi OTP để kiểm tra nợ điện, nên làm gì?','Có được gửi mã OTP cho người gọi báo nợ điện không?'),
 ('tải trực tiếp từ Google Play hoặc App Store','Tôi nên tải ứng dụng điện lực ở đâu để tránh giả mạo?','Nguồn cài ứng dụng EVN CSKH nào được hướng dẫn để tránh lừa đảo?'),
 ('chọn đúng mã khách hàng hoặc hợp đồng điện đã liên kết','Trong EVN CSKH phải chọn gì để xem đúng hóa đơn của mình?','Làm sao kiểm tra đúng hợp đồng và kỳ hóa đơn khi xác minh nợ điện?'),
 ('ngừng giao dịch ngân hàng','Đã cài app nghi giả mạo điện lực thì cần làm gì với giao dịch ngân hàng?','Sau khi nghi bị lừa qua app tiền điện, có nên tiếp tục giao dịch ngân hàng trên máy đó không?'),
 ('liên hệ ngay với ngân hàng','Nếu đã bấm link giả mạo điện lực thì cần liên hệ ngân hàng không?','Lỡ cài app báo nợ điện giả, nên liên hệ ai để bảo vệ tài khoản ngân hàng?'),
 ('trình báo cơ quan công an','Bị lừa qua thông báo nợ điện cần giữ chứng cứ để báo ai?','Tin nhắn giả mạo điện lực và chứng từ giao dịch nên lưu để làm gì?'),
 ('trên thiết bị an toàn','Sau khi bị app điện lực giả kiểm soát máy, nên đổi PIN trên thiết bị nào?','Thiết lập lại mật khẩu sau lừa đảo tiền điện cần dùng thiết bị ra sao?'),
 ('đăng ký trích nợ tự động','Có cách thanh toán tiền điện nào giảm nguy cơ quên trả hàng tháng?','Bài hướng dẫn xác minh nợ điện nói gì về trích nợ ngân hàng tự động?'),
]
cases=[]
for quote,a,b in services:
    for question in (a,b): cases.append({'question':question,'url':VNEID,'quote':quote,'current_price':False,'utility':'ELECTRICITY'})
for quote,a,b in safety:
    for question in (a,b): cases.append({'question':question,'url':SAFETY,'quote':quote,'current_price':False,'utility':'ELECTRICITY'})
for location in ('Thái Nguyên','Hà Nội','Đà Nẵng','Hải Phòng','Cần Thơ','Huế'):
    cases.append({'question':'Giá nước sinh hoạt hiện hành tại '+location,'url':None,'quote':None,'current_price':True,'utility':'WATER','location':location})
assert len(cases)==50
with connection() as db:
    for case in cases:
        if case['url']:
            row=db.execute("SELECT v.content FROM documents d JOIN versions v ON d.active_version=v.id WHERE d.url=%s AND v.status='PUBLISHED'",(case['url'],)).fetchone()
            if not row or case['quote'] not in row['content']:
                raise SystemExit('Gold source absent/unpublished or quote changed; review fixture before evaluating.')
results=[]
for i,case in enumerate(cases,1):
    start=time.monotonic()
    answer=retrieve(KnowledgeQuery(needs_public_knowledge=True,query=case['question'],utility=case['utility'],
        location=case.get('location'),as_of=None,current_price=case['current_price']))
    hit=any(d['url']==case['url'] and case['quote'] in d['content'] for d in answer['documents'][:5]) if case['url'] else not answer['documents']
    results.append({'question':case['question'],'expected_url':case['url'],'hit_at_5':hit,'mode':answer['mode'],
                    'elapsed_ms':int((time.monotonic()-start)*1000),'retrieved_urls':[d['url'] for d in answer['documents'][:5]]})
    print(f'{i}/50: '+('PASS' if hit else 'MISS'),flush=True)
answerable=[r for r in results if r['expected_url']]
score=sum(r['hit_at_5'] for r in answerable)/len(answerable)
report={'total':50,'answerable':44,'hit_at_5':score,'unsupported_price_cases_passed':sum(r['hit_at_5'] for r in results if not r['expected_url']),
        'hybrid_cases':sum(r['mode']=='HYBRID' for r in results),'cases':results}
(ROOT/'.local/knowledge-evaluation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Retrieval hit@5:',round(score*100,1),'%; see .local/knowledge-evaluation.json')
raise SystemExit(0 if score>=.9 and all(r['hit_at_5'] for r in results if not r['expected_url']) and report['hybrid_cases']==50 else 1)
