# core
import pymoleculer.core.topics
import pymoleculer.core.context
# transporters
import pymoleculer.transporters.mqtt
# serializers
import pymoleculer.serializers.json

import threading

class MoleculerBroker:
    __namespace = ""
    __node = ""

    __transporter = None

    __serializer = None

    __topic = pymoleculer.core.topics.Topic()

    '''
    Array of all services in node that we render it for sending INFO to other nodes
    '''
    __services = []

    '''
    All actions in node
    { [actionName]: func }
    '''
    __actions = {}


    '''
    All events in node happen
    { [eventName]: func }
    '''
    __events = {}

    '''
    All events in library happen
    { [eventName]: func }
    '''
    __localEvents = {}


    '''
    All actions from other nodes
    { [actionName]: "nodeId" }
    '''
    __info = {
        "actions": {}
    }


    '''
    All requests waits for response
    { [requestId]: None | { ... response value ... } }
    '''
    __requests = {}


    '''
    All threads are running
    '''
    __threads = {}

    def __init__(
        self,
        namespace="",
        node="",
        transporter=None,
        serializer="JSON"
    ):
        self.__namespace = namespace
        self.__node = node

        if transporter is not None:
            # if transporter startsWith mqtt://
            if transporter.startswith("mqtt://"):
                self.__transporter = pymoleculer.transporters.mqtt.MQTTTransporter(url=transporter)
            else:
                raise Exception("Transporter is not supported")

        # uppercase serializer
        serializer = serializer.upper()

        if serializer == "JSON":
            self.__serializer = pymoleculer.serializers.json.JSONSerializer()

        # set topic
        self.__topic = pymoleculer.core.topics.Topic(
            namespace=self.__namespace,
            node=self.__node
        )

    def start(self):
        self.__transporter.on("connected", self.__on_connect)

        self.__transporter.on("disconnect", self.__on_disconnect)

        self.__transporter.create()

    def __on_connect(self):
        # 0. emit connected event
        self.__emit_local_event("connected", None)

        # 1. send INFO to other nodes
        _info = self.__topic.INFO(
            self.__services
        )
        self.__send(
            topic=_info["topic"],
            payload=_info["payload"]
        )

        # 2. send DISCOVER to other nodes
        _discover = self.__topic.DISCOVER
        self.__send(
            topic=_discover["topic"],
            payload=_discover["payload"]
        )

        # 3. start heartbeat
        self.__heartbeat()

        # 4. subscribe to all topics
        def _on_message(client, userdata, msg):
            self.__threads["message"] = threading.Thread(target=self.__on_message, args=(msg.topic, msg.payload))
            self.__threads["message"].start()
        
        self.__transporter.receive(_on_message)

        # 5. emit ready event
        self.__emit_local_event("ready", None)


    def __on_message(self, topic, payload):
        # deserialize payload
        payload = self.__serializer.deserialize(payload)
        # emit event
        self.__emit_local_event("message", {
            "topic": topic,
            "payload": payload
        })
        # handle topic
        self.__handle_topic(topic, payload)

    def __on_disconnect(self):
        # 1. stop heartbeat
        self.__threads["heartbeat"].cancel()
        
        # 2. stop message thread
        self.__threads["message"].cancel()

        # 3. emit disconnected event to other nodes
        _disconnected = self.__topic.DISCONNECTED
        self.__send(
            topic=_disconnected["topic"],
            payload=_disconnected["payload"]
        )

        # 4. close transporter
        self.__transporter.close()

        # 5. emit disconnected event
        self.__emit_local_event("disconnected", None)


    def __heartbeat(self):
        # 1. send heartbeat message
        _heartbeat = self.__topic.HEARTBEAT
        
        self.__send(
            topic=_heartbeat["topic"],
            payload=_heartbeat["payload"]
        )

        # 2. resend heartbeat message after 10 seconds
        self.__threads["heartbeat"] = threading.Timer(10, self.__heartbeat)
        self.__threads["heartbeat"].start()
    
    def __handle_topic(self, topic, payload):
        # if topic includes ".INFO.{nodeId}"
        if f".INFO.{self.__node}" in topic:
            self.__handle_topic_info(payload)
        # if topic includes ".DISCOVER"
        elif ".DISCOVER" in topic:
            self.__handle_topic_discover(payload)
        # if topic includes ".REQ.{nodeId}"
        elif f".REQ.{self.__node}" in topic:
            self.__handle_topic_request(payload)
        # if topic includes ".RES.{nodeId}"
        elif f".RES.{self.__node}" in topic:
            self.__handle_topic_response(payload)

    def __handle_topic_info(self, payload):
        # map actions
        for service in payload["services"]:
            for action in service["actions"]:
                # if action is string
                if isinstance(action, str):
                    self.__info["actions"][action] = {
                        "node": payload["sender"]
                    }
        # emit event
        self.__emit_local_event("info", payload["sender"])

    def __handle_topic_discover(self, payload):
        # send INFO to other nodes
        _info = self.__topic.INFO(
            self.__services
        )

    def __handle_topic_request(self, payload):
        action = payload["action"]
        # check if action exists
        if action in self.__actions:
            # make context
            ctx = pymoleculer.core.context.Context(
                node=self.__node,
                sender=payload["sender"],
                requestId=payload["id"],
                params=payload["params"],
                meta=payload["meta"]
            )
            # change call method in ctx
            def call(action, payload={}):
                return self.call(action, payload, meta=ctx.meta)
            
            ctx.call = call

            # call action
            result = self.__actions[action](ctx)
            # if result is not None
            if result != None:
                # send response to sender
                _response = self.__topic.RESPONSE(
                    ctx=ctx,
                    result=result
                )

                self.__send(
                    topic=_response["topic"],
                    payload=_response["payload"]
                )

    def __handle_topic_response(self, payload):
        # check if request exists
        if payload["id"] in self.__requests:
            # set request value
            self.__requests[payload["id"]] = payload

    def __emit_local_event(self, event, data):
        # check if event exists
        if event in self.__localEvents:
            # emit event
            self.__localEvents[event](data)

    def __send(self, topic, payload):
        # serialize payload
        payload = self.__serializer.serialize(payload)
        
        # send payload to topic
        self.__transporter.send(
            topic=topic,
            payload=payload
        )

    def on(self, event, callback):
        self.__localEvents[event] = callback

    def call(self, action, params={}, meta={}):
        # check if action exists in info
        if action in self.__info["actions"]:
            # get node id
            node_id = self.__info["actions"][action]["node"]


            # make request
            _request = self.__topic.REQUEST(
                node=node_id,
                action=action,
                params=params,
                meta=meta
            )

            # send request
            self.__send(
                topic=_request["topic"],
                payload=_request["payload"]
            )

            # get request id
            request_id = _request["payload"]["id"]

            # set request value to None
            self.__requests[request_id] = None

            # wait for response
            while self.__requests[request_id] == None:
                pass

            # get response
            _response = self.__requests[request_id].copy()

            # delete request
            del self.__requests[request_id]

            # return response
            return _response["data"]
        else:
            raise Exception(f"Action {action} is not exists in node")

    def action(self, service=None, version="v1", rest=None, params={}):
        def decorator(func):
            # get func name
            func_name = func.__name__

            _service = {
                "name": service,
                "version": version,
                "fullName": version + "." + service,
                "action": {
                    "rest": rest if rest != None else None,
                    "rawName": func_name,
                    "name": version + "." + service + "." + func_name,
                    "params": params
                }
            }

            self.__services.append(_service)

            self.__actions[_service["action"]["name"]] = func

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator