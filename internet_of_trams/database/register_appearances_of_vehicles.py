import os, json, sys, logging
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))
from internet_of_trams.utils.get_config import get_config
from internet_of_trams.database.models import *
from internet_of_trams.api.database_connector import DatabaseConnector
from tortoise import Tortoise, run_async
from kafka import KafkaConsumer

config = get_config()

def from_kafka_log(function):
    def wrapper(message):
        data = json.loads(message.value)
        return function(data)
    return wrapper

from internet_of_trams.api.ztm_data_extractor import parse_appearance, parse_vehicle

parse_appearance = from_kafka_log(parse_appearance)
parse_vehicle = from_kafka_log(parse_vehicle)

def clear_vehicles(username, password, host, port):
    connector = DatabaseConnector(username, password, host, port)
    query = f"DELETE FROM internet_of_trams.vehicle WHERE id != 1"
    connector.execute(query)

async def create_or_update_vehicle(vehicle):
    # Check if the line already exists in the database
    existing_vehicle = await Vehicle.filter(id=vehicle.id).first()
    if existing_vehicle:
        # Update the existing record
        await existing_vehicle.update_from_dict(vehicle.__dict__)
    else:
        # Create a new record
        await vehicle.save()
        
async def create_or_update_appearance(appearance):
    # Check if the line already exists in the database
    existing_appearance = await Appearance.filter(vehicle_id=appearance.vehicle_id, _extraction_timestamp = appearance._extraction_timestamp).first()
    if not existing_appearance:
        # Create a new record
        await appearance.save()

async def register_incoming_appearances_of_vehicles(database_host, database_password, topic, kafka_host):   
    await Tortoise.init(
        db_url=f"mysql://root:{database_password}@{database_host}:3306/internet_of_trams"
        ,modules={"models": ["internet_of_trams.database.models"]})

    consumer = KafkaConsumer(topic, bootstrap_servers=kafka_host, auto_offset_reset='latest')
    
    try:
        for msg in consumer:
            appearance = parse_appearance(msg)
            vehicle = parse_vehicle(msg)
            await create_or_update_vehicle(vehicle)
            await create_or_update_appearance(appearance)
    except KeyboardInterrupt:
        logging.info("Consumer closing.")
        consumer.close()
        
def main():
    config = get_config()
    clear_vehicles(config["DATABASE_USERNAME"], config["DATABASE_PASSWORD"], config["DATABASE_HOST"], config["DATABASE_PORT"])
    run_async(register_incoming_appearances_of_vehicles(config["DATABASE_HOST"], config["DATABASE_PASSWORD"], config["KAFKA_TOPIC"], config["KAFKA_HOST"]))
        
if __name__ == "__main__":
    main()