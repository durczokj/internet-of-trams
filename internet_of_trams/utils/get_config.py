import os
import yaml

def get_config():
    config_path = os.path.abspath(os.path.join(__file__, '..', '..', '..', "configuration.yaml"))
    
    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)
        
    return config
