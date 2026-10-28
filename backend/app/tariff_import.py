"""Read actual EVN public residential table; rates are never application constants."""
import re
from decimal import Decimal
from bs4 import BeautifulSoup
from app.knowledge.crawler import inline_price_tables
from app.knowledge.transform import normalize

def residential_tiers(body):
    soup=BeautifulSoup(body,'html.parser')
    for html in inline_price_tables(soup):
        table=BeautifulSoup(html,'html.parser')
        rows=[];previous=0
        for row in table.select('tbody tr'):
            cells=[c.get_text(' ',strip=True) for c in row.find_all('td')]
            if len(cells)!=3:continue
            label=normalize(cells[0])
            if 'sinh hoat' not in label or not re.search(r'bac\s+\d+\s*:',label):continue
            limits=[int(n) for n in re.findall(r'\d+',label.split(':',1)[1])]
            if not limits or limits[0]!=(0 if not rows else previous+1):raise ValueError('Non-contiguous source table')
            upper=limits[-1] if len(limits)>1 else None
            price=Decimal(cells[-1])
            if price<0:raise ValueError('Invalid source amount')
            rows.append({'from_value':str(previous),'to_value':str(upper) if upper is not None else None,'unit_price':str(price)})
            previous=upper if upper is not None else previous
        if rows:
            if len(rows)<2 or rows[-1]['to_value'] is not None:raise ValueError('Incomplete source table')
            return rows,table.select('th')[-1].get_text(' ',strip=True)
    raise ValueError('No residential tariff table found')
