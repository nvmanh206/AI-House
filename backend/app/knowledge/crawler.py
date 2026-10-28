"""Bounded HTTPS downloads: validate and pin DNS on every redirect."""
import ipaddress
import socket
import time
import json
import re
from html import escape
from urllib.parse import urlsplit,urljoin
from urllib.robotparser import RobotFileParser
from io import BytesIO
import httpx
from bs4 import BeautifulSoup
from app.ai.get_new_evn_data import extract_article

USER_AGENT='NhaMinhKnowledge/1.0'
MAX_BYTES=10*1024*1024

def resolve(host,port):
    return list({row[4][0] for row in socket.getaddrinfo(host,port,type=socket.SOCK_STREAM)})

def validate_url(url,domains,resolver=resolve):
    parsed=urlsplit(url); host=parsed.hostname or ''
    if (parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443)
        or not any(host==d or host.endswith('.'+d) for d in domains)):
        raise ValueError('URL_NOT_ALLOWED')
    addresses=resolver(host,443)
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError('PRIVATE_ADDRESS_BLOCKED')
    return addresses

def download(url,domains):
    started=time.monotonic()
    with httpx.Client(timeout=httpx.Timeout(20,connect=8),trust_env=False) as client:
        for _ in range(6):
            ips=validate_url(url,domains); parsed=httpx.URL(url)
            with client.stream('GET',parsed.copy_with(host=ips[0]),headers={'Host':parsed.host,'User-Agent':USER_AGENT},
                extensions={'sni_hostname':parsed.host},follow_redirects=False) as response:
                if response.status_code in (301,302,303,307,308):
                    url=urljoin(url,response.headers['location']); continue
                response.raise_for_status(); body=bytearray()
                for block in response.iter_bytes():
                    body.extend(block)
                    if len(body)>MAX_BYTES: raise ValueError('DOCUMENT_TOO_LARGE')
                    if time.monotonic()-started>60: raise ValueError('DOWNLOAD_TIMEOUT')
                return bytes(body),response.headers.get('content-type',''),url
    raise ValueError('TOO_MANY_REDIRECTS')

class Crawler:
    def __init__(self,source): self.source=source; self.robots={}
    def fetch(self,url):
        root='https://'+urlsplit(url).netloc
        if root not in self.robots:
            try: data,_,_=download(root+'/robots.txt',self.source['domains'])
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code!=404: raise
                data=b''
            policy=RobotFileParser(); policy.parse(data.decode('utf-8',errors='replace').splitlines()); self.robots[root]=policy
        policy=self.robots[root]
        if not policy.can_fetch(USER_AGENT,url): raise ValueError('ROBOTS_DISALLOWED')
        delay=policy.crawl_delay(USER_AGENT) or policy.crawl_delay('*') or 1
        if delay>30: raise ValueError('CRAWL_DELAY_REQUIRES_REVIEW')
        time.sleep(max(1,delay))
        return download(url,self.source['domains'])

def inline_price_tables(soup):
    """Read literal EVN table data, never evaluate JavaScript or follow script URLs."""
    tables=[]
    quoted=r'"(?:[^"\\]|\\.)*"'
    def literal(raw):
        # Only JSON literals plus bare object keys/trailing commas are accepted.
        # Match strings first so their contents cannot be rewritten as syntax.
        raw=re.sub(quoted+r'|([A-Za-z_]\w*)\s*:',lambda m:m[0] if m[1] is None else json.dumps(m[1])+':',raw)
        raw=re.sub(quoted+r'|,(\s*[}\]])',lambda m:m[0] if m[1] is None else m[1],raw)
        return json.loads(raw)
    for script in soup.find_all('script',src=False):
        code=script.string or script.get_text()
        if len(code)>150000: continue
        for header in re.finditer(r'const\s+([A-Za-z]+)TableHeaders\s*=\s*(\[.*?\])\s*;',code,re.S):
            data=re.search(r'const\s+'+re.escape(header[1])+r'ElectricityData\s*=\s*(\[.*?\])\s*;',code,re.S)
            if not data: continue
            try:
                headings=literal(header[2]); groups=literal(data[1])
                if not isinstance(headings,list) or not 3<=len(headings)<=8 or not all(isinstance(h,str) for h in headings): continue
                if not isinstance(groups,list) or len(groups)>100: continue
                heads=[headings[-3],headings[-2],headings[-1]]
                heads=[BeautifulSoup(h,'html.parser').get_text(' ',strip=True) for h in heads]
                unit_hint = ' (đồng/kWh)' if 'kwh' in str(heads).lower() else ''
                rows=[]
                for group in groups:
                    if not isinstance(group,dict) or not isinstance(group.get('group'),str): raise ValueError()
                    values=group.get('values',[])
                    if not isinstance(values,list) or len(values)>100: raise ValueError()
                    for row in values:
                        if not isinstance(row,dict) or not isinstance(row.get('desc',''),str): raise ValueError()
                        prices=[row.get('oldPrice'),row.get('newPrice')]
                        if any(type(p) not in (int,float) or not 0<=p<=10**9 for p in prices): raise ValueError()
                        label=group['group']+' — '+row.get('desc','')+unit_hint
                        rows.append('<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in (label,*prices))+'</tr>')
                if rows: tables.append('<table><thead><tr>'+''.join('<th>'+escape(h)+'</th>' for h in heads)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
            except (ValueError,TypeError,RecursionError): continue
    return tables


def extract(body,mime,*,fragment=None):
    if body.startswith(b'%PDF-'):
        from pypdf import PdfReader
        reader=PdfReader(BytesIO(body))
        if len(reader.pages)>150: raise ValueError('PDF_TOO_MANY_PAGES')
        blocks=[f'Trang {i+1}\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages)]
        return '\n'.join(blocks),blocks,'pdf'
    if 'html' not in mime.lower(): raise ValueError('UNSUPPORTED_DOCUMENT')
    soup=BeautifulSoup(body,'html.parser')
    generated=inline_price_tables(soup) if not fragment else []
    target=soup.find(id=fragment) if fragment else None
    if fragment and target is None: raise ValueError('DOCUMENT_SECTION_NOT_FOUND')
    for node in soup(['script','style','nav','footer','header','input']): node.decompose()
    for node in soup.find_all('button'):
        if node.find_parent(class_='accordion-item'): node.unwrap()
        else: node.decompose()
    for node in soup.find_all('form'): node.unwrap()
    article=(target.find_parent(class_='accordion-item') or target) if target else (soup.select_one('.chitiettinbai') or soup.find('article') or soup.find('main') or soup.body or soup)
    # Article precision filters drop FAQ lists, headings and tariff effective dates.
    # These explicit content containers exclude the surrounding login/navigation UI.
    sections=[article] if target else (soup.select('.news_detail_detail') or soup.select('.accordion-item') or soup.select('section.wp-section'))
    tables=[str(t) for section in (sections or [article]) for t in section.find_all('table')]
    text=('\n\n'.join(re.sub(r'\s+',' ',section.get_text(' ',strip=True)).strip() for section in sections) if sections else
          extract_article('<html><body>'+str(article)+'</body></html>'))
    if generated:
        text+='\n\n'+'\n\n'.join(BeautifulSoup(t,'html.parser').get_text(' | ',strip=True) for t in generated)
    return text,[*text.split('\n\n'),*tables,*generated],'html'
