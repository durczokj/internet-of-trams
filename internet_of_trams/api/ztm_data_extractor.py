from internet_of_trams.api.ztm_connector import ZtmConnector
from internet_of_trams.database.models import *
from datetime import datetime
import pytz


class ZtmDataExtractor:
    def __init__(self, api_key):
        self.__connector = ZtmConnector(api_key)
    
    def get_vehicles_and_appearances(self, lines):
        def extract_appearances_of_vehicles(vehicle_type, line, connector):
            URL = "https://api.um.warszawa.pl/api/action/busestrams_get/"

            type_mapping = {"bus": 1, "tram": 2}
            if vehicle_type not in type_mapping:
                raise ValueError("Vehicle type must be either tram or bus.")

            params = {
                "resource_id": "f2e5503e-927d-4ad3-9500-4ab9e55deb59"
                ,"type": type_mapping[vehicle_type]
                ,"line": line
            }
            
            return connector.get(URL, params)

        VEHICLE_TYPE = "tram"
        
        appearances_of_vehicles = []
        
        for line in lines:
            appearances_of_vehicles += extract_appearances_of_vehicles(VEHICLE_TYPE, line, self.__connector)
            
        self.vehicles = []
        self.appearances = []

        for aov in appearances_of_vehicles:
            self.vehicles.append(
                Vehicle(
                    id = int(aov["VehicleNumber"])
                    ,type = "tram"
                    ,line_id = aov["Lines"]
                    ,brigade = int(aov["Lines"])))

            self.appearances.append(
                Appearance(
                    vehicle_id = int(aov["VehicleNumber"])
                    ,timestamp = datetime.strptime(aov["Time"], '%Y-%m-%d %H:%M:%S')
                    ,latitude = float(aov["Lat"])
                    ,longitude = float(aov["Lon"])))
        
            
    def get_lines_and_destinations(self):
        def extract_lines_and_destinations(connector):
            URL = "https://api.um.warszawa.pl/api/action/public_transport_routes/"
            return connector.get(URL)

        def get_longest_route(routes):
            max_length = max([len(route) for route in routes.values()])
            longest_route = {key: value for key, value in routes.items() if len(value) == max_length}

            name = list(longest_route.keys())[0]
            destinations = list(longest_route.values())[0]

            return name, destinations

        lines_and_destinations = extract_lines_and_destinations(self.__connector)

        self.lines = []
        self.destinations = []

        for line_id, routes in lines_and_destinations.items():
            id = line_id
            
            name, destinations = get_longest_route(routes)
            
            for key, item in sorted(destinations.items(), key=lambda x: int(x[0])):
                self.destinations.append(
                    Destination(
                        id = len(self.destinations) + 1
                        ,line_id = id
                        ,number = int(key)
                        ,stop_id = item["nr_zespolu"]
                        ,pole_number = int(item["nr_przystanku"])))
                        
            self.lines.append(Line(id = id, name=name))
            
    def get_stops_and_poles(self):
        def extract_stops_and_poles(connector):
            URL = "https://api.um.warszawa.pl/api/action/dbstore_get/"
            PARAMS = {"id": "1c08a38c-ae09-46d2-8926-4f9d25cb0630"}
            
            return connector.get(URL, PARAMS)
        
        result = extract_stops_and_poles(self.__connector)

        result_restructured = []

        for item in result:
            values_dict = {}
            for value_item in item['values']:
                values_dict[value_item['key']] = value_item['value']
            result_restructured.append(values_dict)
            
        self.stops = []
        self.poles = []

        for stop_id, stop_name in set([(element["zespol"], element["nazwa_zespolu"]) for element in result_restructured]):
            for pole in [element for element in result_restructured if element["zespol"] == stop_id]:
                self.poles.append(
                    Pole(
                        id = len(self.poles) + 1
                        ,stop_id = stop_id
                        ,number = int(pole["slupek"])
                        ,longitude=float(pole["dlug_geo"])
                        ,latitude=float(pole["szer_geo"])))
            self.stops.append(
                Stop(
                    id = stop_id
                    ,name = stop_name))

