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
    'secrets.json',  # 储存敏感信息
    'settings.json',  # 储存基本设置
    'tickets_open.json',  # 储存进行中预约
    'tickets_closed.json',  # 储存已完成预约
    'dynamic.json',  # 储存动态规则
]

with open(path + '/data/secrets.json') as f_obj:
    secrets: dict = json.load(f_obj)
with open(path + '/data/settings.json') as f_obj:
    settings: dict = json.load(f_obj)
with open(path + '/data/tickets_open.json') as f_obj:
    tickets: dict = json.load(f_obj)
with open(path + '/data/tickets_closed.json') as f_obj:
    tickets_closed: dict = json.load(f_obj)
with open(path + '/data/dynamic.json') as f_obj:
    dynamic: dict = json.load(f_obj)

# 记录各项数据最近备份时间
database_modified = {data_file: time.time() for data_file in database}
logging.info(('Loaded data', settings, tickets, tickets_closed, dynamic))


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


def save_data(data: Any, filename: str, detail: str = ':)', force: bool = False) -> None:
    """备份数据"""
    if not force and time.time() - database_modified[filename] < settings['checkpoint_frequency']:
        logging.info(('update skipped:', filename, detail))
    else:
        logging.warning(('update DATABASE:', filename, detail))
        try:
            with open(path + '/data/' + filename, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            # 仅作为备份，实时数据全在内存
            logging.error(('save data error:', filename, e))
        else:
            database_modified[filename] = time.time()


def checkpoint(msg='force save'):
    """强制保存所有数据"""
    Process(target=save_data, args=(dynamic, 'dynamic.json', msg, True)).start()
    Process(target=save_data, args=(secrets, 'secrets.json', msg, True)).start()
    Process(target=save_data, args=(settings, 'settings.json', msg, True)).start()
    Process(target=save_data, args=(tickets, 'tickets_open.json', msg, True)).start()
    Process(target=save_data, args=(tickets_closed, 'tickets_closed.json', msg, True)).start()


def construct_response(msg: dict) -> Any:
    """完成请求响应的构造"""
    response = make_response(jsonify(msg))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


def get_schedule_available(teacher_name, school_name):
    unavailable = list()
    for ticket in list(tickets.values()) + list(tickets_closed.values()):
        if ticket['teacher'] == teacher_name:
            unavailable.append((ticket['date'], ticket['hour']))

    max_days = settings['school'][school_name]['最远可预约天数']
    hrs_prep = settings['school'][school_name]['提前预约小时数']
    working = settings['teacher'][school_name][teacher_name]['时间']

    dates, hours = list(), dict()
    for day in range(max_days):
        date = date_lang(time_shift(days=day).strftime(settings['date_format']))
        hours_available = working[datetime.weekday(datetime.today() + timedelta(days=day))]

        if date in dynamic['off_days'] or not hours_available:
            continue

        hours[date] = list()
        for hour_start in hours_available:
            hour = settings['hour_format'].format(hour_start)
            if (day == 0 and hour_start <= datetime.now().hour + hrs_prep) \
                    or (date, hour) in unavailable:  # 不可预约当日早些时候或该时段已有预约
                continue

            hours[date].append(hour)

        if hours[date]:
            dates.append(date)

    return dates, {date: hours[date] for date in dates}


app = Flask(__name__, )
CORS(app, resources=r'/*')  # 允许跨域请求


@app.route('/', methods=['GET'])
def index():
    """https://github.com/bugstop/hitsz-appointment-scheduling"""
    messages = {'statusCode': 200, 'GitHub': 'bugstop', 'copyright': 2021}
    return construct_response(messages)


@app.route('/checkpoint/', methods=['GET'])
def checkpoint_save():
    checkpoint('checkpoint')
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
    admin = request.json.get('password') in secrets['password']
    messages = {'statusCode': 200 if admin else 500}
    return construct_response(messages)


@app.route('/plan/open/school', methods=['GET'])
def open_ticket_school():
    """展示可供预约的时间段"""

    try:
        messages = {
            'statusCode': 200,
            'schools': list(settings['school']),
            'teachers': settings['school']
        }
    except Exception as e:
        logging.error(('open ticket school error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route('/plan/open/schedule', methods=['GET'])
def open_ticket_schedule():
    """展示可供预约的时间段"""

    try:
        school_name = request.args.get('school')
        teacher_name = request.args.get('teacher')
        if not school_name or not teacher_name:
            raise DataCheckException('school or teacher must be filled')

        dates, hours = get_schedule_available(teacher_name, school_name)

        messages = {
            'statusCode': 200,
            'dates': dates,
            'hours': hours,
        }

    except Exception as e:
        logging.error(('open ticket schedule error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route('/plan/open/', methods=['POST'])
def open_ticket():
    """预约心理咨询"""

    def write_data(ticket):
        """新增预约数据"""
        global tickets, dynamic

        # 验证数据完整性：是否有留空、是否在黑名单
        if not all([ticket.get(item) for item in settings['must_fill']]) \
                or ticket['wx'] in dynamic['blocked']:
            raise DataCheckException('data check failed')

        # 工单唯一ID形式为：流水号@时间戳
        ticket_id = 0 if not tickets and not tickets_closed else max(map(
            int, (tid.split('@')[0] for tid in list(tickets) + list(tickets_closed))))
        new_ticket_id = settings['ticket_format'].format(ticket_id + 1, time_shift().strftime('%Y%m%d'))

        dates, hours = get_schedule_available(ticket['teacher'], ticket['school'])
        if not hours.get(ticket['date']) or ticket['hour'] not in hours.get(ticket['date']):
            logging.error((ticket['date'], ticket['hour'], hours))
            raise DataCheckException('invalid time')

        ticket['status'] = 'open'  # 工单状态：open进行中，close已完成
        ticket['timestamp'] = time_shift().strftime(settings['timestamp'])
        tickets[new_ticket_id] = ticket

        logging.info(('reserve:', 'write data'))
        Process(target=save_data, args=(tickets, 'tickets_open.json', '{} {} {} {}'.format(
            new_ticket_id, ticket['name'], ticket['date'].split('·')[0], ticket['hour'][:5]))).start()

        mail_receiver = settings['teacher'][ticket['school']][ticket['teacher']]['邮箱'] \
            if ticket['name'] != '张三' else secrets['mailSettings']['maintainer']  # 测试账号
        mail_content = '{}{}老师，{}预约了 {}{} 的心理咨询。详细信息请在微信小程序查看。'.format(
            ticket['school'], ticket['teacher'], '有同学', ticket['date'].split('·')[0], ticket['hour'][:5])
        Process(target=send_mail, args=(mail_receiver, '新的心理咨询预约', mail_content)).start()

    try:
        write_data(request.json)
        messages = {'statusCode': 200}
    except Exception as e:
        logging.error(('make reservation error:', e))
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route('/plan/list/', methods=['POST'])
def show_reservations():
    """展示预约工单列表"""

    def list_data(user_filter: str, tag: str):
        """筛选展示的工单并排序"""
        global tickets, tickets_closed

        if tag not in ['open', 'closed']:
            raise DataCheckException('key check failed')

        # 工单展示按预约时间顺序由近及远。工单ID仅作为唯一标识符，并不参与排序
        tickets_selected = tickets if tag != 'closed' else tickets_closed
        time_format = date_convert(settings['time_format'], ('zh', 'en'))
        tickets_show = sorted(list(tickets_selected.keys()), key=lambda z: time_format(
            tickets_selected[z]['date'] + tickets_selected[z]['hour']), reverse=(tag == 'closed'))

        # 自动关闭今天之前的工单
        expired_tickets = list()
        time_format = date_convert(settings['date_format'], ('zh', 'en'))
        while tickets_show and tag == 'open' and time_format(tickets[tickets_show[0]]['date']) < time_shift(days=-1):
            ticket_id = tickets_show.pop(0)
            tickets[ticket_id]['status'] = 'closed'  # TODO: expired
            tickets_closed[ticket_id] = tickets[ticket_id]
            del tickets[ticket_id]
            expired_tickets.append(ticket_id)
        if expired_tickets:
            logging.info(('list:', 'close expired'))
            Process(target=save_data, args=(tickets, 'tickets_open.json', 'close expired')).start()
            Process(target=save_data, args=(tickets_closed, 'tickets_closed.json', expired_tickets)).start()

        # 对于普通用户筛选出本人的预约，管理员可以查看本专业所有预约
        if user_filter not in secrets['password']:
            tickets_show = [ticket for ticket in tickets_show
                            if tickets_selected[ticket].get('wx') == user_filter]
        else:
            tickets_show = [ticket for ticket in tickets_show
                            if tickets_selected[ticket].get('school') == secrets['password'][user_filter]]
        tickets_filtered = {ticket: tickets_selected[ticket] for ticket in tickets_show}

        return tickets_filtered, tickets_show

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


@app.route('/plan/edit/', methods=['POST'])
def edit_reservations():
    """更改心理咨询预约工单的状态"""

    def edit_data(username, ticket_id, operation):
        """修改预约数据"""
        global tickets, tickets_closed

        # closed标注工单为已完成，cancel直接删除工单记录
        if operation not in ['closed', 'cancel']:
            raise DataCheckException('key check failed')

        # 对进行中的工单，本人和管理员有权限进行关闭或删除记录
        if tickets.get(ticket_id) and (username == tickets[ticket_id]['wx'] or username in secrets['password']):
            ticket, date, hour = tickets[ticket_id], tickets[ticket_id]['date'], tickets[ticket_id]['hour']
            tickets[ticket_id]['status'] = operation

            if operation == 'closed':
                tickets_closed[ticket_id] = tickets[ticket_id]
                Process(target=save_data, args=(tickets_closed, 'tickets_closed.json',
                                                'close {}'.format(ticket_id))).start()
            if operation == 'cancel':
                mail_receiver = settings['teacher'][ticket['school']][ticket['teacher']]['邮箱'] \
                    if tickets[ticket_id]['name'] != '张三' else secrets['mailSettings']['maintainer']  # 测试账号
                mail_content = '{}老师，{}取消了原定于 {}{} 的心理咨询。此记录已从系统抹除。'.format(
                    tickets[ticket_id]['teacher'], '学生', date.split('·')[0], hour[:5])
                Process(target=send_mail, args=(mail_receiver, '心理咨询预约取消', mail_content)).start()

            logging.info(('edit:', 'write data'))
            del tickets[ticket_id]
            Process(target=save_data, args=(tickets, 'tickets_open.json',
                                            'delete {}'.format(ticket_id))).start()

        # 对已完成的工单，只有管理员有权限删除
        elif operation == 'cancel' and tickets_closed.get(ticket_id) and username in secrets['password']:
            logging.info(('edit:', 'write data'))
            del tickets_closed[ticket_id]
            Process(target=save_data, args=(tickets_closed, 'tickets_closed.json',
                                            'delete {}'.format(ticket_id))).start()

        else:
            raise DataCheckException('permission denied')

    try:
        uid = request.json.get('user')  # 用户的唯一ID，管理员传密码
        tid = request.json.get('tid')  # 操作的工单ID
        op = request.json.get('op')  # 操作选项（closed，cancel）
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
