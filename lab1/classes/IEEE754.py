from core.NumberRepresentation import NumberRepresentation
from core.BitArray import BitArray
from utils.RangeValidator import RangeValidator

class IEEE754(NumberRepresentation):
    """IEEE-754 Single Precision (32 бита)"""
    
    SIGN_BITS = 1
    EXP_BITS = 8
    MANTISSA_BITS = 23
    BIAS = 127
    MAX_EXP = 255  # Все единицы в экспоненте
    MIN_EXP = 0    # Все нули в экспоненте
    
    def __init__(self):
        super().__init__(bits=32)
    
    def to_binary(self, number):
        """Конвертация float → 32 бита IEEE-754"""
        RangeValidator.validate_ieee754(number)
        bits = BitArray(size=self.bits)
        
        if number < 0:
            bits[0] = 1
            number = -number
        
        if number == 0:
            return bits
        
        exponent = 0
        temp = number
        while temp >= 2:
            temp /= 2
            exponent += 1
        while temp < 1 and temp > 0:
            temp *= 2
            exponent -= 1
        
        mantissa_value = temp - 1.0
        
        exp_encoded = exponent + self.BIAS

        if exp_encoded >= self.MAX_EXP:
            for i in range(self.EXP_BITS):
                bits[self.SIGN_BITS + i] = 1
            return bits
        
        if exp_encoded <= 0:
            return bits
        
        # Записываем экспоненту
        for i in range(self.EXP_BITS - 1, -1, -1):
            bits[self.SIGN_BITS + i] = exp_encoded % 2
            exp_encoded //= 2
        
        # Кодируем мантиссу с округлением
        mantissa_start = self.SIGN_BITS + self.EXP_BITS
        val = mantissa_value
        mantissa_bits = []
        
        for _ in range(self.MANTISSA_BITS + 1):  # +1 бит для округления
            val *= 2
            if val >= 1:
                mantissa_bits.append(1)
                val -= 1
            else:
                mantissa_bits.append(0)
        
        # Округление "к чётному"
        if mantissa_bits[23] == 1:
            carry = 1
            for i in range(22, -1, -1):
                s = mantissa_bits[i] + carry
                mantissa_bits[i] = s % 2
                carry = s // 2
                if carry == 0:
                    break
        
        # Записываем 23 бита мантиссы
        for i in range(self.MANTISSA_BITS):
            bits[mantissa_start + i] = mantissa_bits[i]
        
        return bits
    
    def from_binary(self, bit_array):
        """Конвертация 32 бита IEEE-754 → float"""
        sign = -1 if bit_array[0] == 1 else 1
        
        # Извлекаем экспоненту
        exp_value = 0
        for i in range(self.EXP_BITS):
            exp_value = exp_value * 2 + bit_array[self.SIGN_BITS + i]
        
        # Специальные значения
        if exp_value == self.MAX_EXP:  # 255
            # Проверяем мантиссу
            mantissa_start = self.SIGN_BITS + self.EXP_BITS
            if all(bit_array[i] == 0 for i in range(mantissa_start, self.bits)):
                return float('-inf') if sign == -1 else float('inf')
            else:
                return float('nan')  
            
        mantissa_value = 1.0 
        mantissa_start = self.SIGN_BITS + self.EXP_BITS
        
        for i in range(self.MANTISSA_BITS):
            mantissa_value += bit_array[mantissa_start + i] * (2 ** -(i + 1))
   
        if exp_value == 0:
            mantissa_value = 0.0  # Нет скрытой единицы
            for i in range(self.MANTISSA_BITS):
                mantissa_value += bit_array[mantissa_start + i] * (2 ** -(i + 1))
            return sign * mantissa_value * (2 ** (1 - self.BIAS))
        
        # Нормальное число
        real_exp = exp_value - self.BIAS
        result = sign * mantissa_value * (2 ** real_exp)
        
        return round(result, 6)

    
    def _get_exponent(self, bits):
        """Извлечь экспоненту как целое число"""
        exp = 0
        for i in range(self.EXP_BITS):
            exp = exp * 2 + bits[self.SIGN_BITS + i]
        return exp
    
    def _set_exponent(self, bits, exp):
        """Записать экспоненту в биты"""
        for i in range(self.EXP_BITS - 1, -1, -1):
            bits[self.SIGN_BITS + i] = exp % 2
            exp //= 2
    
    def _get_mantissa_float(self, bits):
        """Получить мантиссу как float (1.xxxx)"""
        mantissa = 1.0  
        for i in range(self.MANTISSA_BITS):
            if bits[self.SIGN_BITS + self.EXP_BITS + i] == 1:
                mantissa += 2 ** -(i + 1)
        return mantissa
    
    def _set_mantissa_from_float(self, bits, mantissa):
        """Установить мантиссу из float (1.xxxx)"""
        frac = mantissa - 1.0 
        for i in range(self.MANTISSA_BITS):
            frac *= 2
            if frac >= 1:
                bits[self.SIGN_BITS + self.EXP_BITS + i] = 1
                frac -= 1
            else:
                bits[self.SIGN_BITS + self.EXP_BITS + i] = 0
    
    def _handle_overflow(self, sign, exp):
        """Обработать переполнение экспоненты"""
        if exp >= self.MAX_EXP:
            # Возвращаем ±Infinity
            result = BitArray(size=self.bits)
            result[0] = sign
            for i in range(self.EXP_BITS):
                result[self.SIGN_BITS + i] = 1
            return result, True
        return None, False
    
    def _handle_underflow(self, sign, exp):
        """Обработать недополнение экспоненты"""
        if exp <= 0:
            # Возвращаем ±0
            result = BitArray(size=self.bits)
            result[0] = sign
            return result, True
        return None, False

    
    def add(self, a_bits, b_bits):
        """Сложение IEEE-754"""
        sign_a = a_bits[0]
        sign_b = b_bits[0]
        exp_a = self._get_exponent(a_bits)
        exp_b = self._get_exponent(b_bits)
        mant_a = self._get_mantissa_float(a_bits)
        mant_b = self._get_mantissa_float(b_bits)
        
        # Выравнивание экспонент
        if exp_a > exp_b:
            shift = exp_a - exp_b
            mant_b = mant_b / (2 ** shift)
            exp = exp_a
        elif exp_b > exp_a:
            shift = exp_b - exp_a
            mant_a = mant_a / (2 ** shift)
            exp = exp_b
        else:
            exp = exp_a
        
        # Сложение/вычитание мантисс
        if sign_a == sign_b:
            result_mant = mant_a + mant_b
            result_sign = sign_a
            # Нормализация если >= 2
            if result_mant >= 2.0:
                result_mant /= 2
                exp += 1
        else:
            # Разные знаки — вычитание
            if mant_a >= mant_b:
                result_mant = mant_a - mant_b
                result_sign = sign_a
            else:
                result_mant = mant_b - mant_a
                result_sign = sign_b
            
            # Нормализация если < 1
            if result_mant > 0 and result_mant < 1.0:
                while result_mant < 1.0 and exp > 0:
                    result_mant *= 2
                    exp -= 1
            elif result_mant == 0:
                result = BitArray(size=self.bits)
                return result
        
        overflow, handled = self._handle_overflow(result_sign, exp)
        if handled:
            return overflow
        
        underflow, handled = self._handle_underflow(result_sign, exp)
        if handled:
            return underflow
        
        # Сборка результата
        result = BitArray(size=self.bits)
        result[0] = result_sign
        self._set_exponent(result, exp)
        self._set_mantissa_from_float(result, result_mant)
        
        return result
    
    def subtract(self, a_bits, b_bits):
        """Вычитание: A - B = A + (-B)"""
        b_neg = b_bits.copy()
        b_neg[0] = 1 - b_neg[0]
        return self.add(a_bits, b_neg)
    
    def multiply(self, a_bits, b_bits):
        """Умножение IEEE-754"""
        sign = a_bits[0] ^ b_bits[0]
        exp_a = self._get_exponent(a_bits)
        exp_b = self._get_exponent(b_bits)
        mant_a = self._get_mantissa_float(a_bits)
        mant_b = self._get_mantissa_float(b_bits)
        
        # Экспонента: складываем и вычитаем bias
        exp = exp_a + exp_b - self.BIAS
        
        # Мантисса: умножение
        result_mant = mant_a * mant_b
        
        # Нормализация если >= 2
        if result_mant >= 2.0:
            result_mant /= 2
            exp += 1
        
        # Проверка на переполнение/недополнение
        overflow, handled = self._handle_overflow(sign, exp)
        if handled:
            return overflow
        
        underflow, handled = self._handle_underflow(sign, exp)
        if handled:
            return underflow
        
        # Сборка
        result = BitArray(size=self.bits)
        result[0] = sign
        self._set_exponent(result, exp)
        self._set_mantissa_from_float(result, result_mant)
        
        return result
    
    def divide(self, a_bits, b_bits):
        """Деление IEEE-754"""
        sign = a_bits[0] ^ b_bits[0]
        exp_a = self._get_exponent(a_bits)
        exp_b = self._get_exponent(b_bits)
        mant_a = self._get_mantissa_float(a_bits)
        mant_b = self._get_mantissa_float(b_bits)
        
        # Экспонента: вычитаем и добавляем bias
        exp = exp_a - exp_b + self.BIAS
        
        if mant_b == 0:
            raise ZeroDivisionError("Деление на ноль!")
        
        # Мантисса: деление
        result_mant = mant_a / mant_b
        
        # Нормализация
        if result_mant >= 2.0:
            result_mant /= 2
            exp += 1
        elif result_mant < 1.0 and result_mant > 0:
            while result_mant < 1.0 and exp > 0:
                result_mant *= 2
                exp -= 1
        
        # Проверка на переполнение/недополнение
        overflow, handled = self._handle_overflow(sign, exp)
        if handled:
            return overflow
        
        underflow, handled = self._handle_underflow(sign, exp)
        if handled:
            return underflow
        
        # Сборка
        result = BitArray(size=self.bits)
        result[0] = sign
        self._set_exponent(result, exp)
        self._set_mantissa_from_float(result, result_mant)
        
        return result
    
    def get_type(self):
        return "IEEE754"