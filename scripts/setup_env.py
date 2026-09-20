"""Create local secrets once; never overwrite an existing environment file."""
from pathlib import Path
import secrets
root=Path(__file__).resolve().parents[1]
root_env=root/'.env'
if not root_env.exists():
    root_env.write_text(f'POSTGRES_PASSWORD={secrets.token_hex(24)}\nJWT_SECRET={secrets.token_hex(48)}\n',encoding='utf-8')
values=dict(line.split('=',1) for line in root_env.read_text().splitlines() if '=' in line and not line.startswith('#'))
backend=root/'backend/.env'
if not backend.exists():
    backend.write_text(f"DATABASE_URL=postgresql+psycopg://utility:{values['POSTGRES_PASSWORD']}@localhost:5432/utility\nJWT_SECRET={values['JWT_SECRET']}\nJWT_ALGORITHM=HS256\nACCESS_TOKEN_EXPIRE_MINUTES=30\nREFRESH_TOKEN_EXPIRE_DAYS=7\nLLM_PROVIDER=deterministic\nLLM_API_KEY=\nAPP_ENV=development\nFRONTEND_URL=http://localhost:3000\n",encoding='utf-8')
frontend=root/'frontend/.env.local'
if not frontend.exists(): frontend.write_text('NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api\n',encoding='utf-8')
print('Local environment files ready; secrets were not printed.')
