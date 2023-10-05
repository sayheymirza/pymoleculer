# import json
import json

import pymoleculer.core.serializer

class JSONSerializer(pymoleculer.core.serializer.Serializer):
    def serialize(self, message):
        return json.dumps(message)

    def deserialize(self, message):
        return json.loads(message)