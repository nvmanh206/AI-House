import math
import re
import httpx
from app.config import settings
from app.security import DomainError

def embed(content,*,query=False):
    model=settings.knowledge_embedding_model; key=settings.gemini_api_key or settings.llm_api_key
    if not key or not re.fullmatch(r'[A-Za-z0-9._-]+',model):
        raise DomainError('EMBEDDING_CONFIG','Chưa cấu hình embedding hợp lệ.',503)
    instruction=('Retrieve electricity/water documents relevant to this query: ' if query else
                 'Represent this public electricity/water document for retrieval: ')
    try:
        r=httpx.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent',
            headers={'x-goog-api-key':key},json={'model':'models/'+model,'content':{'parts':[{'text':instruction+content}]},
            'outputDimensionality':768},timeout=30,follow_redirects=False)
        if r.status_code!=200: raise ValueError('PROVIDER_ERROR')
        values=r.json()['embedding']['values']
        if len(values)!=768 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in values): raise ValueError('INVALID_VECTOR')
        return values
    except (httpx.HTTPError,ValueError,KeyError,TypeError):
        raise DomainError('EMBEDDING_UNAVAILABLE','Dịch vụ embedding chưa khả dụng; kiểm tra model và quota.',503) from None

def literal(values): return '['+','.join(str(float(v)) for v in values)+']'
