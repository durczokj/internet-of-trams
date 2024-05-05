import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

from internet_of_trams.api.database_connector import DatabaseConnector
from internet_of_trams.utils.get_config import get_config
from tortoise import Tortoise
from models import *

def register_schema(username, password, host):
    connector = DatabaseConnector(username, password, host)
    query = "CREATE SCHEMA IF NOT EXISTS internet_of_trams"
    connector.execute(query)


async def generate_tables(username, password, host):
    await Tortoise.init(
        db_url= f"mysql://{username}:{password}@{host}:3306/internet_of_trams"
        ,modules={"models": ["models"]})
    
    await Tortoise.generate_schemas()

async def main():
    config = get_config()
    
    register_schema(config["DATABASE_USERNAME"], config["DATABASE_PASSWORD"], config["DATABASE_HOST"])
    await generate_tables(config["DATABASE_USERNAME"], config["DATABASE_PASSWORD"], config["DATABASE_HOST"])

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())