from tortoise import Tortoise, run_async
from models import *

async def manage_product():
    await Tortoise.init(
        db_url="mysql://root:my-secret-pw@127.0.0.1:3306/internet_of_trams"
        ,modules={"models": ["models"]})
    
    await Tortoise.generate_schemas()

if __name__ == "__main__":
    run_async(manage_product())