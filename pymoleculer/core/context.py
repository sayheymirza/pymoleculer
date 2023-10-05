class Context:
    params = {}
    meta = {}
    sender = None
    node = None
    requestId = None

    def __init__(self, params={}, meta={}, sender=None, node=None, requestId=None):
        self.params = params
        self.meta = meta
        self.sender = sender
        self.node = node
        self.requestId = requestId

    def call(action="", payload={}):
        pass
