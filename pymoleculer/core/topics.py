import psutil
import socket
# import uuid
import uuid
# topics
class Topic:
    _namespace = "default"
    _node = "node-1"

    def __init__(
            self,
            namespace="default",
            node="node-1",
    ):
        self._namespace = namespace
        self._node = node

    @property
    def DISCOVER(self):
        return {
            "topic": f"MOL-{self._namespace}.DISCOVER",
            "payload": {
                "ver": "4",
                "sender": self._node,
            }
        }

    @property
    def DISCONNECT(self):
        return {
            "topic": f"MOL-{self._namespace}.DISCONNECT",
            "payload": {
                "ver": "4",
                "sender": self._node,
            }
        }

    @property
    def HEARTBEAT(self):
        return {
            "topic": f"MOL-{self._namespace}.HEARTBEAT",
            "payload": {
                "ver": "4",
                "sender": self._node,
                "cpu": psutil.cpu_percent(1),
            }
        }

    def INFO(self, services = []):
        # create a instance id with uuid version 4
        instance_id = str(uuid.uuid4())
        # map services
        _services = [] 
        _map_services = {} # { [name: str]: index }

        for service in services:
            # if service[name] is not in _services
            if not any(_service["name"] == service["name"] for _service in _services):
                _services.append({
                    "name": service["name"],
                    "version": service["version"],
                    "fullName": service["fullName"],
                    "settings": {},
                    "metadata": {},
                    "actions": {},
                    "events": {}
                })
                _map_services[service["name"]] = len(_services) - 1

        # fill _services
        for service in services:
            index = _map_services[service["name"]]
            if "action" in service:
                action = service["action"]
                
                _services[index]["actions"][action["name"]] = {
                    "rest": action["rest"] if "rest" in action else None,
                    "rawName": action["rawName"],
                    "name": action["name"],
                    "params": action["params"],
                }
                

        return {
            "topic": f"MOL-{self._namespace}.INFO",
            "payload": {
                "ver": "4",
                "sender": self._node,
                "instanceID": instance_id,
                "services": _services,
                "client": {
                    "type": "python",
                    "version": "0.1",
                    "langVersion": "v0.1"
                },
                "config": {},
                "metadata": {},
                "hostname": socket.gethostname(),
                "ipList": [
                    socket.gethostbyname(socket.gethostname()),
                ],
                "seq": 2,
            }
        }

    def RESPONSE(self, ctx, result):
        return {
            "topic": f"MOL-{self._namespace}.RES.{ctx.sender}",
            "payload": {
                "id": ctx.requestId,
                "meta": ctx.meta,
                "success": True,
                "data": result,
                "ver": "4",
                "sender": self._node
            }
        }

    def REQUEST(self, node, action, params, meta):
        return {
            "topic": f"MOL-{self._namespace}.REQ.{node}",
            "payload": {
                "ver": "4",
                "sender": self._node,
                "id": str(uuid.uuid4()),
                "params": params,
                "meta": meta,
                "action": action
            }
        }
