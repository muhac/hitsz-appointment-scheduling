import os
import json
import hashlib

if not os.path.isdir('data'):
    os.mkdir('data')

with open('data/available.json', 'w') as f:
    json.dump({}, f)

with open('data/in_progress.json', 'w') as f:
    json.dump({}, f)

info = {
    'password': hashlib.md5("password".encode('utf-8')).hexdigest(),
    'teachers': ['应梦娴', '田薇', '梁羡飞', '李娜'],
    'time_format': '%Y 年 %m 月 %d 日 ・ %A',
    'work_start': [9, 10, 14, 15, 16],
    'work_hours': '{0:02d}:00 ~ {0:02d}:50',
    'max_capacity': 1,
    'max_days': 10,
    'sort_helper': '%Y 年 %m 月 %d 日 ・ %A%M:00 ~ %S:50'
}

with open('data/settings.json', 'w') as f:
    json.dump(info, f)
