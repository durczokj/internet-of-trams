import subprocess, os, logging

logging.basicConfig(level=logging.INFO)

def run_app():
    REGISTER_MODELS_FILE_NAME = os.path.join("internet_of_trams", "database", "register_models.py")
    STOPS_AND_POLES_FILE_NAME = os.path.join("internet_of_trams", "database", "upload_stops_and_poles.py")
    LINES_AND_DESTINATIONS_FILE_NAME = os.path.join("internet_of_trams", "database", "upload_lines_and_destinations.py")
    APPEARANCES_AND_VEHICLES_FILE_NAME = os.path.join("internet_of_trams", "database", "upload_appearances_of_vehicles.py")
    APP_FILE_NAME = os.path.join("internet_of_trams", "frontend", "app.py")

    try:
        logging.info("Registering models...")
        subprocess.run(["python", REGISTER_MODELS_FILE_NAME])
        
        logging.info("Registering stops and poles...")
        subprocess.run(["python", STOPS_AND_POLES_FILE_NAME])
        
        logging.info("Registering lines and destinations...")
        subprocess.run(["python", LINES_AND_DESTINATIONS_FILE_NAME])
        
        logging.info("Registering appearances and vehicles...")
        aov = subprocess.Popen(["python", APPEARANCES_AND_VEHICLES_FILE_NAME])
        
        logging.info("Running app...")
        app = subprocess.Popen(["python", APP_FILE_NAME])
        
        aov.wait()
        app.wait()
        
    except KeyboardInterrupt:
        aov.kill()
        app.kill()
        
def main():
    run_app()


if __name__ == "__main__":
    main()