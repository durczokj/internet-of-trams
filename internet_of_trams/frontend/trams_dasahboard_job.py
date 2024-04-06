import folium
from datetime import datetime
from dateutil.relativedelta import relativedelta

from internet_of_trams.api.ztm_data_extractor import ZtmDataExtractor
from tortoise import Tortoise
from internet_of_trams.database.models import *
import pytz 


COLOR_LIST = ['darkred',
              'orange',
              'pink',
              'darkpurple',
              'blue',
              'cadetblue',
              'black',
              'gray',
              'purple',
              'green',
              'darkgreen',
              'darkblue',
              'beige',
              'red']

WARSAW_COORDINATES = (52.2297, 21.0122)

def get_popup_html(vehicle_id, line, timestamp):
    CSS = """
        <style>
        .leaflet-popup-content-wrapper {
            width: 200px;
        }
        </style>
    """

    info = {
        "vehicle_id": vehicle_id,
        "line": line,
        "date": timestamp.strftime('%Y-%m-%d'),
        "time": timestamp.strftime('%H:%M:%S')}
    
    html_output = '\n'.join([f'<p>{key}: {item}</p>' for key, item in info.items()])
    
    return CSS + html_output

def get_color_mapping(lines):
    color_mapping = {}
    for i, line in enumerate(lines):
        index = round(i*len(COLOR_LIST)/len(lines))
        color_mapping[line] = COLOR_LIST[index]
    return color_mapping

def get_marker(appearance, vehicles, color_mapping):
    latitude, longitude = appearance.latitude, appearance.longitude
    vehicle_id = appearance.vehicle_id
    line = [vehicle.line_id for vehicle in vehicles if vehicle.id == vehicle_id][0]
    timestamp = appearance.timestamp

    popup = get_popup_html(vehicle_id, line, timestamp)

    color = color_mapping.get(line, 'black')

    return folium.Marker(
        location=[latitude, longitude],
        popup=popup,
        icon=folium.Icon(color=color))
    
def get_poly_line(line_id, paths, color_mapping):
    return folium.PolyLine(paths[line_id], color=color_mapping.get(line_id, 'black'))

class TramsDashboardJob:
    def __init__(self,
                 ztm_api_key,
                 database_password):
        self.__extractor = ZtmDataExtractor(api_key=ztm_api_key)
        self.__database_password = database_password
    
    @staticmethod
    def filter_recent_appearances(appearances):
        observation_cutoff = datetime.now(pytz.utc) - relativedelta(minutes=5)
        return [appearance for appearance in appearances if appearance.timestamp > observation_cutoff]
        
    async def get_static_data(self):
        async def get_paths():
            lines = await Line.all().prefetch_related('destinations')
            paths = {}
            for line in lines:
                path = []
                for destination in line.destinations:
                    pole = await Pole.filter(stop_id=destination.stop_id, number=destination.pole_number).first()
                    if pole:
                        path.append((pole.latitude, pole.longitude))
                
                paths[line.id] = path
            return paths

        await Tortoise.init(
            db_url=f"mysql://root:{self.__database_password}@127.0.0.1:3306/internet_of_trams",
            modules={"models": ["internet_of_trams.database.models"]}
        )
        
        self.stops = await Stop.all()
        self.poles = await Pole.all()
        self.lines = await Line.all()
        self.destinations = await Destination.all()
        self.paths = await get_paths()
        
    def get_vehicles_and_appearances(self, lines):
        self.__extractor.get_vehicles_and_appearances(lines = lines)
        
        return self.__extractor.vehicles, self.__extractor.appearances
        
    def show_trams(self, lines):
        lines = [str(line) for line in lines]

        # Initialize the map
        map_warsaw = folium.Map(location=WARSAW_COORDINATES, zoom_start=12)
        
        # Get vehicles and appearances
        vehicles, appearances = self.get_vehicles_and_appearances(lines)
        
        # Filter appearances
        recent_appearances = self.filter_recent_appearances(appearances)
        
        # Get color mapping for lines
        color_mapping = get_color_mapping(lines)

        # Crate a marker for each appearance
        for appearance in recent_appearances:
            get_marker(appearance, vehicles, color_mapping).add_to(map_warsaw)

        # Crate a poly-line for each line path
        for line_id in lines:
            get_poly_line(line_id, self.paths, color_mapping).add_to(map_warsaw)

        # Display the map
        display(map_warsaw)
