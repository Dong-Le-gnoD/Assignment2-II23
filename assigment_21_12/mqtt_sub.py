import model
import paho.mqtt.subscribe as subscribe
from datetime import datetime, timezone
import json

NUM_ROB = 10
MQTT_TOPIC = "ii23/telemetry/#"
MQTT_BROKER = "broker.mqttdashboard.com"
rob_list = []
for i in range(NUM_ROB):
    rob_list.append(f"rob{i+1}")


def on_message_print(client, userdata, msg):
    try:
        js_msg = json.loads(msg.payload)
        print(js_msg)

        robot_ = js_msg["deviceId"]
        if robot_ in rob_list:
            state = js_msg["state"]

            int_time = str_time_to_integer(js_msg["time"])

        print(f"Message Received: {robot_}, {state}, {int_time}")
        model.store_msg(robot_, state, int_time)

    except Exception as e:
        print(e)


def str_time_to_integer(date_time_str):
    yr = int(date_time_str[0:4])
    mth = int(date_time_str[5:7])
    dd = int(date_time_str[8:10])
    hr = int(date_time_str[11:13])
    minute = int(date_time_str[14:16])
    sec = int(date_time_str[17:19])
    mlsec = int(date_time_str[20:23])

    epoch_timestamp = int(datetime(yr, mth, dd, hr, minute, sec).timestamp()) * 1000 + mlsec
    return epoch_timestamp


def client_sub():

    while True:
        subscribe.callback(on_message_print, MQTT_TOPIC, hostname=MQTT_BROKER)



