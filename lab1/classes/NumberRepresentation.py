from abc import ABC, abstractmethod
from core.BitArray import BitArray

class NumberRepresentation(ABC):
    def __init__(self, bits=32):
        self.bits = bits
    
    @abstractmethod
    def to_binary(self, number):
        pass
    
    @abstractmethod
    def from_binary(self, bit_array):
        pass
    
    @abstractmethod
    def get_type(self):
        pass

