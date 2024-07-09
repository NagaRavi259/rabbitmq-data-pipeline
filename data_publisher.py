#imports
from paho.mqtt import client as mqtt_client
import random
import yaml
import time
import json
from datetime import datetime
import pytz

## Reading config file
try:
    with open("mqtt_config.yaml", "r") as file:
        Config_data = yaml.safe_load(file)
except Exception as e:
    print("Got an error while fetching config please check restart program")
    print("Config " + repr(e) + " unable read config ")

class PublishData:
    def __init__(self, MQTT_data, publish_interval=1, publish_period=10, continuous=False, status_min=0, status_max=6):
        ## Reading Mqtt config
        self.MQTT_HOST = MQTT_data["MQTT_IP"]
        self.MQTT_PORT = MQTT_data["MQTT_Port"]
        self.MQTT_TOPIC = MQTT_data["Topic"]
        self.MQTT_QOS = MQTT_data["QoS"]
        self.MQTT_USERNAME = MQTT_data["userName"]
        self.MQTT_PASSWORD = MQTT_data["Password"]

        self.status_min = status_min
        self.status_max = status_max

        self.PUBLISH_INTERVAL = publish_interval
        self.PUBLISH_PERIOD = publish_period

        self.COUNT = 0
        self.CONTINUOUS = continuous

        ## connect MQTT server
        self.reconnect_attempts = 0
        self.client = self.connect_mqtt()

    def reconnect(self):
        try:
            if self.reconnect_attempts > 10:
                raise Exception("failed to establish connection check the config")
            print(f"trying to reconnect attempt :- {self.reconnect_attempts}")
            self.reconnect_attempts += 1
            self.client = self.connect_mqtt()
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise Exception("MongoDB connection failed.")

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                self.reconnect_attempts = 0
            else:
                if rc == 5:
                    raise Exception("Connection Refused: Not authorized. Please check your credentials.")
                else:
                    print(f"Failed to connect, return code {rc}")
                self.reconnect()

        client = mqtt_client.Client(f"Test_MQTT_Publisher_{random.randint(5,97)}")
        client.username_pw_set(self.MQTT_USERNAME, self.MQTT_PASSWORD)
        client.on_connect = on_connect

        try:
            client.connect(self.MQTT_HOST, self.MQTT_PORT)
        except ConnectionRefusedError as e:
            print(f"Connection to MQTT broker failed: {e}")
            time.sleep(5)  # Wait before retrying
            self.reconnect()

        return client

    def publish_data(self):
        current_utc_time = datetime.now(pytz.utc)
        timestamp = current_utc_time.isoformat(" ")

        payload = {
            "timeStamp": timestamp,
            "Device": "Device1",
            "data": {
                "status": random.randint(self.status_min, self.status_max)
            }
        }

        json_payload = json.dumps(payload)
        try:
            response = self.client.publish(self.MQTT_TOPIC, json_payload, qos=self.MQTT_QOS)
            time.sleep(0.01)
            status = response.is_published()
            if status == True:
                self.COUNT += 1
                print(f"{self.COUNT} messages sent")
        except:
            print(f"failed to publish message ERROR CODE :- {response[0]}")

        return response

    def start_loop(self):
        self.client.loop_start()

        current_time = time.time()
        end_time = current_time + self.PUBLISH_PERIOD

        while (current_time < end_time) or self.CONTINUOUS:
            self.publish_data()
            time.sleep(self.PUBLISH_INTERVAL)
            current_time = time.time()
        ## Closing the connectiion
        self.client.disconnect()

if __name__ == "__main__":
    calss_instence = PublishData(Config_data['MQTT_CONFIG'], 1, 10, continuous=True)
    calss_instence.start_loop()