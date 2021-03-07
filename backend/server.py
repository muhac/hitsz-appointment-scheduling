# Author: limuhan
# GitHub: bugstop
#   March 7, 2021

# TODO: statusCode

import os
import json
import time
import signal
import inspect
import logging
import requests
from typing import Any, Callable
from multiprocessing import Process
from datetime import datetime, timedelta

from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

DEBUG = False
path = os.path.dirname(inspect.getfile(inspect.currentframe()))

log_file = path + '/server.log'
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)

database = [
    'secrets.json',         # 储存敏感信息
    'settings.json',        # 储存基本设置
    'schedules.json',       # 储存预约余量
    'tickets.json',         # 储存进行中预约
    'tickets_closed.json',  # 储存已完成预约
    'dynamic.json',         # 储存动态规则
]

with open(path + '/data/secrets.json') as f_obj:
    secrets: dict = json.load(f_obj)
with open(path + '/data/settings.json') as f_obj:
    settings: dict = json.load(f_obj)
with open(path + '/data/schedules.json') as f_obj:
    schedule: dict = json.load(f_obj)
with open(path + '/data/tickets.json') as f_obj:
    appointments: dict = json.load(f_obj)
with open(path + '/data/tickets_closed.json') as f_obj:
    appointments_closed: dict = json.load(f_obj)
with open(path + '/data/dynamic.json') as f_obj:
    dynamic: dict = json.load(f_obj)

# 记录各项数据最近备份时间
database_modified = {data_file: time.time() for data_file in database}
logging.info(('Loaded data', settings, schedule,
              appointments, appointments_closed, dynamic))


class DataCheckException(Exception):
    """数据校验错误信息"""


def send_mail(receiver: str, title: str, content: str) -> None:
    """当有新预约时，向对应老师发送邮件"""
    try:
        server: str = secrets['mailSettings']['server']
        username: str = secrets['mailSettings']['username']
        password: str = secrets['mailSettings']['password']

        smtp = SMTP_SSL(server)
        smtp.set_debuglevel(0)
        smtp.ehlo(server)
        smtp.login(username, password)

        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = username
        msg['To'] = receiver

        smtp.sendmail(username, receiver, msg.as_string())
        smtp.quit()
    except Exception as e:
        logging.error(('send mail error:', e))


def time_shift(*args: Any, **kwargs: Any) -> datetime:
    """获取（经过偏移量后的）时间"""
    return datetime.now() + timedelta(*args, **kwargs)


def date_lang(date: str, lang: (str, str) = ('en', 'zh')) -> str:
    """时间戳中英互译"""
    languages: dict = settings['languages']
    source_words, target_words = languages[lang[0]], languages[lang[1]]
    for source_word, target_word in zip(source_words, target_words):
        date = date.replace(source_word, target_word)
    return date


def date_convert(date_format: str, lang: (str, str) = ('en', 'zh')) -> Callable:
    """辅助时间戳转换函数"""
    return lambda z: datetime.strptime(date_lang(z, lang), date_format)


