import os
import json

if not os.path.isdir('data'):
    os.mkdir('data')

with open('data/available.json', 'w') as f:
    json.dump({}, f)

with open('data/in_progress.json', 'w') as f:
    json.dump({}, f)

info = {
    'teachers': ['应梦娴', '田薇', '梁羡飞', '李娜'],
    'time_format': '%Y 年 %m 月 %d 日  （%A）',
    'work_start': [9, 10, 14, 15, 16],
    'work_hours': '{0:02d}:00 ~ {0:02d}:50',
    'max_capacity': 1
}

with open('data/settings.json', 'w') as f:
    json.dump(info, f)
