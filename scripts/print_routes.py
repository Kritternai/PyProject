import sys
from pathlib import Path

# Ensure project root is on sys.path so 'app' import works
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app import create_app

app = create_app()

for rule in sorted(app.url_map.iter_rules(), key=lambda r: (str(r))):
    print(f"{rule} -> {rule.endpoint}")
import sys
import os
sys.path.insert(0, os.getcwd())
from app import create_app
app = create_app()
print('\n'.join(sorted([str(rule) + ' -> ' + rule.endpoint for rule in app.url_map.iter_rules()])))
