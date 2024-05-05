
import subprocess

def upload_appearances_of_vehicles():
    REGISTRATOR_FILE_NAME = "register_appearances_of_vehicles.py"
    PRODUCER_FILE_NAME = "produce_appearances_of_vehicles.py"

    try:
        registrator = subprocess.Popen(["python", REGISTRATOR_FILE_NAME])
        producer = subprocess.Popen(["python", PRODUCER_FILE_NAME])
        
        registrator.wait()
        producer.wait()
        
    except KeyboardInterrupt:
        registrator.kill()
        producer.kill()
        
def main():
    upload_appearances_of_vehicles()


if __name__ == "__main__":
    main()
