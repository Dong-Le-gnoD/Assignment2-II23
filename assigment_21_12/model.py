import sql_handler
from time import time


rb_states = {
    'rob1': ['None', None],
    'rob2': ['None', None],
    'rob3': ['None', None],
    'rob4': ['None', None],
    'rob5': ['None', None],
    'rob6': ['None', None],
    'rob7': ['None', None],
    'rob8': ['None', None],
    'rob9': ['None', None],
    'rob10': ['None', None]
}


def get_current_states():
    st, result = sql_handler.get_current_states()
    print(st)
    for r in result:
        robot_ = r["robotID"]
        sta = r["state"]

        timee = r["time"]
        rb_states[robot_] = [sta, timee]
    return st, result, rb_states


def store_msg(robot_, state, timee):
    if state == "DOWN":
        sql_handler.fill_event(robot_, timee+1, f"Robot {robot_} is down!")

    sql_handler.save_value(robot_, state, timee)


def get_history(robot_id, start_date, end_date):

    start_record, end_record = sql_handler.get_begin_end_time(robot_id)

    if start_record == 0 and end_record == 0:
        print("No begin and end")
        stm = f"No data of {robot_id}"
        return stm, []
    else:
        print("It actually has begin and end")
        if end_date > end_record:
            end_date = end_record

        if start_date < start_record:
            start_date = start_record

        if start_date > end_date:
            stm = "End time should be after start time"
            return stm, []

        stm, res = sql_handler.get_history_states(robot_id, start_date, end_date)

        return stm, res


def frequency_checking_robots():
    print("Frequently checking robots' status")
    stm, result = sql_handler.get_current_states()

    print(stm)
    current_date = int(time() * 1000)
    print(current_date)

    for r in result:
        robot_ = r["robotID"]
        if ((current_date - r["time"]) > 30000) and r["state"] == "READY-IDLE-STARVED":
            sql_handler.fill_event(robot_, current_date, f"Idle too long!")

    return stm, result


def historical_data(robot_id, start_time, end_time):

    start_record, end_record = sql_handler.get_begin_end_time(robot_id="")

    if end_time > end_record:
        end_time = end_record

    if start_time < start_record:
        start_time = start_record

    if start_time > end_time:
        stm = "End time should be after start time"
        return stm, {}

    stm, result = sql_handler.get_history_states(robot_id, start_time, end_time)

    print(stm)
    if len(result) == 0:
        return stm, {}
    else:
        return calculate_time(result, end_time, start_time)


def calculate_time(result, end_time, start_time):
    summary = {'READY-IDLE-STARVED': {'time': 0, 'counter': 0},
               'READY-PROCESSING-EXECUTING': {'time': 0, 'counter': 0},
               'DOWN': {'time': 0, 'counter': 0}}

    down_event = False
    before_down_ts = 0
    mtbf = 0
    time_between_failures = []

    total_time = end_time - start_time
    result.reverse()
    prev_state = result[0]["state"]
    prev_time = result[0]["time"]
    summary[prev_state]["time"] += end_time - prev_time

    for i in range(1, len(result)):
        timee = result[i]["time"]
        value = result[i]["state"]

        if prev_state != value:
            summary[value]["counter"] += 1

        summary[value]["time"] += prev_time - timee

        if prev_state == "DOWN":
            down_event = True
            before_down_ts = timee

        if value == "DOWN" and down_event:
            time_between_failures.append(before_down_ts - prev_time)
            down_event = False

        prev_state = value
        prev_time = timee

    for state, data in summary.items():
        summary[state]['percent'] = round(100 * data["time"] / total_time, 2)
        summary[state]["average"] = 0

        if data["counter"] > 0:
            summary[state]["average"] = round(data["time"] / data["counter"] / 1000, 2)

        summary[state]["time"] = round(data["time"] / 1000)

    if time_between_failures:
        for number in time_between_failures:
            mtbf += number/len(time_between_failures)

    summary['mean'] = round(mtbf/1000)

    return "Get analytical data", summary


