import sql_handler
from mqtt_sub import client_sub
from threading import Thread
import model

import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
import time

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('all_states_polling.html')


@app.route('/get_robot_states')
def get_robot_states():
    stm, result, rob_states = model.get_current_states()
    return jsonify(rob_states)


@app.route('/events_display')
def events_display():
    return render_template('index.html')


@app.route('/search_results', methods=['POST'])
def search_results():
    start_time = int(request.form.get('start_time'))
    end_time = int(request.form.get('end_time'))
    selected_robot = request.form.get('robotSelect')

    stm, result = model.get_history(selected_robot, start_time, end_time)
    # [{}, {}, {}, {}]
    return json.dumps(result)


@app.route('/chart_results', methods=['POST'])
def chart_results():
    start_time = int(request.form.get('start_time'))
    end_time = int(request.form.get('end_time'))
    selected_robot = request.form.get('robotSelect')

    stm, result = model.historical_data(selected_robot, start_time, end_time)
    # {"":{}, "":{}, "":{}}
    return result


def controller():
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__' or __name__ == 'app':
    sql_handler.create_table()

    mqtt_client = Thread(target=client_sub, name="mqtt_client")
    mqtt_client.start()

    chking = Thread(target=model.frequency_checking_robots, name='chking')
    chking.start()

    controller = Thread(target=controller, name="controller")
    controller.start()



