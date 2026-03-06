from core.NumberRepresentation import NumberRepresentation
from core.BitArray import BitArray
from utils.RangeValidator import RangeValidator

class ReverseCode(NumberRepresentation):
    def to_binary(self, number):
        RangeValidator.validate_signed_int32(number)
        
        from representations.DirectCode import DirectCode
        
        direct = DirectCode(self.bits)
        bits = direct.to_binary(number)
        
        if number < 0:
            bits.invert(start=1)
        
        return bits
    
    def from_binary(self, bit_array):
        from representations.DirectCode import DirectCode
        
        if bit_array[0] == 0:
            return DirectCode(self.bits).from_binary(bit_array)
        else:
            temp = bit_array.copy()
            temp.invert(start=1)
            value = 0
            for i in range(1, self.bits):
                value = value * 2 + temp[i]
            return -value
    
    def get_type(self):
        return "ReverseCode"