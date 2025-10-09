import sys
import os
sys.path.insert(0, os.getcwd())
from app import create_app
app = create_app()
print('\n'.join(sorted([str(rule) + ' -> ' + rule.endpoint for rule in app.url_map.iter_rules()])))
