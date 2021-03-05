import os
import json

if not os.path.isdir('data'):
    os.mkdir('data')

with open('data/schedules.json', 'w') as f:
    json.dump({}, f)

with open('data/tickets.json', 'w') as f:
    json.dump({}, f)

settings = {
    'teachers': ['应梦娴', '田薇', '梁羡飞', '李娜'],
    'time_format': '%Y 年 %m 月 %d 日 ・ %A',
    'work_start': [9, 10, 11, 14, 15, 16],
    'work_hours': '{:02d}:00 ~ {:02d}:30',
    'work_days': ['星期一', '星期二', '星期三', '星期四', '星期五'],
    'max_capacity': 1,
    'max_days': 14,
    'hour_before': 1,
    'ticket_format': '{:05d}@{}',
    'timestamp': '%Y 年 %m 月 %d 日 %H 时 %M 分 %S 秒',
    'sort_helper': '%Y 年 %m 月 %d 日 ・ %A%H:00 ~ %M:30',
    'questionnaire': ['wx', 'id', 'name', 'sex', 'mobile', 'teacher', 'date', 'hour', 'detail'],
    'languages': {
        'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'zh': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    }
}

with open('data/settings.json', 'w') as f:
    json.dump(settings, f)

dynamic = {
    'work_days': ['2021 年 03 月 06 日', '2021 年 03 月 13 日', ],
    'off_days': ['2021 年 03 月 12 日', ],
    'blocked': []
}

with open('data/dynamic.json', 'w') as f:
    json.dump(dynamic, f)
