from abc import ABC, abstractmethod

class ArithmeticOperation(ABC):
    @abstractmethod
    def execute(self, a, b):
        pass
    
    @abstractmethod
    def get_name(self):
        pass