import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from database.logger import init_db, write_log, read_logs
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--init', action='store_true')
parser.add_argument('--write', action='store_true')
parser.add_argument('--level', default='INFO')
parser.add_argument('--source', default=None)
parser.add_argument('--message', default='test')
parser.add_argument('--meta', default='')
parser.add_argument('--read', action='store_true')
parser.add_argument('--limit', type=int, default=50)
args = parser.parse_args()

if args.init:
    init_db()
    print('DB initialized')

if args.write:
    write_log(datetime.utcnow().isoformat(), args.level, args.source, args.message, {'meta': args.meta})
    print('Log written')

if args.read:
    logs = read_logs(args.limit)
    for l in logs:
        print(l)
