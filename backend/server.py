# Author: limuhan
# GitHub: bugstop

import os
import json
import signal
import requests
from typing import Any, Callable
from multiprocessing import Process
from datetime import datetime, timedelta

from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText

from flask import *
from flask_cors import CORS

path: str = os.getcwd() + '/data/'

with open(path + 'secrets.json') as f_obj:
    secrets = json.load(f_obj)
with open(path + 'settings.json') as f_obj:
    settings = json.load(f_obj)
with open(path + 'schedules.json') as f_obj:
    schedule = json.load(f_obj)
with open(path + 'tickets.json') as f_obj:
    appointments = json.load(f_obj)
with open(path + 'tickets_closed.json') as f_obj:
    appointments_closed = json.load(f_obj)
with open(path + 'dynamic.json') as f_obj:
    dynamic = json.load(f_obj)


def send_mail(receiver: str, title: str, content: str) -> None:
    try:
        server = secrets['mailSettings']['server']
        username = secrets['mailSettings']['username']
        password = secrets['mailSettings']['password']

        smtp = SMTP_SSL(server)
        smtp.set_debuglevel(0)
        smtp.ehlo(server)
        smtp.login(username, password)

        msg = MIMEText(content, "plain", 'utf-8')
        msg["Subject"] = Header(title, 'utf-8')
        msg["From"] = username
        msg["To"] = receiver
        smtp.sendmail(username, receiver, msg.as_string())
        smtp.quit()
    except Exception as e:
        print('send mail error:', e)


