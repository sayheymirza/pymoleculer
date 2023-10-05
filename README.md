<!-- create a readmoe of Python implementation of Moleculer framework -->
# Moleculer Python

[![PyPI version](https://badge.fury.io/py/moleculer-py.svg)](https://badge.fury.io/py/moleculer-py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python implementation of [Moleculer JS](https://moleculer.services/) framework.

# Installation
```bash
pip install pymoleculer
```

# Usage
```python
from pymoleculer.broker import MolecularBroker

broker = MolecularBroker(
    namespace="test",
    node="node-1",
    transporter="mqtt://localhost:1883",
    serializer="json",
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

```

## Features
- [x] Create a broker
- [x] Create a service with action decorators
- [x] Call an action from another service

## Roadmap
- [ ] Handle events
- [ ] Handle permissions on actions
- [ ] Improve disconnecting