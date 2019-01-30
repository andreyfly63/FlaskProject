import json
import re
import flask
import logging
import os
from flask import Flask, request, jsonify
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
app = Flask(__name__)


@app.route("/clearall")
def clear_all():
    logger = logging.getLogger("flask-project:/clearall")
    logger.info("User clear all data in Example.json")
    with open("Example.json", 'w'):
        pass
    return jsonify("data clear")


@app.route('/getall')
def getall():
    logger=logging.getLogger("flask-project:/getall")
    logger.info("User get all information about names and ages")
    if os.stat("Example.json").st_size == 0:
        with open("Example.json", mode='w'):
            pass
        return jsonify("no data")
    with open("Example.json", 'r') as file:
        return jsonify(json.load(file))


@app.route('/')
def start_page():
    return jsonify(r'''Hi, people! '''
                   '''write \'add\', then add name and age, '''
                   '''write \'get\', then get name if you write age or age if you write name''')


@app.route('/add', methods=['GET'])
def test():
    name_and_age_dict = {}
    logger = logging.getLogger("flask-project/add")
    try:
        name = request.args.get('name', 'Andrey')
        age = int(request.args.get('age', 23))
        name_and_age_dict[name] = age

        pattern = r'[^a-zA-Z]+'
        if re.findall(pattern, name):
            raise TypeError
        logger.info("User add name=%s and age=%s" % (name, age))
        name_and_age_dict[name] = age
        if os.stat("Example.json").st_size == 0:
            with open("Example.json", mode='w') as file:
                json.dump(name_and_age_dict, file)
        with open("Example.json", mode='r') as file:
            name_and_age_from_example = json.load(file)

            if name_and_age_from_example:
                if name_and_age_from_example.get(name) is None:
                    name_and_age_from_example[name] = age
            else:
                name_and_age_from_example[name] = age
        with open("Example.json", mode='w', encoding='utf-8') as file:
            json.dump(name_and_age_from_example, file)
        return jsonify(name_and_age_dict)
    except TypeError:
        logger.error('error(403): User add uncorrect name')
        return flask.abort(403)
    except ValueError:
        logger.error('error(404): User add uncorrect age')
        return flask.abort(404)


@app.route('/get', methods=['GET'])
def get_info_by_parameter():
    name = request.args.get("name")
    age = request.args.get("age", 0)
    print (type(age))
    name_for_print = []
    age = int(age)
    if name is None and age == 0:
        return "enter name OR age"
    try:
        with open('Example.json', 'r') as file:
            if age == 0:
                name_and_age_from_example = json.load(file)
                if name_and_age_from_example.get(name):
                        return jsonify(name_and_age_from_example.get(name))
                else:
                        return jsonify("value not found")
            else:
                name_and_age_from_example=json.load(file)
                for key in name_and_age_from_example.keys():
                    if name_and_age_from_example.get(key) == age:
                        name_for_print.append(key)
                if name_for_print:
                    return jsonify(name_for_print)
                else:
                    return jsonify("value not found")
    except ValueError:
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