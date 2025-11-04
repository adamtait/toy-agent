import os
import json
from datetime import datetime

LOGS_DIR = 'logs'
LOG_FILE = os.path.join(LOGS_DIR, f"{datetime.now().isoformat()}.log")

def setup_logging():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def log(data):
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(data, indent=2))
        f.write('\n---\n')
