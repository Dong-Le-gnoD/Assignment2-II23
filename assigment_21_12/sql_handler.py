import sqlite3

c = None
conn = None
NUM_ROB = 10

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def create_table():
    global conn, c
    conn = sqlite3.connect('assigment2group3.db', check_same_thread=False)
    conn.row_factory = dict_factory

    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS history "
              "(robotID text, state text, time integer, PRIMARY KEY (robotID, time));")
    c.execute("CREATE TABLE IF NOT EXISTS current (robotID text PRIMARY KEY, state text, time integer);")
    c.execute("CREATE TABLE IF NOT EXISTS events (robotID text PRIMARY KEY, event text, time integer);")


def get_current_states():
    sql_st = "SELECT * FROM current"
    c.execute(sql_st)

    result = c.fetchall()

    if len(result) != NUM_ROB:
        st = "Not all robots have current states"
    else:
        st = "Got all robots' states"
    return st, result


def get_begin_end_time(robot_id):
    if robot_id == "":
        sql_st = f"SELECT time FROM history"
    else:
        sql_st = f"SELECT time FROM history WHERE robotID=\"{robot_id}\""

    c.execute(sql_st)

    result = c.fetchall()
    if len(result) != 0:
        return result[0]["time"], result[-1]["time"]

    return 0, 0


def get_history_states(robot_id, start_time, end_time):
    sql_st = f"SELECT state, time FROM history WHERE robotID=\"{robot_id}\" " \
             f"AND time BETWEEN {str(start_time)} AND {str(end_time)}"

    c.execute(sql_st)

    result = c.fetchall()
    if len(result) != 0:
        return f"Got history state of {robot_id}", result
    else:
        return "No History", []


def save_value(robot_id, state, timee):

    sql_st1 = f"REPLACE INTO current (robotID, state, time) VALUES (\"{robot_id}\", \"{state}\", {timee})"
    sql_st2 = f"INSERT INTO history (robotID, state, time) VALUES (\"{robot_id}\", \"{state}\", {timee})"
    try:
        print(sql_st1)
        c.execute(sql_st1)
        print(sql_st2)
        c.execute(sql_st2)
        conn.commit()
        print("Successfully save data")

    except conn.Error as e:
        conn.rollback()
        print("Unsuccessfully save data")


def fill_event(robot_id, timee, statement):

    sql_st = f"INSERT INTO events (robotID, event, time) VALUES (\"{robot_id}\", \"{statement}\", {timee})"

    try:
        c.execute(sql_st)
        conn.commit()
        print("Successfully save event")

    except conn.Error as e:
        conn.rollback()
        print("Unsuccessfully save event")
