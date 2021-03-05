# Author: limuhan
# GitHub: bugstop

import json
import requests
from typing import Callable
from datetime import datetime, timedelta

from flask import *
from flask_cors import CORS

with open('data/secrets.json') as f_obj:
    secrets = json.load(f_obj)

with open('data/settings.json') as f_obj:
    settings = json.load(f_obj)


def date_lang(date: str, lang: (str, str) = ('en', 'zh')) -> str:
    languages = settings['languages']
    source_dict, target_dict = languages[lang[0]], languages[lang[1]]
    for source_word, target_word in zip(source_dict, target_dict):
        date = date.replace(source_word, target_word)
    return date


def date_convert(date_format: str, lang: (str, str) = ('en', 'zh')) -> Callable:
    return lambda z: datetime.strptime(date_lang(z, lang), date_format)


def construct_response(msg: dict):
    print(msg)
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
def reserve():
    def check_data(data):
        with open('data/dynamic.json') as f:
            dynamic = json.load(f)
        with open('data/available.json') as f:
            schedule = json.load(f)

        if not all([data.get(item) for item in settings['questionnaire']]) \
                or schedule[data['date']][data['hour']] < 1 or data['wx'] in dynamic['blocked']:
            print('check failed')
            raise RuntimeError

        schedule[data['date']][data['hour']] -= 1
        with open('data/available.json', 'w') as f:
            json.dump(schedule, f)

    def write_data(data):
        with open('data/in_progress.json') as f:
            appointments = json.load(f)

        tickets = sorted(list(appointments.keys()), key=lambda z: int(z.split('@')[0]))
        ticket_id = 1 if not tickets else int(tickets[-1].split('@')[0]) + 1
        new_ticket = settings['ticket_format'].format(ticket_id, datetime.now().strftime('%Y%m%d'))

        data['timestamp'] = datetime.now().strftime(settings['timestamp'])
        appointments[new_ticket] = data

        with open('data/in_progress.json', 'w') as f:
            json.dump(appointments, f)

    post = request.json
    messages = {"statusCode": 200}

    try:
        check_data(post)
        print('write data')
        write_data(post)
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    return construct_response(messages)


@app.route("/list/", methods=['POST'])
def in_progress():
    def get_data(user_filter: str = None):
        with open('data/in_progress.json') as f:
            appointments = json.load(f)

        time_format = date_convert(settings['sort_helper'], ('zh', 'en'))
        tickets = sorted(list(appointments.keys()),
                         key=lambda z: time_format(appointments[z]['date'] + appointments[z]['hour']))

        if user_filter != secrets['password']:
            tickets_filtered = [ticket for ticket in tickets if appointments[ticket].get('wx') == user_filter]
            appointments_filtered = {ticket: appointments[ticket] for ticket in tickets_filtered}
            appointments, tickets = appointments_filtered, tickets_filtered

        return appointments, tickets

    messages = {'statusCode': 200}

    try:
        username = request.json.get('user')
        data = get_data(username)
        messages['tickets'] = data[1]
        messages['inProgress'] = data[0]
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    return construct_response(messages)


@app.route("/available/", methods=['GET'])
def available():
    def get_data(max_days=10):
        with open('data/available.json') as f:
            schedule = json.load(f)

        time_format = date_convert(settings['time_format'])
        dates = [date_lang(key, ('zh', 'en')) for key in list(schedule.keys())]
        dates.sort(key=lambda z: time_format(z))

        if not dates or len(dates) != max_days or \
                time_format(dates[0]) < datetime.now() - timedelta(days=1) or \
                time_format(dates[-1]) < datetime.now() + timedelta(days=max_days - 2):
            print('update schedule')

            schedule_new = {}
            for day in range(max_days):
                d = date_lang((datetime.now() + timedelta(days=day)).strftime(settings['time_format']))
                schedule_new[d] = {}
                for hour in settings['work_start']:
                    h = settings['work_hours'].format(hour, hour)

                    if d in dates and h in list(schedule[d].keys()):
                        schedule_new[d][h] = schedule[d][h]
                    else:
                        schedule_new[d][h] = settings['max_capacity']

            with open('data/available.json', 'w') as f:
                json.dump(schedule_new, f)
            schedule = schedule_new

        time_format = date_convert(settings['time_format'], ('zh', 'en'))
        date = sorted(list(schedule.keys()), key=lambda z: time_format(z))
        hour = sorted(list(schedule[date[0]].keys()), key=lambda z: int(z[:2]))

        with open('data/dynamic.json') as f:
            dynamic = json.load(f)

        date = [d for d in date if not any(off_day in d for off_day in dynamic['off_days'])
                and any(work_day in d for work_day in settings['work_days'] + dynamic['work_days'])]
        schedule = {d: schedule[d] for d in date}

        time_format = date_convert(settings['sort_helper'], ('zh', 'en'))
        schedule[date[0]] = {h: 0 if datetime.now() + timedelta(hours=settings['hour_before']) >
                                     time_format(date[0] + h) else schedule[date[0]][h] for h in hour}

        return schedule, date, hour

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
    app.run(port=2333)
