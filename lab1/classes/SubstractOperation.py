from core.ArithmeticOperation import ArithmeticOperation
from core.BitArray import BitArray

class SubtractOperation(ArithmeticOperation):
    def __init__(self, bits=32):
        self.bits = bits
        from operations.AddOperation import AddOperation
        self.add_op = AddOperation(bits)
    
    def negate(self, bits: BitArray):
        result = bits.copy()
        result.invert()
        result.add_one()
        return result
    
    def execute(self, a, b):
        neg_b = self.negate(b)
        return self.add_op.execute(a, neg_b)
    
    def get_name(self):
        return "Subtraction"