from core.ArithmeticOperation import ArithmeticOperation
from core.BitArray import BitArray

class DivideOperation(ArithmeticOperation):
    def __init__(self, bits=32, precision=5):
        self.bits = bits
        self.precision = precision
        self.multiplier = 10 ** precision  # 100000
    
    def execute(self, a, b):
        # 1. Знак результата
        sign = a[0] ^ b[0]
        
        # 2. Извлекаем модули (без знака)
        a_mag = self._get_magnitude(a)
        b_mag = self._get_magnitude(b)
        
        # 3. Конвертируем в числа
        a_val = self._to_int(a_mag)
        b_val = self._to_int(b_mag)
        
        if b_val == 0:
            raise ZeroDivisionError("Деление на ноль!")
        
        # 4. Делим модули
        quotient = a_val // b_val
        remainder = a_val % b_val
        
        # 5. Дробная часть (5 десятичных знаков)
        fractional = 0
        for _ in range(self.precision):
            remainder *= 10
            digit = remainder // b_val
            fractional = fractional * 10 + digit
            remainder = remainder % b_val
        
        # 6. Собираем: целая * 100000 + дробная
        result_value = quotient * self.multiplier + fractional
        
        # 7. Конвертируем в биты (31 бит для модуля)
        result_bits = self._from_int(result_value, self.bits - 1)
        
        # 8. Создаём финальный BitArray со знаком
        final = BitArray(size=self.bits)
        final[0] = sign  # Знак в первый бит
        
        # Копируем биты результата (справа налево, LSB → LSB)
        for i in range(self.bits - 1):
            src_idx = len(result_bits) - 1 - i
            dst_idx = self.bits - 1 - i
            if src_idx >= 0 and src_idx < len(result_bits):
                final[dst_idx] = result_bits[src_idx]
            else:
                final[dst_idx] = 0
        
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
        return "Division"