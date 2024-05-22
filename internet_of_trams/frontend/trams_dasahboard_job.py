import folium
from datetime import datetime
from dateutil.relativedelta import relativedelta

from internet_of_trams.api.ztm_data_extractor import ZtmDataExtractor
from tortoise import Tortoise
from internet_of_trams.database.models import *
from tortoise.expressions import Subquery
from internet_of_trams.api.database_connector import DatabaseConnector
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

def get_marker(appearance_of_vehicle, color_mapping):
    popup = get_popup_html(appearance_of_vehicle["id"], appearance_of_vehicle["line_id"], appearance_of_vehicle["timestamp"])

    color = color_mapping.get(appearance_of_vehicle["line_id"], 'black')

    return folium.Marker(
        location=[appearance_of_vehicle["latitude"], appearance_of_vehicle["longitude"]],
        popup=popup,
        icon=folium.Icon(color=color))
    
def get_poly_line(line_id, paths, color_mapping):
    return folium.PolyLine(paths[line_id], color=color_mapping.get(line_id, 'black'))

class TramsDashboardJob:
    def __init__(self,
                 database_host,
                 database_port,
                 database_password):
        self.__database_host = database_host
        self.__database_port = database_port
        self.__database_password = database_password
        
        self.__database_connector = DatabaseConnector(username = 'root', password = database_password, host = database_host, database="internet_of_trams")
    
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
            db_url=f"mysql://root:{self.__database_password}@{self.__database_host}:{self.__database_port}/internet_of_trams",
            modules={"models": ["internet_of_trams.database.models"]}
        )
        
        self.stops = await Stop.all()
        self.poles = await Pole.all()
        self.lines = await Line.all()
        self.destinations = await Destination.all()
        self.paths = await get_paths()
        
    def get_appearances_of_vehicles(self, lines):
        observation_cutoff = datetime.now() - relativedelta(minutes=5)
        observation_cutoff_str = observation_cutoff.strftime("%Y%m%d%H%m%S")
        extraction_cutoff = datetime.now() - relativedelta(minutes=2)
        extraction_cutoff_str = extraction_cutoff.strftime("%Y%m%d%H%m%S")
        
        if len(lines) == 0:
            return []
            
        lines_str = ", ".join(lines)
        lines_str = f"({lines_str})"

        query = f"""
            SELECT 
                v.id
                ,v.line_id
                ,v.type
                ,v.brigade
                ,a.longitude
                ,a.latitude
                ,a.timestamp
                ,a._extraction_timestamp
            FROM 
                appearance a 
            JOIN 
                vehicle v 
            ON 
                a.vehicle_id=v.id 
            WHERE 
                a.timestamp > STR_TO_DATE({observation_cutoff_str}, '%Y%m%d%H%i%s')
                AND a._extraction_timestamp > STR_TO_DATE({extraction_cutoff_str}, '%Y%m%d%H%i%s')
                AND a._extraction_timestamp = (SELECT MAX(_extraction_timestamp) FROM appearance s WHERE a.vehicle_id = s.vehicle_id)
                AND v.line_id IN {lines_str}
            """

        return self.__database_connector.execute(query).to_dict(orient="records")
    
    def get_map(self, lines, zoom=0, longitude_shift=0, latitude_shift=0):
        lines = [str(line) for line in lines]
        
        __zoom = 12 + zoom
        
        longitude = 21.0122 + (longitude_shift/250*1.8**(zoom))
        latitude = 52.2297 + (latitude_shift/100*1.2**(zoom))

        # Initialize the map
        map_warsaw = folium.Map(location=(latitude, longitude), zoom_start=__zoom, min_zoom=__zoom, zoom_control=False)
        
        # Get vehicles and appearances
        appearances_of_vehicles = self.get_appearances_of_vehicles(lines)
        
        # Get color mapping for lines
        color_mapping = get_color_mapping(lines)

        # Crate a marker for each appearance
        for aov in appearances_of_vehicles:
            get_marker(aov, color_mapping).add_to(map_warsaw)

        # Crate a poly-line for each line path
        for line_id in lines:
            get_poly_line(line_id, self.paths, color_mapping).add_to(map_warsaw)

        # Display the map
        return map_warsaw
    
    def get_map_html(self, lines, zoom=0, longitude_shift=0, latitude_shift=0):
        map = self.get_map(lines, zoom, longitude_shift, latitude_shift)
        return map.get_root().render()
