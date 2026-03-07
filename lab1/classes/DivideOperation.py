from core.ArithmeticOperation import ArithmeticOperation
from core.BitArray import BitArray

class DivideOperation(ArithmeticOperation):
    def __init__(self, bits=32, frac_bits=16):
        self.bits = bits
        self.frac_bits = frac_bits
    
    def execute(self, a, b):
        # 1. Определяем знак результата
        sign = a[0] ^ b[0]
        
        # 2. Преобразуем в целые числа (без учета знака)
        a_val = self._bitarray_to_int(a, include_sign=False)
        b_val = self._bitarray_to_int(b, include_sign=False)
        
        if b_val == 0:
            raise ZeroDivisionError("Деление на ноль!")
        
        # 3. Для деления с фиксированной точкой сдвигаем делимое
        #    на количество дробных битов
        dividend = a_val << self.frac_bits
        
        # 4. Выполняем деление
        quotient = dividend // b_val
        
        # 5. Ограничиваем размер результата
        max_val = (1 << (self.bits - 1)) - 1
        if quotient > max_val:
            raise OverflowError("Переполнение результата")
        
        # 6. Создаем BitArray
        result = BitArray(size=self.bits)
        result[0] = sign
        
        # Заполняем остальные биты
        for i in range(1, self.bits):
            bit = (quotient >> (self.bits - 1 - i)) & 1
            result[i] = bit
            
        return result
    
    def _bitarray_to_int(self, bit_array, include_sign=True):
        """Преобразует BitArray в целое число"""
        result = 0
        start_idx = 0 if include_sign else 1
        
        for i in range(start_idx, self.bits):
            result = result * 2 + bit_array[i]
            
        return result
    
    def get_name(self):
        return f"Fixed Point Division ({self.frac_bits} fractional bits)"