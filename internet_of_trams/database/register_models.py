import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

from internet_of_trams.api.database_connector import DatabaseConnector
from internet_of_trams.utils.get_config import get_config
from tortoise import Tortoise
from models import *

def register_schema(username, password, host, port):
    SCHEMA_NAME = "internet_of_trams"
    
    connector = DatabaseConnector(username, password, host, port)
    query = f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"
    connector.execute(query)


async def generate_tables(username, password, host, port):
    await Tortoise.init(
        db_url= f"mysql://{username}:{password}@{host}:{port}/internet_of_trams"
        ,modules={"models": ["models"]})
    
    await Tortoise.generate_schemas()

async def main():
    config = get_config()
    
    register_schema(config["DATABASE_USERNAME"], config["DATABASE_PASSWORD"], config["DATABASE_HOST"], config["DATABASE_PORT"])
    await generate_tables(config["DATABASE_USERNAME"], config["DATABASE_PASSWORD"], config["DATABASE_HOST"], config["DATABASE_PORT"])

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())