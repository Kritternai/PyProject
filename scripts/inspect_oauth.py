import os
import json
from pathlib import Path

def load_env_files():
    # check project root .env and app/.env
    cwd = Path.cwd()
    candidates = [cwd / '.env', cwd / 'app' / '.env']
    env = {}
    for p in candidates:
        if p.exists():
            try:
                text = p.read_text(encoding='utf-8')
                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
    return env

def main():
    print('=== Inspect OAuth config ===')
    env = load_env_files()
    print('Loaded from .env/app/.env (preview):')
    for k in ('GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET','PORT'):
        print(f'  {k}:', env.get(k))

    # Runtime env
    for k in ('GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET','PORT'):
        print(f'ENV {k}:', os.environ.get(k))

    # Check client_secrets.json in project root
    project_root = Path.cwd()
    secrets = project_root / 'client_secrets.json'
    print('client_secrets.json exists:', secrets.exists())
    if secrets.exists():
        try:
            data = json.loads(secrets.read_text(encoding='utf-8'))
            print('client_secrets keys:', list(data.keys()))
            for key in ('web','installed'):
                if key in data and 'redirect_uris' in data[key]:
                    print(f"redirect_uris in {key}:")
                    for u in data[key]['redirect_uris']:
                        print(' ', u)
        except Exception as e:
            print('failed to read client_secrets.json:', e)

    # If no file, show what a fallback Flow would use
    if not secrets.exists():
        cid = os.environ.get('GOOGLE_CLIENT_ID') or env.get('GOOGLE_CLIENT_ID')
        csec = os.environ.get('GOOGLE_CLIENT_SECRET') or env.get('GOOGLE_CLIENT_SECRET')
        port = os.environ.get('PORT') or env.get('PORT') or '5004'
        print('Fallback client_id:', cid)
        print('Fallback redirect_uri:', f'http://localhost:{port}/auth/google/callback')

if __name__ == '__main__':
    main()
