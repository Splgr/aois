from core.ArithmeticOperation import ArithmeticOperation
from core.BitArray import BitArray

class MultiplyOperation(ArithmeticOperation):
    def __init__(self, bits=32):
        self.bits = bits
    
    def execute(self, a, b):
        # 1. Знак результата (XOR знаков)
        sign = a[0] ^ b[0]
        
        # 2. Извлекаем модули (31 бит без знака)
        a_mag = self._get_magnitude(a)
        b_mag = self._get_magnitude(b)
        
        # 3. Конвертируем модули в числа
        a_val = self._to_int(a_mag)
        b_val = self._to_int(b_mag)
        
        # 4. Умножаем
        product = a_val * b_val
        
        # 5. Конвертируем результат обратно в биты (31 бит)
        result_bits = self._from_int(product, self.bits - 1)
        
        # 6. Создаём финальный BitArray
        final = BitArray(size=self.bits)
        final[0] = sign
        
        # Копируем биты результата (защита от index out of range)
        for i in range(self.bits - 1):
            bit_index = len(result_bits) - 1 - i
            if bit_index >= 0:
                final[self.bits - 1 - i] = result_bits[bit_index]
            else:
                final[self.bits - 1 - i] = 0
        
        return final
    
    def _get_magnitude(self, bits):
        """Извлечь 31 бит без знака"""
        mag = []
        for i in range(1, len(bits)):
            mag.append(bits[i])
        return mag
    
    def _to_int(self, bit_list):
        """Конвертировать список битов в число"""
        value = 0
        for bit in bit_list:
            value = value * 2 + bit
        return value
    
    def _from_int(self, num, size):
        """Конвертировать число в список битов (MSB first)"""
        if num == 0:
            return [0] * size
        
        bits = []
        temp = num
        for _ in range(size):
            bits.append(temp % 2)
            temp //= 2
        
        bits.reverse()  # Теперь MSB first
        return bits
    
    def get_name(self):
        return "Multiplication"