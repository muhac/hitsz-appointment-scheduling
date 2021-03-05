import json
from datetime import datetime, timedelta
from flask import *
from flask_cors import CORS

with open('data/settings.json') as f_obj:
    settings = json.load(f_obj)


def date_lang(date: str, lang: (str, str) = ('en', 'zh')) -> str:
    languages = {
        'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'zh': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    }
    for i in range(len(languages['en'])):
        date = date.replace(languages[lang[0]][i], languages[lang[1]][i])
    return date


app = Flask(__name__, )
CORS(app, resources=r'/*')


@app.route("/", methods=['GET'])
def index():
    messages = {"statusCode": 200, 'GitHub': 'bugstop'}

    response = make_response(jsonify(messages))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


@app.route("/verify/", methods=['GET'])
def admin_verification():
    messages = {"statusCode": 200, 'password': settings['password']}

    response = make_response(jsonify(messages))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


@app.route("/reserve/", methods=['POST'])
def reserve():
    def check_data(data):
        with open('data/available.json') as f:
            schedule = json.load(f)

        if not all([
            data.get('name'),
            data.get('sex'),
            data.get('id'),
            data.get('mobile'),
            data.get('teacher'),
            data.get('date'),
            data.get('hour'),
            data.get('detail'),
        ]) or schedule[data['date']][data['hour']] < 1:
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
        new_ticket = '{:05d}@{}'.format(ticket_id, datetime.now().strftime('%Y%m%d%M%S'))
        appointments[new_ticket] = data

        with open('data/in_progress.json', 'w') as f:
            json.dump(appointments, f)

    post = request.json
    print(post)
    messages = {"statusCode": 200}

    try:
        check_data(post)
        print('write data')
        write_data(post)
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    response = make_response(jsonify(messages))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


@app.route("/list/", methods=['GET'])
def in_progress():
    def get_data():
        with open('data/in_progress.json') as f:
            appointments = json.load(f)

        tickets = sorted(list(appointments.keys()),
                         key=lambda z: datetime.strptime(
                             date_lang(appointments[z]['date'] +
                                       appointments[z]['hour'], ('zh', 'en')),
                             settings['sort_helper'])
                         )

        return appointments, tickets

    messages = {'statusCode': 200}

    try:
        data = get_data()
        messages['tickets'] = data[1]
        messages['inProgress'] = data[0]
    except Exception as e:
        print(e)
        messages['statusCode'] = 500

    response = make_response(jsonify(messages))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


@app.route("/available/", methods=['GET'])
def available():
    def get_data(max_days=10):
        with open('data/available.json') as f:
            schedule = json.load(f)

        dates = [date_lang(key, ('zh', 'en')) for key in list(schedule.keys())]
        dates.sort(key=lambda z: datetime.strptime(z, settings['time_format']))

        if not dates or len(dates) != max_days or \
                datetime.strptime(dates[0], settings['time_format']) < datetime.now() - timedelta(days=1) or \
                datetime.strptime(dates[-1], settings['time_format']) < datetime.now() + timedelta(days=max_days - 2):
            print('update schedule')

            schedule_new = {}
            for day in range(max_days):
                d = date_lang((datetime.now() + timedelta(days=day)).strftime(settings['time_format']))
                schedule_new[d] = {}
                for hour in settings['work_start']:
                    h = settings['work_hours'].format(hour)

                    if d in dates and h in list(schedule[d].keys()):
                        schedule_new[d][h] = schedule[d][h]
                    else:
                        schedule_new[d][h] = settings['max_capacity']

            with open('data/available.json', 'w') as f:
                json.dump(schedule_new, f)
            schedule = schedule_new

        date = sorted(list(schedule.keys()),
                      key=lambda z: datetime.strptime(date_lang(z, ('zh', 'en')), settings['time_format']))
        hour = sorted(list(schedule[list(schedule.keys())[0]].keys()), key=lambda z: int(z[:2]))

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

    response = make_response(jsonify(messages))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


if __name__ == '__main__':
    app.run(port=2333)
