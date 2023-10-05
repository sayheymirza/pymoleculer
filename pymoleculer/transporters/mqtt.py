# import mqtt as mqtt
import paho.mqtt.client as mqtt
# import abstract class
import pymoleculer.core.transporter

class MQTTTransporter(pymoleculer.core.transporter.Transporter):
    __client = None
    __username = None
    __password = None
    __host = None
    __port = 1883
    # local events
    __localEvents = {}

    def __init__(self, url=None):
        # if url is None or empty string, raise exception
        if not url:
            raise ValueError("MQTT URL cannot be empty")

        # parse url
        # mqtt://username:password@host:port
        # mqtt://host:port
        # mqtt://host

        # if url does not start with mqtt://, raise exception
        if not url.startswith("mqtt://"):
            raise ValueError("MQTT URL must start with mqtt://")

        # remove mqtt://
        url = url[7:]

        # if url contains @, parse username and password
        if "@" in url:
            # split url into two parts, before and after @
            username_password, host_port = url.split("@", 1)

            # split username_password into two parts, before and after :
            username, password = username_password.split(":", 1)

            # set username and password
            self.__username = username
            self.__password = password

            # split host_port into two parts, before and after :
            host, port = host_port.split(":", 1)

            # set host and port
            self.__host = host
            self.__port = port
        # else, parse host and port
        else:
            # split url into two parts, before and after :
            host, port = url.split(":", 1)

            # set host and port
            self.__host = host
            self.__port = port if port else "1883"

    def create(self):
        # create mqtt client
        self.__client = mqtt.Client()

        # set username and password
        if self.__username and self.__password:
            self.__client.username_pw_set(self.__username, self.__password)

        # connect to host
        self.__client.connect(self.__host, int(self.__port))

        # handle on_connect event
        def on_connect(client, userdata, flags, rc):
            # if connection is successful
            if rc == 0:
                # emit connected event
                self.__emit("connected", None)
            else:
                # emit error event
                self.__emit("error", "Connection failed")
                # throw exception
                raise Exception("Connection failed")

        # handle on_disconnect event
        def on_disconnect(client, userdata, rc):
            # emit disconnected event
            self.__emit("disconnected", None)

        # set on_connect event
        self.__client.on_connect = on_connect

        # set on_disconnect event
        self.__client.on_disconnect = on_disconnect

        # start loop
        self.__client.loop_forever(
            timeout=1.0, max_packets=1, retry_first_connection=True,
        )

    def close(self):
        # disconnect from host
        self.__client.disconnect()
         # stop loop
        self.__client.loop_stop()

    def send(self, topic, payload):
        # publish payload= to topic
        self.__client.publish(topic, payload)

    def receive(self, callback):
        # subscribe to topic
        self.__client.subscribe("#")

        # set callback
        self.__client.on_message = callback

    def on(self, event, callback):
        self.__localEvents[event] = callback
    
    def __emit(self, event, data=None):
        # check if event exists
        if event in self.__localEvents:
            # emit event if data is None
            if data is None:
                self.__localEvents[event]()
            else:
                self.__localEvents[event](data)