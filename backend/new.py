import os
import json

if not os.path.isdir('data'):
    os.mkdir('data')

with open('data/tickets_open.json', 'w') as f:
    json.dump({}, f)

with open('data/tickets_closed.json', 'w') as f:
    json.dump({}, f)

dynamic = {
    'off_days': [],  # 特殊休息日
    'blocked': []  # 封禁用户名单
}

with open('data/dynamic.json', 'w') as f:
    json.dump(dynamic, f)

# written in secrets.py
with open('data/settings.json', 'w') as f:
    json.dump({}, f)

# written in secrets.py
with open('data/secrets.json', 'w') as f:
    json.dump({}, f)
