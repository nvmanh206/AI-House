"""Preserve current Docker credentials locally before adopting portable defaults."""
import json,subprocess
from pathlib import Path
from dotenv import dotenv_values
from sqlalchemy.engine import make_url
root=Path(__file__).resolve().parents[1]
raw=subprocess.run(['docker','inspect','nha-minh-backend'],capture_output=True,text=True,check=True)
values=dict(line.split('=',1) for line in json.loads(raw.stdout)[0]['Config']['Env'] if '=' in line)
target=root/'.env';existing=dotenv_values(target) if target.exists() else {}
allowed=('GEMINI_API_KEY','GEMINI_MODEL','GEMINI_SEARCH_ENABLED','GEMINI_REPLY_TOKENS','GEMINI_REQUESTS_PER_MINUTE','GEMINI_QUOTA_GUARD_ENABLED')
preserved={k:values[k] for k in allowed if k in values}
preserved.update(POSTGRES_PASSWORD=make_url(values['DATABASE_URL']).password,JWT_SECRET=values['JWT_SECRET'])
preserved['KNOWLEDGE_POSTGRES_PASSWORD']=make_url(values['KNOWLEDGE_DATABASE_URL']).password
password=root/'.local/pgadmin-admin-password'
if password.is_file():preserved['PGADMIN_PASSWORD']=password.read_text().strip()
existing.update(preserved)
target.write_text('\n'.join(k+'='+json.dumps(v) for k,v in existing.items() if v is not None)+'\n',encoding='utf-8')
print('Preserved existing Docker settings in ignored root .env; no values displayed.')
