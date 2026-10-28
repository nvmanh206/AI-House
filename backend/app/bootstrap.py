"""Idempotent infrastructure/public-catalog initialization; no demo household data."""
import json
from pathlib import Path
from uuid import uuid4
from psycopg.types.json import Jsonb
from app.db import SessionLocal
from app.repository import Repository
from app.models import Tariff,TariffTier,AuditLog
from app.schemas import TariffInput
from app.knowledge.store import migrate,connection

def initialize():
    migrate()
    with connection() as db:
        db.execute('SELECT pg_advisory_xact_lock(7410830)')
        for name,domain,url,topic,utility,area in [
            ('EVNSPC · Bảng giá điện công khai','evnspc.vn','https://cskh.evnspc.vn/TraCuu/ThongTinGiaDien','PRICES','ELECTRICITY',None),
            ('EVN · Hướng dẫn','evn.com.vn','https://www.evn.com.vn/vi-VN/news-l/Tin-tuc-60-12','GUIDANCE','ELECTRICITY',None),
            ('SAWACO · Giá nước và hỏi đáp','sawaco.com.vn','https://cskh.sawaco.com.vn/ho_tro/hoi_dap','PRICES','WATER','Hồ Chí Minh'),
            ('HAWACOM · Giá nước Hà Nội','hawacom.vn','https://www.hawacom.vn/thong-tin-gia-nuoc','PRICES','WATER','Hà Nội'),
            ('SAWACO · Hướng dẫn dịch vụ trực tuyến','sawaco.com.vn','https://sawaco.com.vn/post-detail/nganh-cap-nuoc-day-manh-chuyen-doi-so-trong-cham-soc-khach-hang-260707104643','GUIDANCE','WATER','Hồ Chí Minh'),
            ('SAWACO · Hỏi đáp công tơ và dịch vụ nước','sawaco.com.vn',[
                'https://cskh.sawaco.com.vn/ho_tro/hoi_dap#collapsePricing3',
                'https://cskh.sawaco.com.vn/ho_tro/hoi_dap#collapsePricing11',
                'https://cskh.sawaco.com.vn/ho_tro/hoi_dap#collapsePricing12',
                'https://cskh.sawaco.com.vn/ho_tro/hoi_dap#collapsePricing19'],'GUIDANCE','WATER','Hồ Chí Minh'),
            ('Nước sạch Thái Nguyên · Giá nước','nuocsachthainguyen.vn','https://nuocsachthainguyen.vn/Content.aspx?tab=news&lang=vi&pid=1&cid=1&id=6778','PRICES','WATER','Thái Nguyên')]:
            if not db.execute('SELECT id FROM sources WHERE name=%s',(name,)).fetchone():
                db.execute('INSERT INTO sources(id,name,domains,seeds,topic,interval_hours,seed_mode,utility,service_area) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (uuid4(),name,Jsonb([domain]),Jsonb([url] if isinstance(url,str) else url),topic,6 if topic=='PRICES' else 24,'DOCUMENT' if topic=='PRICES' or utility=='WATER' else 'LISTING',utility,area))
    catalog=json.loads((Path(__file__).parents[1]/'data/tariffs/evn-residential-1279-2025.json').read_text(encoding='utf-8'))
    source=catalog['source']
    data=TariffInput(utility_type='ELECTRICITY',provider_name='EVN',name='EVN sinh hoạt - '+source['decision'],version='1279-2025-verified',
        tariff_category='RESIDENTIAL_1PHASE',province=None,effective_from=source['effective_from'],tiers=catalog['tiers'])
    with SessionLocal.begin() as db:
        repo=Repository(db)
        if not repo.one(Tariff,utility_type=data.utility_type,provider_name=data.provider_name,tariff_category=data.tariff_category,version=data.version):
            tariff=repo.add(Tariff,**data.model_dump(exclude={'tiers'}))
            for i,tier in enumerate(data.tiers):repo.add(TariffTier,tariff_id=tariff.id,order_index=i,**tier.model_dump())
            repo.add(AuditLog,user_id=None,household_id=None,action='VERIFY_TARIFF_SOURCE',entity_type='tariffs',entity_id=tariff.id,details=source)
    print('Database schemas, registered sources and versioned public tariff ready; no demo users/readings created.',flush=True)
