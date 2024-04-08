from json import loads, dumps
from typing import Any, Tuple

from flask_mqtt import Mqtt
from flask_mysql import MySQL
from paho.mqtt.client import MQTTMessage, Client
from flask import Flask, request, render_template


app, mqtt, mysql = Flask(__name__), Mqtt(), MySQL()
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['MQTT_BROKER_URL'] = '100.64.177.74'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'admin'
app.config['MQTT_PASSWORD'] = '012345678'
app.config['MQTT_REFRESH_TIME'] = 0.5

app.config['MYSQL_USER'] = 'gyros'
app.config['MYSQL_PASSWORD'] = 'gyro'
app.config['MYSQL_DB'] = 'gyro'


@mqtt.on_connect()
def handle_connect(client: Client, userdata: Any, flags: int, rc: int) -> None:
    print("Connected to MQTT Broker")
    client.subscribe('gyro')


@mqtt.on_message()
def handle_message(client: Client, userdata: Any, message: MQTTMessage) -> None:
    payload = loads(message.payload)

    with mysql.cursor() as cursor:
        cursor.execute(
            "INSERT IGNORE INTO data(x, y, z, temp) VALUES(%s, %s, %s, %s)",
            (int(payload[key]) for key in ('x', 'y', 'z', 'temp'))
        )


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/live")
def get_live() -> str:
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM data ORDER BY created_at DESC LIMIT 1;")

        entry = cursor.fetchone()
        if not entry:
            return """{"x": "NaN", "y": "NaN", "z": "NaN", "temp": "NaN", "created_at": "null"}"""

        return dumps({
            field[0]: value if isinstance(value, int) else str(value)
            for field, value in zip(cursor.description, entry)
        })


@app.get("/temps")
def get_data() -> str:
    with mysql.cursor() as cursor:
        cursor.execute("SELECT temp, created_at FROM data ORDER BY created_at ASC LIMIT 15;")

        entries = cursor.fetchall()
        if not entries:
            return "[]"

        return dumps([{
            field[0]: value if isinstance(value, int) else str(value)
            for field, value in zip(cursor.description, entry)
        } for entry in entries])


@app.post("/clear")
def clear_data() -> str:
    with mysql.cursor() as cursor:
        cursor.execute("DELETE FROM data;")
        return "OK", 200


@app.post("/led")
def toggle_led() -> Tuple[str, int]:
    if 'state' not in request.args:
        return "Request should have a 'state' field\n", 400

    state = request.args['state']
    if state in ('ON', 'OFF'):
        mqtt.publish('LED', state)
        return f"{state}\n", 200

    return f"Invalid state: {state}\n", 400


if __name__ == "__main__":
    mqtt.init_app(app)
    mysql.init_app(app)
    app.run(host="0.0.0.0", port=8000)
