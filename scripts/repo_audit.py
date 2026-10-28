"""Fail on secrets/runtime artifacts in the proposed Git source set; redact all matches."""
import re,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
raw=subprocess.check_output(['git','-c','safe.directory='+str(root).replace('\\','/'),'ls-files','-c','-o','--exclude-standard','-z'],cwd=root)
paths=sorted(set(p for p in raw.decode().split('\0') if p))
bad=[]
blocked={'.local','node_modules','.next','.venv','__pycache__','.pytest_cache','.agents','.codex','.claude','.impeccable'}
for name in paths:
    path=root/name
    if blocked.intersection(Path(name).parts) or (Path(name).name.startswith('.env') and not name.endswith('.env.example')):
        bad.append((name,'local/generated file'));continue
    if not path.is_file() or path.stat().st_size>2_000_000:continue
    try:content=path.read_text(encoding='utf-8')
    except (UnicodeError,OSError):continue
    if re.search(r'(?:AIza|AQ\.)[0-9A-Za-z_-]{30,}',content) or re.search(r'gh[pousr]_[A-Za-z0-9]{30,}',content) or re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',content):
        bad.append((name,'credential pattern (redacted)'))
for name,reason in bad:print(name+': '+reason)
print(f'Audited {len(paths)} source paths; {len(bad)} blocking findings. No secret values displayed.')
sys.exit(bool(bad))
