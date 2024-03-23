# Import Tortoise package
from tortoise import Tortoise, run_async
# Import product schema
import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))
from internet_of_trams.api.ztm_data_extractor import ZtmDataExtractor
from internet_of_trams.database.models import Stop, Pole


async def manage_stops_and_poles():
    await Tortoise.init(
        db_url="mysql://root:my-secret-pw@127.0.0.1:3306/internet_of_trams"
        ,modules={"models": ["internet_of_trams.database.models"]})
    
    iot = ZtmDataExtractor(api_key="12b8f222-5689-4177-9ac2-01ff1229c098")
    iot.get_stops_and_poles()
    
    for stop in iot.stops:
        # Check if the line already exists in the database
        existing_stop = await Stop.filter(id=stop.id).first()
        if existing_stop:
            # Update the existing record
            await existing_stop.update_from_dict(stop.__dict__)
        else:
            # Create a new record
            await stop.save()
            
    for pole in iot.poles:
        # Check if the line already exists in the database
        existing_pole = await Pole.filter(stop_id=pole.stop_id, number=pole.number).first()
        if existing_pole:
            # Update the existing record
            await existing_pole.update_from_dict(pole.__dict__)
        else:
            # Create a new record
            await pole.save()

run_async(manage_stops_and_poles())