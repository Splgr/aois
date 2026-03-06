from core.NumberRepresentation import NumberRepresentation
from core.BitArray import BitArray
from utils.RangeValidator import RangeValidator

class DirectCode(NumberRepresentation):
    def to_binary(self, number):
        RangeValidator.validate_signed_int32(number)
        
        bits = BitArray(size=self.bits)
        is_negative = number < 0
        num = abs(number)
        
        bits[0] = 1 if is_negative else 0
        
        idx = self.bits - 1
        while num > 0 and idx > 0:
            bits[idx] = num % 2
            num //= 2
            idx -= 1
        
        return bits
    
    def from_binary(self, bit_array):
        value = 0
        for i in range(1, self.bits):
            value = value * 2 + bit_array[i]
        
        if bit_array[0] == 1:
            value = -value
        
        return value
    
    def get_type(self):
        return "DirectCode"