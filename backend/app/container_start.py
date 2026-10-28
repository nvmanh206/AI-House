"""Docker-only startup; no host Python, env files or machine-specific paths required."""
import os,secrets,subprocess,sys
from pathlib import Path

def main():
    if not os.environ.get('JWT_SECRET'):
        path=Path('/app/runtime/jwt-secret');path.parent.mkdir(parents=True,exist_ok=True)
        try:
            descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'w') as stream:stream.write(secrets.token_urlsafe(48))
        except FileExistsError:pass
        os.environ['JWT_SECRET']=path.read_text().strip()
    mode=sys.argv[1] if len(sys.argv)>1 else 'serve'
    if mode=='serve':
        subprocess.run([sys.executable,'-m','alembic','upgrade','head'],check=True)
        from app.bootstrap import initialize
        initialize()
        os.execvp('uvicorn',['uvicorn','app.main:app','--host','0.0.0.0','--port','8000'])
    if mode=='scheduler':os.execv(sys.executable,[sys.executable,'-m','app.scheduler'])
    if mode=='seed':os.execv(sys.executable,[sys.executable,'-m','app.seed','--demo'])
    raise SystemExit('Unknown container mode')

if __name__=='__main__':main()
