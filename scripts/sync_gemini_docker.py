"""Export only Gemini configuration to ignored Docker env file; never print values."""
import json
from pathlib import Path
from dotenv import dotenv_values
root=Path(__file__).resolve().parents[1]
source=dotenv_values(root/'backend/.env')
allowed=('LLM_PROVIDER','GEMINI_API_KEY','GEMINI_MODEL','GEMINI_SEARCH_ENABLED','GEMINI_TIMEOUT_SECONDS','GEMINI_REPLY_TOKENS','GEMINI_QUOTA_GUARD_ENABLED','GEMINI_REQUESTS_PER_MINUTE')
if not source.get('GEMINI_API_KEY'):raise SystemExit('Gemini key missing; no configuration written.')
(root/'.local/gemini-backend.env').write_text('\n'.join(k+'='+json.dumps(source[k]) for k in allowed if source.get(k) is not None)+'\n',encoding='utf-8')
print('Wrote only allowlisted Gemini settings; no values displayed.')
