#!/usr/bin/env python3
from pathlib import Path
import shutil, zipfile, re, time, sys
root = Path('.').resolve()
stamp = int(time.time())
zip_name = root / f"whatsapp-medical-bot-github-ready-{stamp}.zip"
export_dir = root / f"github_ready_bot_{stamp}"
exclude_dirs = {'node_modules','sessions','auth','downloads','tmp','.cache','.git','.local','.config','.upm','.pythonlibs','.bin','__pycache__','.next','dist','build','coverage'}
exclude_files = {'.env','.replit','.DS_Store'}
exclude_suffixes = {'.bak','.old','.zip','.mp3','.mp4','.ogg','.wav','.pdf','.png','.jpg','.jpeg','.webp','.svg','.puml','.pyc','.log'}
text_exts = {'.js','.json','.md','.txt','.nix','.sh','.example','.yml','.yaml','.html','.css','.mjs','.cjs','.ts'}
print('Root:', root)
print('Cleaning old temporary export folders...')
for p in list(root.iterdir()):
    if p.name.startswith(('github_upload_export_','github_upload_clean_','github_ready_bot_','bot_github_export_')) and p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
export_dir.mkdir(parents=True, exist_ok=True)
def should_skip(path: Path) -> bool:
    try: parts = path.relative_to(root).parts
    except Exception: return True
    for part in parts:
        if part in exclude_dirs: return True
        if part.startswith(('github_upload_export_','github_upload_clean_','github_ready_bot_','bot_github_export_','sessions.old.','sessions.loggedout.')): return True
    if path.name in exclude_files: return True
    if path.name.startswith('.env.'): return True
    if path.suffix.lower() in exclude_suffixes: return True
    return False
print('Copying project files safely...')
for item in root.iterdir():
    if should_skip(item): continue
    dest = export_dir / item.name
    if item.is_dir():
        shutil.copytree(item, dest, ignore=lambda d,names:[n for n in names if should_skip(Path(d)/n)], dirs_exist_ok=True)
    else:
        shutil.copy2(item, dest)
print('Sanitizing accidental API keys/secrets...')
repls=[
    (re.compile(r'AIza[0-9A-Za-z_-]{20,}'),'REPLACE_WITH_YOUR_GEMINI_API_KEY'),
    (re.compile(r'sk-[A-Za-z0-9_-]{20,}'),'REPLACE_WITH_YOUR_API_KEY'),
    (re.compile(r'(GEMINI_API_KEY\s*=\s*")[^"]+(")'), r'\1\2'),
    (re.compile(r'(GOOGLE_API_KEY\s*=\s*")[^"]+(")'), r'\1\2'),
    (re.compile(r'(API_KEY\s*=\s*")[^"]+(")'), r'\1\2'),
    (re.compile(r'(TOKEN\s*=\s*")[^"]+(")'), r'\1\2'),
    (re.compile(r'(SECRET\s*=\s*")[^"]+(")'), r'\1\2'),
    (re.compile(r'(PASSWORD\s*=\s*")[^"]+(")'), r'\1\2'),
]
for file in export_dir.rglob('*'):
    if not file.is_file(): continue
    if file.suffix.lower() not in text_exts and file.name not in {'reconnect','package.json','package-lock.json','.gitignore'}: continue
    try: text=file.read_text(encoding='utf-8', errors='ignore')
    except Exception: continue
    orig=text
    for pat,rep in repls: text=pat.sub(rep,text)
    if text!=orig:
        file.write_text(text, encoding='utf-8')
        print('Sanitized:', file.relative_to(export_dir))
print('Writing support files...')
(export_dir/'.gitignore').write_text("""node_modules/
sessions/
auth/
downloads/
tmp/
.cache/
.local/
.config/
.bin/
.env
.env.*
.replit
*.bak
*.old
*.zip
*.mp3
*.mp4
*.ogg
*.wav
*.pdf
*.png
*.jpg
*.jpeg
*.webp
*.svg
*.puml
*.log
.DS_Store
""", encoding='utf-8')
(export_dir/'.env.example').write_text("""GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_TIMEOUT_MS=90000
GEMINI_AUTO_ON=true
PAGE_TIMEOUT_MS=180000
URDU_EXTRA_WAIT_MS=10000
BULK_PDF_CONCURRENCY=2
SELF_PING_MS=180000
RADIO_STREAM_URL=https://whmsonic.radio.gov.pk:7008/stream?type=http&nocache=12
RADIO_CHUNK_SECONDS=30
YT_USE_ARIA2=true
YT_FRAGMENTS=8
""", encoding='utf-8')
(export_dir/'.replit.example').write_text("""run = "npm start"
entrypoint = "index.js"

[env]
PUPPETEER_SKIP_DOWNLOAD = "true"
PAGE_TIMEOUT_MS = "180000"
URDU_EXTRA_WAIT_MS = "10000"
BULK_PDF_CONCURRENCY = "2"
SELF_PING_MS = "180000"
GEMINI_API_KEY = ""
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_TIMEOUT_MS = "90000"
GEMINI_AUTO_ON = "true"
RADIO_STREAM_URL = "https://whmsonic.radio.gov.pk:7008/stream?type=http&nocache=12"
RADIO_CHUNK_SECONDS = "30"
YT_USE_ARIA2 = "true"
YT_FRAGMENTS = "8"
""", encoding='utf-8')
readme=export_dir/'README.md'
if not readme.exists():
    readme.write_text("""# WhatsApp Medical Research Bot

Self-hosted WhatsApp medical research bot running on Replit / Node.js 20.

## Setup

```bash
npm install
npm start
```

Scan QR from WhatsApp Linked Devices.

## Environment

Copy `.env.example` or `.replit.example`. Do not commit real secrets.

## Reconnect

```bash
./reconnect
```
""", encoding='utf-8')
print('Final secret scan...')
hits=[]
for file in export_dir.rglob('*'):
    if not file.is_file(): continue
    try: text=file.read_text(encoding='utf-8', errors='ignore')
    except Exception: continue
    if re.search(r'AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9_-]{20,}|BEGIN PRIVATE KEY', text): hits.append(str(file.relative_to(export_dir)))
if hits:
    print('ERROR: possible real secret still found. ZIP not created.')
    print('\n'.join(' - '+h for h in hits))
    sys.exit(1)
print('Creating ZIP:', zip_name.name)
with zipfile.ZipFile(zip_name,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for file in export_dir.rglob('*'):
        if file.is_file(): z.write(file, file.relative_to(export_dir.parent))
size=zip_name.stat().st_size
if size<=1024: raise SystemExit('ERROR: ZIP too small')
print('\nDONE')
print('ZIP:', zip_name.name)
print('Size:', f'{size/1024:.1f} KB')
print('Download from Replit Files panel:', zip_name.name)
