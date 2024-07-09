# rabbitmq-data-pipeline

This repository contains a RabbitMQ pipeline with five services, including a RabbitMQ and MQTT broker, MongoDB for data storage, a FastAPI app, and data publisher and subscriber services.

## Getting Started

### Configuration

Before starting the application, edit the configuration files to include the required details:

1. **MQTT Configuration:**
   - Navigate to the root directory.
   - Open the `mqtt_config.yaml` file and add the necessary details such as rabbitmq MQTT broker host, port, username, and password.

2. **MongoDB Configuration:**
   - In the same `mqtt_config.yaml` file, add the mongo db detials such as host, port, username, and password.
   - Navigate to the `FastAPI_app` folder.
   - Open the `config.yaml` file and fill in the mongo db detials.

### Starting the Application

#### Using Docker

1. Navigate to the root folder.
2. Run the following command to start the application using Docker:
   ```sh
   docker-compose up
   ```

#### Using Terminal

1. Navigate to the root directory.
2. Create a virtual environment by executing the following command:
   ```sh
   python -m venv rabitmqapp
   ```
   This will create a virtual environment named `rabitmqapp`.

3. Activate the virtual environment:
   - **Windows:**
     ```sh
     .\rabitmqapp\Scripts\activate -- this will activate virtual environment
     ```
   - **Linux:**
     ```sh
     source ./rabitmqapp/bin/activate -- this will activate virtual environment
     ```

4. Install the required dependencies:
    - this will install all dependency libraries
   ```sh
   pip install -r requirements.txt
   ```

5. Start the services:
   - To start the data subscriber:
     ```sh
     python data_subscriber.py
     ```
   - To start the data publisher:
     ```sh
     python data_publisher.py
     ```

6. Start the FastAPI app:
   - Navigate to the `FastAPI_app` folder.
   1. Install the required dependencies:
        ```sh
        pip install -r requirements.txt
        ```
        - this will install all dependency libraries
   - Execute the following command:
     ```sh
     python main.py
     ```
     - This will start the FastAPI app.

## Services

This start five services:
1. **RabbitMQ and MQTT Broker:**
   - Handles the message brokering between the data publisher and subscriber.

2. **MongoDB:**
   - Stores the data received from the data publisher.

3. **FastAPI App:**
   - Connects to mongo and creates endpoint that takes start and end times in a payload and returns count of status of each unique status 
   - Endpoint URL: `http://127.0.0.1:8000/getdata`
   - Payload example:
     ```json
     {
       "startTime": "09-07-2024 00:00:00",
       "endTime": "10-07-2024 00:00:00"
     }
     ```
   - Response example:
     ```json
     [
       {
         "status": 0,
         "count": 221
       },
       ...
     ]
     ```

4. **Data Publisher:**
   - Publishes data to the rabbitmq mqtt broker.

5. **Data Subscriber:**
   - Subscribes to the data from the rabbitmq mqtt broker and inserts it into mongo db.

### Note

- Ensure the configuration files are correctly set up before starting the application.
- If running in Docker, the provided Docker Compose file will handle the setup and execution of the services.
- For manual startup via terminal, ensure the virtual environment is activated and dependencies are installed before running the services.