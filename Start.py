import json
import re
from flask import Flask, request, jsonify


class InputValueException(Exception):
    pass


app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test():
    try:
        user = request.args.get('name')
        year = int(request.args.get('year'))
        pattern = r'[^a-zA-Z]+'
        if re.findall(pattern, user):
            raise TypeError("U write uncorrect value")
        return jsonify(username=user, year=year)
    except TypeError as te:
        return jsonify("Error {666}: " + str(te))
    except ValueError:
        return jsonify("Error: was no valid number")

