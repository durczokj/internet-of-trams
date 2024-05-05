import os, sys, logging
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

from internet_of_trams.api.ztm_data_extractor import ZtmDataExtractor
from internet_of_trams.utils.get_config import get_config
import json
from kafka import KafkaProducer  
import time


def produce_appearances_of_vehicles(api_key, lines, topic):
    extractor = ZtmDataExtractor(api_key)

    appearances_of_vehicles = extractor.extract_appearances_of_vehicles_for_lines(lines)
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    for aov in appearances_of_vehicles:
        producer.send(topic, value=bytes(json.dumps(aov), encoding="UTF-8"))
        
    producer.close()

def main():
    config = get_config()     
    produce_appearances_of_vehicles(config["API_KEY"], config["LINES"], config["KAFKA_TOPIC"])

if __name__ == "__main__":
    try:
        while True:
            main()
            time.sleep(30)
    except KeyboardInterrupt:
        logging.info("Producer closing.")
