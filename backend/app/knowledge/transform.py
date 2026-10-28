import unicodedata
from datetime import date

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')

def chunks(blocks, size=2400, overlap=320):
    result, current = [], ''
    for block in blocks:
        block=block.strip()
        if not block: continue
        if '<table' in block:
            if current: result.append(current)
            result.append(block); current=''; continue
        while len(block)>size:
            cut=block.rfind(' ',0,size)
            cut=cut if cut>size//2 else size
            if current: result.append(current); current=''
            result.append(block[:cut]); block=block[max(1,cut-overlap):]
        if len(current)+len(block)>size:
            result.append(current); current=current[-overlap:]+'\n'
        current+=block+'\n'
    if current.strip(): result.append(current.strip())
    return result

def publication(topic, metadata, content):
    if not content.strip(): return 'PENDING_REVIEW'
    blocking = [c for c in metadata.get('conflicts', []) if c not in ('PRICE_FACTS_UNVERIFIED', 'PRICE_SOURCE_STALE')]
    if blocking: return 'PENDING_REVIEW'
    if topic not in ('PRICES','GUIDANCE','REGULATIONS'): return 'PENDING_REVIEW'
    if topic=='PRICES':
        try: date.fromisoformat(metadata.get('effective_from') or '')
        except ValueError: return 'PENDING_REVIEW'
        if not metadata.get('scope'): return 'PENDING_REVIEW'
    return 'PUBLISHED'

def fuse(keyword, dense, limit=8):
    scores,rows={},{}
    for results in (keyword,dense):
        for rank,row in enumerate(results,1):
            key=str(row['id']); rows[key]=row; scores[key]=scores.get(key,0)+1/(60+rank)
    return [dict(rows[key],score=score) for key,score in sorted(scores.items(),key=lambda item:-item[1])[:limit]]