def save_data(data: Any, filename: str, detail: str = ':)') -> None:
    """定时备份数据"""
    if time.time() - database_modified[filename] < settings['checkpoint_frequency']:
        logging.info(('update skipped:', filename, detail))
    else:
        logging.warning(('update DATABASE:', filename, detail))
        try:
            with open(path + '/data/' + filename, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            # 仅作为备份，实时数据全在内存
            logging.error(('save data error:', filename, e))


def construct_response(msg: dict) -> Any:
    """完成请求响应的构造"""
    response = make_response(jsonify(msg))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


app = Flask(__name__, )
CORS(app, resources=r'/*')  # 允许跨域请求


@app.route('/', methods=['GET'])
def index():
    """https://github.com/bugstop/hitsz-appointment-scheduling"""
    messages = {'statusCode': 200, 'GitHub': 'bugstop', 'copyright': 2021}
    return construct_response(messages)


@app.route('/user/id/', methods=['POST'])
def get_uid():
    """获得用户唯一微信ID"""
    code = request.json.get('code')
    url = 'https://api.weixin.qq.com/sns/jscode2session?' \
          'appid={}&secret={}&js_code={}&grant_type=authorization_code'. \
        format(secrets['AppID'], secrets['AppSecret'], code)

    for _ in range(3):
        try:
            user_id = requests.get(url, timeout=2).json()['openid']
        except Exception as e:
            logging.critical(('get uid error:', e))
        else:
            break  # 已取得用户ID
    else:
        user_id = None  # 超时

    messages = {'statusCode': 200 if user_id else 500, 'wx': user_id}
    logging.info(('user id:', messages))
    return construct_response(messages)


@app.route('/user/verify/', methods=['POST'])
def admin_verification():
    """验证管理员密码"""
    admin = secrets['password'] == request.json.get('password')
    messages = {'statusCode': 200 if admin else 500}
    return construct_response(messages)


@app.route('/plan/empty/', methods=['GET'])
def schedule_available():
    """展示可供预约的时间段"""

    def list_data(max_days: int = 14):
        """筛选展示的时间段并排序"""
        global schedule, dynamic

        time_format = date_convert(settings['date_format'], ('zh', 'en'))
        dates = sorted(list(schedule.keys()), key=lambda z: time_format(z))

        # 检测数据完整性：是否包含从当日起共[max_days]天
        if not dates or len(dates) != max_days or \
                time_format(dates[0]) < time_shift(days=-1) or \
                time_format(dates[-1]) < time_shift(days=max_days - 2):

            schedule_new = dict()
            for day in range(max_days):
                date = date_lang(time_shift(days=day).strftime(settings['date_format']))
                schedule_new[date] = dict()
                for start in settings['work_start']:
                    hour = settings['hour_format'].format(start)
                    exist = date in dates and hour in list(schedule[date].keys())  # 此时间段可能已有预约
                    schedule_new[date][hour] = schedule[date][hour] if exist else settings['max_capacity']

            schedule = schedule_new
            Process(target=save_data, args=(schedule, 'schedules.json')).start()

        # 按照时间顺序排序
        time_format = date_convert(settings['date_format'], ('zh', 'en'))
        date_show = sorted(list(schedule.keys()), key=lambda z: time_format(z))
        hour_show = sorted(list(schedule[date_show[0]].keys()), key=lambda z: int(z[:2]))

        # 筛选出工作日，并剔除已无剩余预约名额的日期
        date_show = [date for date in date_show if not any(off_day in date for off_day in dynamic['off_days'])
                     and any(work_day in date for work_day in settings['work_days'] + dynamic['work_days'])
                     and sum(schedule[date].values()) > 0]
        schedule_show = {date: schedule[date] for date in date_show}

        # 将当日早些时候的余量设为0
        time_format = date_convert(settings['time_format'], ('zh', 'en'))
        schedule_show[date_show[0]] = {hour: 0 if time_shift(hours=settings['hour_before']) > time_format(
            date_show[0] + hour) else schedule_show[date_show[0]][hour] for hour in hour_show}

        return schedule_show, date_show, hour_show

    try:
        available = list_data(settings['max_days'])
        messages = {
            'statusCode': 200,
            'date': available[1],
            'hour': available[2],
            'schedule': available[0],
            'teachers': settings['teachers']
        }
    except Exception as e:
        logging.error(('list schedule error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route('/plan/list/', methods=['POST'])
def show_reservations():
    """展示预约工单列表"""

    def list_data(user_filter: str, tag: str):
        """筛选展示的工单并排序"""
        global appointments, appointments_closed

        if tag not in ['open', 'closed']:
            raise DataCheckException('key check failed')

        # 工单展示按预约时间顺序由近及远。工单ID仅作为唯一标识符，并不参与排序
        appointments_selected = appointments if tag != 'closed' else appointments_closed
        time_format = date_convert(settings['time_format'], ('zh', 'en'))
        tickets = sorted(list(appointments_selected.keys()), key=lambda z: time_format(
            appointments_selected[z]['date'] + appointments_selected[z]['hour']), reverse=(tag == 'closed'))

        # 自动关闭今天之前的工单
        expired_appointments = list()
        time_format = date_convert(settings['date_format'], ('zh', 'en'))
        while tickets and tag == 'open' and time_format(appointments[tickets[0]]['date']) < time_shift(days=-1):
            ticket_id = tickets.pop(0)
            appointments[ticket_id]['status'] = 'closed'  # TODO: expired
            appointments_closed[ticket_id] = appointments[ticket_id]
            del appointments[ticket_id]
            expired_appointments.append(ticket_id)
        if expired_appointments:
            logging.info(('list:', 'close expired'))
            Process(target=save_data, args=(appointments, 'tickets.json', 'close expired')).start()
            Process(target=save_data, args=(appointments_closed, 'tickets_closed.json', expired_appointments)).start()

        # 对于普通用户筛选出本人的预约，管理员可以查看所有预约
        if user_filter != secrets['password']:
            tickets = [ticket for ticket in tickets if appointments_selected[ticket].get('wx') == user_filter]
        appointments_filtered = {ticket: appointments_selected[ticket] for ticket in tickets}

        return appointments_filtered, tickets

    try:
        username = request.json.get('user')
        ticket_status = request.json.get('tag')
        reservations = list_data(username, ticket_status)
        messages = {
            'statusCode': 200,
            'tickets': reservations[1],
            'reservations': reservations[0]
        }
    except Exception as e:
        logging.error(('list reservation error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route('/plan/new/', methods=['POST'])
def make_reservations():
    """预约心理咨询"""

    def write_data(ticket):
        """新增预约数据"""
        global schedule, appointments, dynamic

        # 验证数据完整性：是否留空、是否有余量、是否在黑名单
        if not all([ticket.get(item) for item in settings['must_fill']]) \
                or schedule[ticket['date']][ticket['hour']] < 1 \
                or ticket['wx'] in dynamic['blocked']:
            raise DataCheckException('data check failed')

        schedule[ticket['date']][ticket['hour']] -= 1
        Process(target=save_data, args=(schedule, 'schedules.json', 'new {} {} {} {}'.format(
            ticket['wx'], ticket['date'], ticket['hour'], ticket['teacher']))).start()

        # 工单唯一ID形式为：流水号@时间戳
        ticket_id = 0 if not appointments and not appointments_closed else max(map(
            int, (tid.split('@')[0] for tid in list(appointments) + list(appointments_closed))))
        new_ticket = settings['ticket_format'].format(ticket_id + 1, time_shift().strftime('%Y%m%d'))

        ticket['status'] = 'open'  # 工单状态：open进行中，close已完成
        ticket['timestamp'] = time_shift().strftime(settings['timestamp'])
        appointments[new_ticket] = ticket

        logging.info(('reserve:', 'write data'))
        Process(target=save_data, args=(appointments, 'tickets.json', '{} {} {} {}'.format(
            new_ticket, ticket['name'], ticket['date'].split('·')[0], ticket['hour'][:5]))).start()

        mail_receiver = settings['emails'][ticket['teacher']] \
            if ticket['name'] != '张三' else secrets['mailSettings']['maintainer']  # 测试账号
        mail_content = '{}老师，{}预约了 {}{} 的心理咨询。'.format(
            ticket['teacher'], '有同学', ticket['date'].split('·')[0], ticket['hour'][:5])
        Process(target=send_mail, args=(mail_receiver, '新的心理咨询预约', mail_content)).start()

    try:
        write_data(request.json)
        messages = {'statusCode': 200}
    except Exception as e:
        logging.error(('make reservation error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route('/plan/edit/', methods=['POST'])
def edit_reservations():
    """更改心理咨询预约工单的状态"""

    def edit_data(username, ticket_id, operation):
        """修改预约数据"""
        global schedule, appointments, appointments_closed

        # closed标注工单为已完成，cancel直接删除工单记录
        if operation not in ['closed', 'cancel']:
            raise DataCheckException('key check failed')

        # 对进行中的工单，本人和管理员有权限进行关闭或删除记录
        if appointments.get(ticket_id) and username in (appointments[ticket_id]['wx'], secrets['password']):
            date, hour = appointments[ticket_id]['date'], appointments[ticket_id]['hour']
            appointments[ticket_id]['status'] = operation

            if operation == 'closed':
                appointments_closed[ticket_id] = appointments[ticket_id]
                Process(target=save_data, args=(appointments_closed, 'tickets_closed.json',
                                                'close {}'.format(ticket_id))).start()

            if operation == 'cancel' and date in schedule and hour in schedule[date]:
                schedule[date][hour] += 1  # 删除后，可以恢复该时间段的预约人数
                Process(target=save_data, args=(schedule, 'schedules.json',
                                                'cancel {}'.format(ticket_id))).start()

            logging.info(('edit:', 'write data'))
            del appointments[ticket_id]
            Process(target=save_data, args=(appointments, 'tickets.json',
                                            'delete {}'.format(ticket_id))).start()

        # 对已完成的工单，只有管理员有权限删除
        elif operation == 'cancel' and appointments_closed.get(ticket_id) and username == secrets['password']:
            logging.info(('edit:', 'write data'))
            del appointments_closed[ticket_id]
            Process(target=save_data, args=(appointments_closed, 'tickets_closed.json',
                                            'delete {}'.format(ticket_id))).start()

        else:
            raise DataCheckException('permission denied')

    try:
        uid = request.json.get('user')  # 用户的唯一ID，管理员传密码
        tid = request.json.get('tid')   # 操作的工单ID
        op = request.json.get('op')     # 操作选项（closed，cancel）
        edit_data(uid, tid, op)
        messages = {'statusCode': 200}
    except Exception as e:
        logging.error(('edit reservation error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


if __name__ == '__main__':
    logging.info(('working directory:', path))
    # 由于Process.start没有join，需要处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    app.run(port=2333 if not DEBUG else 6666)
