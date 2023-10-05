from abc import ABC, abstractmethod

class Transporter(ABC):
    @abstractmethod
    def send(self, topic, payload):
        pass

    @abstractmethod
    def receive(self, callback):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def on(self, event, callback):
        pass