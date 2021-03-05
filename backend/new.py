import os
import json
import hashlib

if not os.path.isdir('data'):
    os.mkdir('data')

with open('data/available.json', 'w') as f:
    json.dump({}, f)

with open('data/in_progress.json', 'w') as f:
    json.dump({}, f)

settings = {
    'password': hashlib.md5("000000".encode('utf-8')).hexdigest(),
    'teachers': ['应梦娴', '田薇', '梁羡飞', '李娜'],
    'time_format': '%Y 年 %m 月 %d 日 ・ %A',
    'work_start': [9, 10, 11, 14, 15, 16],
    'work_hours': '{:02d}:00 ~ {:02d}:30',
    'work_days': ['星期一', '星期二', '星期三', '星期四', '星期五'],
    'max_capacity': 1,
    'max_days': 10,
    'ticket_format': '{:05d}@{}',
    'timestamp': '%Y 年 %m 月 %d 日 %H 时 %M 分 %S 秒',
    'sort_helper': '%Y 年 %m 月 %d 日 ・ %A%M:00 ~ %S:50'
}

with open('data/settings.json', 'w') as f:
    json.dump(settings, f)

dynamic = {
    'work_days': ['2021 年 03 月 13 日', ],
    'off_days': ['2021 年 03 月 12 日', ],
    'blocked': []
}

with open('data/dynamic.json', 'w') as f:
    json.dump(dynamic, f)
