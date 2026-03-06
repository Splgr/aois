from core.NumberRepresentation import NumberRepresentation
from core.BitArray import BitArray
from utils.RangeValidator import RangeValidator

class AdditionalCode(NumberRepresentation):
    def __init__(self, bits=32):
        self.bits = bits
    
    def to_binary(self, number):
        RangeValidator.validate_signed_int32(number)
        
        bits = BitArray(size=self.bits)
        
        if number == -2147483648:
            bits[0] = 1
            return bits
        
        if number >= 0:
            bits[0] = 0 
            num = number
            idx = self.bits - 1
            while num > 0 and idx > 0:
                bits[idx] = num % 2
                num //= 2
                idx -= 1
            return bits
        
        # Отрицательные числа (кроме -2147483648)
        # Алгоритм: инвертировать биты модуля + 1
        bits[0] = 1  # Знак = 1
        num = abs(number)
        
        # Записываем модуль в биты
        temp_bits = BitArray(size=self.bits)
        idx = self.bits - 1
        while num > 0 and idx > 0:
            temp_bits[idx] = num % 2
            num //= 2
            idx -= 1
        
        # Инвертируем биты (кроме знака)
        for i in range(1, self.bits):
            bits[i] = 1 - temp_bits[i]
        
        # Прибавляем 1
        carry = 1
        for i in range(self.bits - 1, 0, -1):
            total = bits[i] + carry
            bits[i] = total % 2
            carry = total // 2
            if carry == 0:
                break
        
        return bits
    
    def from_binary(self, bit_array):
        # ✅ ОСОБЫЙ СЛУЧАЙ: 10000000000000000000000000000000 = -2147483648
        if bit_array[0] == 1 and all(b == 0 for b in bit_array.bits[1:]):
            return -2147483648
        
        # Положительные числа
        if bit_array[0] == 0:
            value = 0
            for i in range(1, self.bits):
                value = value * 2 + bit_array[i]
            return value
        
        # Отрицательные числа (инвертировать + 1)
        temp = bit_array.copy()
        
        # Инвертируем биты (кроме знака)
        for i in range(1, self.bits):
            temp[i] = 1 - temp[i]
        
        # Прибавляем 1
        carry = 1
        for i in range(self.bits - 1, 0, -1):
            total = temp[i] + carry
            temp[i] = total % 2
            carry = total // 2
            if carry == 0:
                break
        
        # Вычисляем значение
        value = 0
        for i in range(1, self.bits):
            value = value * 2 + temp[i]
        
        return -value
    
    def get_type(self):
        return "AdditionalCode"