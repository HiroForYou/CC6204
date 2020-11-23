from flask import Flask, request

from src.exceptions import Container
from src.homeworks.homework1 import homework1
from src.homeworks.homework2 import homework2
from src.homeworks.homework3 import homework3
from src.homeworks.homework4 import homework4
from src.messages import error

available_homeworks = {
    '1': homework1,
    '2': homework2,
    '3': homework3,
    '4': homework4
}


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('configs.cfg')


def request_checking(request, token_level, homework_number):
    if not request.is_json:
        raise Container(error('Sent format is not a json', 'json'))
    data = request.get_json()
    if 'token' not in data:
        raise Container(error('The token is not included', 'token_missing'))
    if data['token'] != app.config[token_level]:
        raise Container(
            error(
                'The token is not correct/is invalid',
                'token_wrong'))
    if homework_number not in available_homeworks:
        raise Container(
            error(
                f'There is no homework {homework_number}',
                'no_homework'))

    return data


@app.route('/ping')
def ping():
    # return {'message': 'Not yet ready.'}
    return {'status': 'OK'}


@app.route('/force_reload/<string:homework_number>', methods=['POST'])
def reload_tests(homework_number):
    try:
        request_checking(
            request,
            token_level='ADMIN_TOKEN',
            homework_number=homework_number)
    except Container as e:
        return e.data

    available_homeworks[homework_number].reload_tests()

    return {'status': 'OK'}


@app.route('/api/autocheck/<string:homework_number>/<string:question_number>',
           methods=['POST'])
def autocheck(homework_number, question_number):
    try:
        data = request_checking(
            request,
            token_level='TOKEN',
            homework_number=homework_number)
    except Container as e:
        return e.data

    return available_homeworks[homework_number].check(
        question_number=question_number,
        data=data)


@app.route('/api/tests/<string:homework_number>/<string:question_number>',
           methods=['POST'])
def process(homework_number, question_number):
    try:
        data = request_checking(
            request,
            token_level='TOKEN',
            homework_number=homework_number)
    except Container as e:
        return e.data

    return available_homeworks[homework_number].get_test(
        question_number=question_number,
        data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
