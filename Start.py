import json
import re
import time

import flask
import logging
import os
import utils
from flask import Flask, request, jsonify, g

""" 
todo - 
1) добавить функцию "getall" - возвращает всё, что есть в файле  v
2) добавить функцию "claerall" - удаляет всё, что есть в файле   v
3) добавить мониторинг: 
        /get_success - возвращает число успешных запросов
        /get_error - возвращает число неуспешных запросов
        /get_all - возвращает число запросов всего
        /get_apm - возвращает среднее время ответа за последнюю секунду (average per minute) 

совет - разобраться с "before request" и "before server start" в доках фласка
удачи!
"""

_data_base = "Example.json"
_pattern = re.compile("[^a-zA-Z]+")
time_count = {}
request_start_time = 0
request_stop_time = 0
error_count = 0
success_count = 0
time_interval = 60
app = Flask(__name__)


@app.before_request
def before_request():
    global request_start_time
    request_start_time = time.time()
    print("start=", request_start_time)


@app.after_request
def after_request(response):
    global time_count, request_start_time, request_stop_time, time_interval
    request_stop_time = time.time()
    time_count[time.time()] = request_stop_time-request_start_time
    for key in list(time_count.keys()):
        if request_stop_time-key > time_interval:
            del time_count[key]
    print("time=", time_count)
    return response


@app.route("/geterror")
def get_error():
    global success_count
    success_count += 1
    return jsonify(error_count)


@app.route("/getsuccess")
def get_success():
    global success_count
    success_count += 1
    return jsonify(success_count)


@app.route("/getallrequest")
def get_all_request():
    global error_count, success_count
    success_count += 1
    return jsonify(error_count+success_count)


@app.route("/getapm")
def get_apm():
    global success_count, time_count, error_count, time_interval
    time_interval = int(request.args.get('interval', 60))
    temp_time = 0
    next_time = time.time()
    success_count += 1
    if not time_count:
        print("time1=", time.time() - next_time)
        return jsonify("apm=", time.time() - next_time)
    else:
        for key in list(time_count.keys()):
            temp_time += time_count[key]
    apm = temp_time/len(list(time_count.keys()))
    return jsonify("apm=", apm)


@app.route("/clearall")
def clear_all():
    global success_count
    success_count += 1
    logger = logging.getLogger("flask-project:/clearall")
    logger.info("User clear all data in Example.json")
    os.remove(_data_base)
    return jsonify("data clear")


@app.route('/getall')
def getall():
    global success_count
    logger=logging.getLogger("flask-project:/getall")
    logger.info("User get all information about names and ages")
    try:
        with open(_data_base, 'r') as file:
            return jsonify(json.load(file))
    except:
        FileNotFoundError("exept")
    return jsonify("no data")


@app.route('/')
def start_page():
    global success_count
    success_count += 1
    return jsonify(r'''Hi, people! '''
                   '''write \'add\', then add name and age, '''
                   '''write \'get\', then get name if you write age or age if you write name''')


@app.route('/add', methods=['GET'])
def test():
    global success_count, error_count
    name_and_age_dict = {}
    logger = logging.getLogger("flask-project/add")
    try:
        name = request.args.get('name', 'Andrey')
        age = int(request.args.get('age', 23))
        name_and_age_dict[name] = age
        time.sleep(3)
        if re.findall(_pattern, name):
            error_count += 1
            raise TypeError
        logger.info("User add name=%s and age=%s" % (name, age))
        name_and_age_dict[name] = age
        if os.stat(_data_base).st_size == 0:
            with open(_data_base, mode='w') as file:
                json.dump(name_and_age_dict, file)
        with open(_data_base, mode='r') as file:
            name_and_age_from_example = json.load(file)

            if name_and_age_from_example:
                if name_and_age_from_example.get(name) is None:
                    name_and_age_from_example[name] = age
            else:
                name_and_age_from_example[name] = age
        with open(_data_base, mode='w', encoding='utf-8') as file:
            json.dump(name_and_age_from_example, file)
            old_time = time.time()
            new_time = time.time()
            print("next time", new_time - old_time)
        success_count += 1
        return jsonify(name_and_age_dict)
    except TypeError:

        logger.error('error(403): User add uncorrect name')
        return flask.abort(403)
    except ValueError:

        logger.error('error(404): User add uncorrect age')
        return flask.abort(404)


@app.route('/get', methods=['GET'])
def get_info_by_parameter():
    global error_count, success_count
    name = request.args.get("name")
    age = request.args.get("age", 0)
    name_for_print = []
    age = int(age)
    #data_from_data_base = utils.get_data_from_file(name, age, _data_base)
    if name is None and age == 0:
        error_count += 1
        return "enter name OR age"
    try:
        with open(_data_base, 'r') as file:
            if age == 0:
                name_and_age_from_example = json.load(file)
                if name_and_age_from_example.get(name):
                        success_count += 1
                        return jsonify(name_and_age_from_example.get(name))
                else:
                        error_count += 1
                        return jsonify("value not found")
            else:
                name_and_age_from_example=json.load(file)
                for key in name_and_age_from_example.keys():
                    if name_and_age_from_example.get(key) == age:
                        name_for_print.append(key)
                if name_for_print:
                    success_count += 1
                    return jsonify(name_for_print)
                else:
                    error_count += 1
                    return jsonify("value not found")
    except ValueError:
        error_count += 1
        logger.error('Error: User did not write value')
        return 'Error: User  write uncorrect value'


if __name__ == "__main__":

    logger = logging.getLogger("flask-project")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("flask-project-log.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    app.run(host='0.0.0.0', port=8080, debug=True)
