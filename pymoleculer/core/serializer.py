from abc import ABC, abstractmethod

class Serializer(ABC):
    @abstractmethod
    def serialize(self, message):
        pass

    @abstractmethod
    def deserialize(self, message):
        pass