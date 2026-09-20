from pathlib import Path

def instructions(intent):
    base = Path(__file__).parent
    return '\n'.join(p.read_text(encoding='utf-8') for p in sorted((base / 'rules').glob('*.md'))) + '\n' + (base / 'skills' / intent / 'SKILL.md').read_text(encoding='utf-8')
