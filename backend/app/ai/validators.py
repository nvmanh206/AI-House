import re
SENSITIVE = re.compile(r'password|secret|token|api.?key|database.?url|raw_text|customer_code',re.I)
def sanitize(value):
    if isinstance(value,dict): return {k:sanitize(v) for k,v in value.items() if not SENSITIVE.search(k)}
    if isinstance(value,list): return [sanitize(v) for v in value]
    if isinstance(value,str):
        value=re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+','[REDACTED]',value)
        value=re.sub(r'(?:postgres(?:ql)?|mysql)://\S+','[REDACTED]',value)
        value=re.sub(r'\bsk-[A-Za-z0-9_-]+','[REDACTED]',value)
        value=re.sub(r'(?i)(password|secret|token|api_key)\s*[:=]\s*\S+',r'\1=[REDACTED]',value)
    return value
