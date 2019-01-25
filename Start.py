import json
import re
import flask
import logging
import os
from flask import Flask, request, jsonify


app = Flask(__name__)

""" add:
    1)logging errors
    2)save name and age
    3)get name for age

"""


def get_user_person_data(Username, Age):

    user = {
        'name': Username,
        'age': Age
    }
    return user


@app.route('/')
def start_page():
    """
    Начальная страница
    """
    return jsonify("Hi, people! "
                   "write \"add\", then add name and age, "
                   "write \"get\", then get name if you write age or age if you write name")


@app.route('/add', methods=['GET'])
def test():

# !!!!!!! не работает если файл example пуст, надо чето придумать

    name_and_age_dict = {}
    logger = logging.getLogger("flask-project.add")
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
            print(name_and_age_dict)
            if name_and_age_from_example:
                print(4)
                if name_and_age_from_example.get(name) is None:
                    print(5)
                    name_and_age_from_example[name] = age
            else:
                print(6)
                name_and_age_from_example[name] = age
                print(7)
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
def get_name_for_age():
    """ функция возвращает возраст если ввести имя или если ввести возраст то список имен с таким возрастом
    """
    name_for_print = []
    logger = logging.getLogger("flask-project.get")
    try:
        with open('Example.json', 'r') as file:
            name_and_age_from_example = json.load(file)
        name = request.args.get('name', 'DefaultName')
        age = int(request.args.get('age', -1))
        pattern = r'[^a-zA-Z]+'
        if re.findall(pattern, name):
            raise ValueError
# найти как сделать так чтоб пользователь мог вводить только возраст или имЯ
        if name == 'DefaultName' and age == -1:
            return "Write name or age"
        elif name != 'DefaultName' and age == -1:
            if name_and_age_from_example.get(name):
                return jsonify(name_and_age_from_example.get(name))
            else:
                return jsonify("value not found")
        else:
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

    # create the logging file handler
    fh = logging.FileHandler("flask-project-log.log")

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    app.run(host='0.0.0.0', port=8080, debug=True)