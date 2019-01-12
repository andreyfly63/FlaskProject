import re
import flask
from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test():
    try:
        user = request.args.get('name', 'Andrey')
        age = int(request.args.get('age', 23))
        pattern = r'[^a-zA-Z]+'
        if re.findall(pattern, user):
            raise TypeError
#            raise TypeError("U write uncorrect value")
        return jsonify(username=user, age=age)
    except TypeError:
        return flask.abort(403)
#        return jsonify("Error {666}: " + str(te))
    except ValueError:
        return flask.abort(404)
#        return jsonify("Error: was no valid number")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
