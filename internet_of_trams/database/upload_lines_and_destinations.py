# Import Tortoise package
from tortoise import Tortoise, run_async
import os
# Import product schema
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))
from internet_of_trams.api.ztm_data_extractor import ZtmDataExtractor
from internet_of_trams.database.models import Line, Destination
from internet_of_trams.utils.get_config import get_config


async def manage_lines_and_destinations(database_password, api_key):
    await Tortoise.init(
        db_url=f"mysql://root:{database_password}@127.0.0.1:3306/internet_of_trams"
        ,modules={"models": ["internet_of_trams.database.models"]})
    
    extractor = ZtmDataExtractor(api_key)
    extractor.get_lines_and_destinations()
    
    for line in extractor.lines:
        # Check if the line already exists in the database
        existing_line = await Line.filter(id=line.id).first()
        if existing_line:
            # Update the existing record
            await existing_line.update_from_dict(line.__dict__)
        else:
            # Create a new record
            await line.save()
            
    for destination in extractor.destinations:
        # Check if the line already exists in the database
        existing_destination = await Destination.filter(line_id=destination.line_id, number=destination.number).first()
        if existing_destination:
            # Update the existing record
            await existing_destination.update_from_dict(destination.__dict__)
        else:
            # Create a new record
            await destination.save()

if __name__ == "__main__":
    config = get_config()
    run_async(manage_lines_and_destinations(config["DATABASE_PASSWORD"], config["API_KEY"]))
