import json

null = {}
with open('available.json', 'w') as f:
    json.dump(null, f)

with open('in_progress.json', 'w') as f:
    json.dump(null, f)

info = {
    'teachers': ['应梦娴', '田薇', '梁羡飞', '李娜'],
    'time_format': '%Y 年 %m 月 %d 日  (%A)',
    'work_start': [9, 10, 14, 15, 16],
    'work_hours': '{0:02d}:00 - {0:02d}:50'
}

with open('settings.json', 'w') as f:
    json.dump(info, f)
