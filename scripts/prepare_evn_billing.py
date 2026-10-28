"""Prepare a reviewed tariff catalog from live official data, not embedded rate constants."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'backend'))
from app.knowledge.crawler import Crawler
from app.tariff_import import residential_tiers
url='https://cskh.evnspc.vn/TraCuu/ThongTinGiaDien'
body,_,final=Crawler({'domains':['evnspc.vn']}).fetch(url)
tiers,heading=residential_tiers(body)
if '1279' not in heading:raise SystemExit('Source decision changed; review before import.')
source={'url':final,'decision':'1279/QĐ-BCT','effective_from':'2025-05-10',
 'effective_source_url':'https://xaydungchinhsach.chinhphu.vn/chi-tiet-gia-ban-le-dien-sinh-hoat-gia-ban-buon-dien-tu-10-5-11925051008285612.htm',
 'checked_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(body).hexdigest(),
 'heading':heading,'tax_included':False,'scope':'NATIONAL','unit':'VND/kWh'}
directory=root/'.local/knowledge';directory.mkdir(parents=True,exist_ok=True)
(directory/'evn-billing-original.html').write_bytes(body)
(directory/'evn-billing-verified.json').write_text(json.dumps({'source':source,'tiers':tiers},ensure_ascii=False),encoding='utf-8')
print('Prepared live official residential catalog:',len(tiers),'tiers; no business data changed.')
