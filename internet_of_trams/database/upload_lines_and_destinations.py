# Import Tortoise package
from tortoise import Tortoise, run_async
import os
# Import product schema
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))
from internet_of_trams.api.ztm_data_extractor import ZtmDataExtractor
from internet_of_trams.database.models import Line, Destination


async def manage_lines_and_destinations():
    await Tortoise.init(
        db_url="mysql://root:my-secret-pw@127.0.0.1:3306/internet_of_trams"
        ,modules={"models": ["internet_of_trams.database.models"]})
    
    extractor = ZtmDataExtractor(api_key="12b8f222-5689-4177-9ac2-01ff1229c098")
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

run_async(manage_lines_and_destinations())