from pymoleculer.broker import MoleculerBroker
# import dotenv
from dotenv import load_dotenv

import os

# load .env file from
load_dotenv()

broker = MoleculerBroker(
    namespace="doting",
    node="test-server",
    transporter=os.getenv("MQTT")
)

@broker.action(
    service="hello",
    version="api.v1",
    rest="GET /",
    params={
        "name": {
            "type": "string",
            "optional": True,
            "default": "World"
        }
    }
)
def hello(ctx):
    name = ctx.params["name"] if "name" in ctx.params else "World"

    data = ctx.call("api.v1.search.search" ,{
        "type": "product"
    })

    return {
        "status": True,
        "code": 200,
        "error": -1,
        "message": f"Hello {name}!",
        "data": data
    }

broker.start()