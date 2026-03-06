from core.NumberRepresentation import NumberRepresentation
from core.BitArray import BitArray
from utils.RangeValidator import RangeValidator

class BCD8421Code(NumberRepresentation):
    BITS_PER_DIGIT = 4
    MAX_DIGITS = 7  # 31 бит / 4 = 7 полных тетрад + 1 бит знака
    
    def __init__(self):
        super().__init__(bits=32)
        self.encoding_table = {
            0: [0, 0, 0, 0], 1: [0, 0, 0, 1], 2: [0, 0, 1, 0],
            3: [0, 0, 1, 1], 4: [0, 1, 0, 0], 5: [0, 1, 0, 1],
            6: [0, 1, 1, 0], 7: [0, 1, 1, 1], 8: [1, 0, 0, 0],
            9: [1, 0, 0, 1]
        }
        self.decoding_table = {tuple(v): k for k, v in self.encoding_table.items()}
    
    def to_binary(self, number):
        RangeValidator.validate_bcd32(number)
        
        bits = BitArray(size=self.bits)
        is_negative = number < 0
        num_str = str(abs(number))
        
        # Бит 0 — знак
        bits[0] = 1 if is_negative else 0
        
        # Кодируем цифры справа налево
        # Первая цифра (справа) идёт в биты 28-31, вторая в 24-27 и т.д.
        digit_index = 0
        for digit_char in reversed(num_str):
            digit = int(digit_char)
            digit_bits = self.encoding_table[digit]
            
            # Позиция тетрады: последняя = биты 28-31, предпоследняя = 24-27
            tetra_start = self.bits - 4 - (digit_index * 4)
            
            if tetra_start < 1:  # Не вышли за пределы (бит 0 — знак)
                break
            
            # Записываем 4 бита тетрады
            for j in range(4):
                bits[tetra_start + j] = digit_bits[j]
            
            digit_index += 1
        
        return bits
    
    def from_binary(self, bit_array):
        is_negative = bit_array[0] == 1
        
        number_str = ""
        
        # Читаем тетрады справа налево, начиная с битов 28-31
        tetra_start = self.bits - 4
        
        while tetra_start >= 1:
            # Извлекаем 4 бита тетрады
            digit_bits = tuple(bit_array[tetra_start + j] for j in range(4))
            
            if digit_bits in self.decoding_table:
                digit = self.decoding_table[digit_bits]
                number_str = str(digit) + number_str
            
            tetra_start -= 4
        
        value = int(number_str) if number_str else 0
        return -value if is_negative else value
    
    def add_with_correction(self, bits1, bits2):
        result = BitArray(size=self.bits)
        carry = 0
        
        # Обрабатываем тетрады справа налево
        tetra_start = self.bits - 4
        
        while tetra_start >= 1:
            # Извлекаем значение первой тетрады
            val1 = 0
            for j in range(4):
                val1 = val1 * 2 + bits1[tetra_start + j]
            
            # Извлекаем значение второй тетрады
            val2 = 0
            for j in range(4):
                val2 = val2 * 2 + bits2[tetra_start + j]
            
            # Складываем с переносом
            tetra_sum = val1 + val2 + carry
            
            # BCD-коррекция: если сумма > 9, добавляем 6
            if tetra_sum > 9:
                tetra_sum += 6
            
            # Новый перенос и значение тетрады
            carry = tetra_sum // 16
            tetra_sum = tetra_sum % 16
            
            # Записываем результат в тетраду
            for j in range(3, -1, -1):
                result[tetra_start + j] = tetra_sum % 2
                tetra_sum //= 2
            
            tetra_start -= 4
        
        # Копируем бит знака
        result[0] = bits1[0]
        
        return result
    
    def get_type(self):
        return "BCD8421"