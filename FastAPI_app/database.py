import yaml
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    with open("config.yaml", "r") as file:
        Config_data = yaml.safe_load(file)
except Exception as e:
    print("Got an error while fetching config please check restart program")
    print("Config " + repr(e) + " unable read config ")

MONGO_data = Config_data['MONGO_CONFIG']
MONGO_HOST = MONGO_data["HOST"]
MONGO_PORT = MONGO_data["PORT"]
MONGO_USERNAME = MONGO_data["USERNAME"]
MONGO_PASSWORD = MONGO_data["PASSWORD"]
MONGO_DATABASE = MONGO_data["DATABASE"]

def get_database(retries=10, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource=admin"
            mongo_client = MongoClient(uri)
            db = mongo_client[MONGO_DATABASE]
            mongo_client.admin.command('ping')
            print("MongoDB connection successful.")
            return db
        except ConnectionFailure as e:
            attempt += 1
            print(f"Attempt {attempt}/{retries}: Could not connect to MongoDB: {e}")
            if attempt >= retries:
                print("Exceeded maximum retry attempts. MongoDB connection failed.")
                raise Exception("MongoDB connection failed after multiple attempts.")
            time.sleep(delay)