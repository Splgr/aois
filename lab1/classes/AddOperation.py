from core.ArithmeticOperation import ArithmeticOperation
from core.BitArray import BitArray
from core.exceptions import OverflowError

class AddOperation(ArithmeticOperation):
    def __init__(self, bits=32):
        self.bits = bits  
    
    def execute(self, a, b):
        result = BitArray(size=self.bits)
        carry = 0
        
        for i in range(self.bits - 1, -1, -1):
            total = a[i] + b[i] + carry
            result[i] = total % 2
            carry = total // 2
        
        if a[0] == b[0] and result[0] != a[0]:
            raise OverflowError("Переполнение при сложении!")
        
        return result
    
    def get_name(self):
        return "Addition"