def save_data(data: Any, filename: str) -> None:
    print('update:', filename)
    try:
        with open(path + filename, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print('save data error:', e)


def date_lang(date: str, lang: (str, str) = ('en', 'zh')) -> str:
    languages = settings['languages']
    source_dict, target_dict = languages[lang[0]], languages[lang[1]]
    for source_word, target_word in zip(source_dict, target_dict):
        date = date.replace(source_word, target_word)
    return date


def date_convert(date_format: str, lang: (str, str) = ('en', 'zh')) -> Callable:
    return lambda z: datetime.strptime(date_lang(z, lang), date_format)


def construct_response(msg: dict) -> Any:
    print('response:', msg)
    response = make_response(jsonify(msg))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


app = Flask(__name__, )
CORS(app, resources=r'/*')


@app.route("/", methods=['GET'])
def index():
    messages = {"statusCode": 200, 'GitHub': 'bugstop', 'copyright': 2021}
    return construct_response(messages)


@app.route("/uid/", methods=['POST'])
def get_uid():
    code = request.json.get('code')
    url = 'https://api.weixin.qq.com/sns/jscode2session?' \
          'appid={}&secret={}&js_code={}&grant_type=authorization_code'
    rc = requests.get(url.format(secrets['AppID'], secrets['AppSecret'], code))
    messages = {"statusCode": 200, 'wx': rc.json().get('openid')}
    return construct_response(messages)


@app.route("/verify/", methods=['POST'])
def admin_verification():
    messages = {"statusCode": 200 if secrets['password'] == request.json.get('password') else 500}
    return construct_response(messages)


@app.route("/reserve/", methods=['POST'])
def make_reservations():
    def check_data(data):
        global schedule, dynamic

        if not all([data.get(item) for item in settings['questionnaire']]) \
                or schedule[data['date']][data['hour']] < 1 or data['wx'] in dynamic['blocked']:
            print('reserve: data check failed')
            raise RuntimeError

        schedule[data['date']][data['hour']] -= 1
        Process(target=save_data, args=(schedule, 'schedules.json')).start()

    def write_data(data):
        global appointments

        tickets = sorted(list(appointments.keys()), key=lambda z: int(z.split('@')[0]))
        ticket_id = 1 if not tickets else int(tickets[-1].split('@')[0]) + 1
        new_ticket = settings['ticket_format'].format(ticket_id, datetime.now().strftime('%Y%m%d'))

        data['status'] = 'open'
        data['timestamp'] = datetime.now().strftime(settings['timestamp'])
        appointments[new_ticket] = data

        print('reserve: write data')
        Process(target=save_data, args=(appointments, 'tickets.json')).start()

        mail_content = '{}老师，{}（{}）预约了{} ・ {}的心理咨询。'.format(
            data["teacher"], data['name'], data['mobile'], data['date'], data['hour'])
        Process(target=send_mail, args=('limuhan@live.com', '新的心理咨询预约', mail_content)).start()

    post = request.json
    messages = {"statusCode": 200}

    try:
        check_data(post)
        write_data(post)
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    return construct_response(messages)


@app.route("/edit/", methods=['POST'])
def edit_reservations():
    def edit(username, ticket_id, operation):
        global schedule, appointments, appointments_closed

        if operation not in ['open', 'closed', 'cancel']:
            raise KeyError

        if appointments.get(ticket_id) and username in (appointments[ticket_id]['wx'], secrets['password']):
            date, hour = appointments[ticket_id]['date'], appointments[ticket_id]['hour']
            appointments[ticket_id]['status'] = operation

            if operation == 'closed':
                appointments_closed[ticket_id] = appointments[ticket_id]
                Process(target=save_data, args=(appointments_closed, 'tickets_closed.json')).start()

            if operation == 'cancel':
                try:
                    schedule[date][hour] += 1
                    Process(target=save_data, args=(schedule, 'schedules.json')).start()
                except KeyError:
                    pass

            print('edit: write data')
            del appointments[ticket_id]
            Process(target=save_data, args=(appointments, 'tickets.json')).start()

        elif appointments_closed.get(ticket_id) and username == secrets['password']:
            date, hour = appointments_closed[ticket_id]['date'], appointments_closed[ticket_id]['hour']
            appointments_closed[ticket_id]['status'] = operation

            if operation == 'cancel':
                try:
                    schedule[date][hour] += 1
                    Process(target=save_data, args=(schedule, 'schedules.json')).start()
                except KeyError:
                    pass

            del appointments_closed[ticket_id]
            Process(target=save_data, args=(appointments_closed, 'tickets.json')).start()

        else:
            print('edit: permission denied')

    messages = {'statusCode': 200}

    try:
        user = request.json.get('user')
        tid = request.json.get('tid')
        op = request.json.get('op')
        edit(user, tid, op)
    except Exception as e:
        print('edit error:', e)
        messages = {'statusCode': 500}

    return construct_response(messages)


@app.route("/list/", methods=['POST'])
def show_reservations():
    def get_data(user_filter: str, tag: str):
        global appointments, appointments_closed

        if tag not in ['open', 'closed']:
            raise KeyError
        appointments_selected = appointments_closed if tag == 'closed' else appointments

        time_format = date_convert(settings['sort_helper'], ('zh', 'en'))
        tickets = sorted(list(appointments_selected.keys()), key=lambda z: time_format(
            appointments_selected[z]['date'] + appointments_selected[z]['hour']), reverse=(tag == 'closed'))

        if user_filter != secrets['password']:
            tickets = [ticket for ticket in tickets if appointments_selected[ticket].get('wx') == user_filter]
        appointments_filtered = {ticket: appointments_selected[ticket] for ticket in tickets}

        return appointments_filtered, tickets

    messages = {'statusCode': 200}

    try:
        username = request.json.get('user')
        ticket_status = request.json.get('tag')
        data = get_data(username, ticket_status)
        messages['tickets'] = data[1]
        messages['inProgress'] = data[0]
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    return construct_response(messages)


@app.route("/available/", methods=['GET'])
def available():
    def get_data(max_days=10):
        global schedule, dynamic

        time_format = date_convert(settings['time_format'], ('zh', 'en'))
        dates = sorted(list(schedule.keys()), key=lambda z: time_format(z))

        if not dates or len(dates) != max_days or \
                time_format(dates[0]) < datetime.now() - timedelta(days=1) or \
                time_format(dates[-1]) < datetime.now() + timedelta(days=max_days - 2):

            schedule_new = {}
            for day in range(max_days):
                date = date_lang((datetime.now() + timedelta(days=day)).strftime(settings['time_format']))
                schedule_new[date] = {}
                for start in settings['work_start']:
                    hour = settings['work_hours'].format(start, start)
                    exist = date in dates and hour in list(schedule[date].keys())
                    schedule_new[date][hour] = schedule[date][hour] if exist else settings['max_capacity']

            schedule = schedule_new
            Process(target=save_data, args=(schedule, 'schedules.json')).start()

        time_format = date_convert(settings['time_format'], ('zh', 'en'))
        date_show = sorted(list(schedule.keys()), key=lambda z: time_format(z))
        hour_show = sorted(list(schedule[date_show[0]].keys()), key=lambda z: int(z[:2]))

        date_show = [date for date in date_show if not any(off_day in date for off_day in dynamic['off_days'])
                     and any(work_day in date for work_day in settings['work_days'] + dynamic['work_days'])
                     and sum(schedule[date].values()) > 0]
        schedule_show = {date: schedule[date] for date in date_show}

        time_format = date_convert(settings['sort_helper'], ('zh', 'en'))
        ddl = datetime.now() + timedelta(hours=settings['hour_before'])
        schedule_show[date_show[0]] = {hour: 0 if ddl > time_format(date_show[0] + hour) else
                                             schedule_show[date_show[0]][hour] for hour in hour_show}

        return schedule_show, date_show, hour_show

    messages = {"statusCode": 200}

    try:
        data = get_data(settings['max_days'])
        messages['date'] = data[1]
        messages['hour'] = data[2]
        messages['schedule'] = data[0]
        messages['teachers'] = settings['teachers']
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    return construct_response(messages)


if __name__ == '__main__':
    print('working directory:', path)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    app.run(port=2333)
