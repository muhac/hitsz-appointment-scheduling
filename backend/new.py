import os
import json

if not os.path.isdir('data'):
    os.mkdir('data')

with open('data/schedules.json', 'w') as f:
    json.dump({}, f)

with open('data/tickets.json', 'w') as f:
    json.dump({}, f)

with open('data/tickets_closed.json', 'w') as f:
    json.dump({}, f)

settings = {
    'checkpoint_frequency': 600,                               # 数据备份频率（秒）
    'teachers': ['应梦娴', '田薇', '梁羡飞', '李娜'],              # 辅导员列表
    'date_format': '%Y 年 %m 月 %d 日 · %A',                     # 显示日期格式
    'work_start': [9, 10, 11, 14, 15, 16],                      # 每场开始时间
    'hour_format': '{:02d}:00 · 大约 30 分钟',                    # 每场持续时间
    'time_format': '%Y 年 %m 月 %d 日 · %A%H:00 · 大约 30 分钟',   # 拼接时间格式
    'work_days': ['周一', '周二', '周三', '周四', '周五'],          # 一般工作日
    'max_capacity': 1,                                          # 每个时间段最大预约人数
    'max_days': 15,                                             # 最远可预约天数
    'hour_before': 1,                                           # 至少提前预约小时数
    'ticket_format': '{:05d}@{}',                               # 工单ID格式
    'timestamp': '%Y-%m-%d %H:%M:%S',                           # 工单时间戳格式
    'must_fill': ['wx', 'id', 'name', 'sex', 'mobile', 'teacher', 'date', 'hour', 'detail'],  # 必填项
    'emails': {                                                 # 辅导员邮箱
        '应梦娴': '916720619@qq.com',
        '梁羡飞': '2695998275@qq.com',
        '田薇': '635661409@qq.com',
        '李娜': '2076505738@qq.com',
    },
    'languages': {                                              # 时间戳翻译
        'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'zh': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        'zh_cn': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    }
}

with open('data/settings.json', 'w') as f:
    json.dump(settings, f)

dynamic = {
    'work_days': [],  # 特殊工作日
    'off_days': [],  # 特殊休息日
    'blocked': []  # 封禁用户名单
}

with open('data/dynamic.json', 'w') as f:
    json.dump(dynamic, f)
