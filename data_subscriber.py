#imports
import random
import yaml
import time
import json
import pytz
from datetime import datetime
from pymongo import MongoClient
from paho.mqtt import client as mqtt_client
from pymongo.errors import ConnectionFailure

## Reading config file
try:
    with open("mqtt_config.yaml", "r") as file:
        Config_data = yaml.safe_load(file)
except Exception as e:
    print("Got an error while fetching config please check restart program")
    print("Config " + repr(e) + " unable read config ")

class SubscribeData:
    def __init__(self, MQTT_data, MONGO_data):
        ## Reading Mqtt config
        self.MQTT_HOST = MQTT_data["MQTT_IP"]
        self.MQTT_PORT = MQTT_data["MQTT_Port"]
        self.MQTT_TOPIC = MQTT_data["Topic"]
        self.MQTT_QOS = MQTT_data["QoS"]
        self.MQTT_USERNAME = MQTT_data["userName"]
        self.MQTT_PASSWORD = MQTT_data["Password"]
        
        
        ## Reading MONGO config
        self.MONGO_HOST = MONGO_data["HOST"]
        self.MONGO_PORT = MONGO_data["PORT"]
        self.MONGO_USERNAME = MONGO_data["USERNAME"]
        self.MONGO_PASSWORD = MONGO_data["PASSWORD"]
        self.MONGO_DATABASE = MONGO_data["DATABASE"]
        
        ## connect MQTT server
        
        self.reconnect_attempts = 0
        self.mqtt_client = self.connect_mqtt()
        
        self.mongo_collection = "mqtt_data"
        self.mongo_client = self.connect_mongo()
        
    def reconnect(self):
        try:
            if self.reconnect_attempts > 10:
                raise Exception("failed to establish connection check the config")
            print(f"trying to reconnect attempt :- {self.reconnect_attempts}")
            self.reconnect_attempts += 1
            self.mqtt_client = self.connect_mqtt()
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise Exception("MongoDB connection failed.")
        
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                client.subscribe(self.MQTT_TOPIC, qos=self.MQTT_QOS)
                self.reconnect_attempts = 0
            else:
                if rc == 5:
                    raise Exception(
                        "Connection Refused: Not authorized. Please check your credentials."
                    )
                else:
                    print(f"Failed to connect, return code {rc}")

        def on_message(client, userdata, msg):
            print(f"Received message on {msg.topic}: {msg.payload.decode()}")
            data = json.loads(msg.payload)
            response = self.insert_json_to_mongo(data)

        client = mqtt_client.Client(f"Test_MQTT_Subscriber_{random.randint(0,99)}")
        client.username_pw_set(self.MQTT_USERNAME, self.MQTT_PASSWORD)
        client.on_connect = on_connect
        client.on_message = on_message
        
        try:
            client.connect(self.MQTT_HOST, self.MQTT_PORT)
        except ConnectionRefusedError as e:
            print(f"Connection to MQTT broker failed: {e}")
            time.sleep(5)  # Wait before retrying
            self.reconnect()
            
        return client

    def connect_mongo(self):
        # Connect to MongoDB with credentials
        uri = f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DATABASE}?authSource=admin"

        try:
            mongo_client = MongoClient(uri)
            self.db = mongo_client[self.MONGO_DATABASE]
            mongo_client.admin.command('ping')
            print("MongoDB connection successful.")

            if self.mongo_collection not in self.db.list_collection_names():
                print(f"`{self.mongo_collection}` collection not exists. crating the new collection")
                self.db.create_collection(
                    self.mongo_collection,
                    timeseries={
                        'timeField': 'timeStamp',
                        'metaField': 'Device',
                        'granularity': 'seconds'
                    }
                )

            else:
                print(f"`{self.mongo_collection}` collection previously exists. skipping the collection creation")
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise Exception("MongoDB connection failed.")
            
        return mongo_client

    # Function to insert JSON into MongoDB
    def insert_json_to_mongo(self, json_data):
        try:
            collection = self.db[self.mongo_collection]
            json_data['timeStamp'] = datetime.fromisoformat(json_data['timeStamp'])
            collection.insert_one(json_data)
            print("Data successfully inserted.")
            return True
        except Exception as e:
            print(f"An error occurred while inserting data: {e}")
            return False

    
    def start_loop(self):
        try:
            self.mqtt_client.loop_start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Interrupted by user, stopping MQTT client...")
            self.mqtt_client.disconnect()
if __name__ == "__main__":
    calss_instence = SubscribeData(Config_data['MQTT_CONFIG'], Config_data['MONGO_CONFIG'])
    calss_instence.start_loop()