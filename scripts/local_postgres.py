"""Project-local Windows PostgreSQL runner. Requires EDB binaries in .local/pgsql.

No system service, no Docker changes, loopback binding, SCRAM password authentication.
"""
from pathlib import Path
import subprocess,os,argparse
root=Path(__file__).resolve().parents[1]
local=root/'.local';binary=local/'pgsql/bin';data=local/'pgdata'
values=dict(line.split('=',1) for line in (root/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
parser=argparse.ArgumentParser();parser.add_argument('action',choices=['start','stop','status']);args=parser.parse_args()
env={**os.environ,'PGPASSWORD':values['POSTGRES_PASSWORD']}
def run(name,*arguments,check=True):
    return subprocess.run([str(binary/(name+'.exe')),*map(str,arguments)],env=env,check=check,creationflags=subprocess.CREATE_NO_WINDOW)
if args.action=='stop':
    run('pg_ctl','-D',data,'-m','fast','-w','stop')
elif args.action=='status':
    run('pg_ctl','-D',data,'status')
else:
    if not (data/'PG_VERSION').exists():
        password_file=local/'pg-init-password'
        password_file.write_text(values['POSTGRES_PASSWORD'],encoding='utf-8')
        try: run('initdb','-D',data,'-U','utility','--auth=scram-sha-256','--encoding=UTF8','--locale=C','--pwfile',password_file)
        finally: password_file.unlink(missing_ok=True)
        with (data/'postgresql.conf').open('a') as f:
            f.write("\nlisten_addresses = '127.0.0.1'\nport = 5433\ntimezone = 'Asia/Ho_Chi_Minh'\n")
    status=run('pg_ctl','-D',data,'status',check=False)
    if status.returncode:
        run('pg_ctl','-D',data,'-l',local/'postgres.log','-w','start')
    for name in ('utility','utility_test'):
        result=subprocess.run([str(binary/'psql.exe'),'-h','127.0.0.1','-p','5433','-U','utility','-d','postgres','-tAc',f"SELECT 1 FROM pg_database WHERE datname='{name}'"],env=env,check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.stdout.strip()!='1': run('createdb','-h','127.0.0.1','-p','5433','-U','utility',name)
    print('PostgreSQL ready on 127.0.0.1:5433; databases utility and utility_test.')
