
import pandas as pd
import mysql.connector

class DatabaseConnector:
    class Params:
        def __init__(
            self,
            username,
            password,
            host,
            database):
            
            self.username = username
            self.password = password
            self.host = host
            self.database = database
    
    def __init__(
        self,
        username,
        password,
        host,
        database = None):
        
        self.params = DatabaseConnector.Params(username, password, host, database)
    
    @staticmethod
    def __parse_into_data_frame(cursor):
        column_names = cursor.column_names
        data = [element for element in cursor]
        return pd.DataFrame(data, columns=column_names)
        
        
    def __get_connection(self):
        p = self.params
        return mysql.connector.connect(
            user=p.username,
            password=p.password,
            host=p.host,
            database=p.database)
    
    def execute(self, query):
        connection = self.__get_connection()
        cursor = connection.cursor()
        
        cursor.execute(query)
        
        df = self.__parse_into_data_frame(cursor)
        
        cursor.close()
        connection.close()
        
        return df
