class RangeValidator:
    @staticmethod
    def validate_signed_int32(number):
        """Проверка диапазона для 32-битного знакового целого"""
        if not isinstance(number, int):
            raise ValueError("Ожидается целое число")
        if number < -2147483648 or number > 2147483647:
            raise OverflowError(
                f"Число {number} не помещается в 32-битный знаковый формат. "
                f"Диапазон: [-2147483648, 2147483647]"
            )
    
    @staticmethod
    def validate_unsigned_int32(number):
        """Проверка диапазона для 32-битного БЕЗзнакового целого"""
        if not isinstance(number, int):
            raise ValueError("Ожидается целое число")
        if number < 0 or number > 4294967295:
            raise OverflowError(
                f"Число {number} не помещается в 32-битный беззнаковый формат. "
                f"Диапазон: [0, 4294967295]"
            )
    
    @staticmethod
    def validate_bcd32(number):
        
        if not isinstance(number, int):
            raise ValueError("Ожидается целое число")
        if number < 0:
            raise ValueError(
                f"BCD-код поддерживает только положительные числа. "
                f"Вы ввели: {number}"
            )
        if number > 99999999:  
            raise OverflowError(
                f"Число {number} не помещается в BCD 32 бита. "
                f"Максимум: 99999999 (8 цифр)"
            )
    
    @staticmethod
    def validate_ieee754(number):
        """Проверка диапазона для IEEE-754 32 бита"""
        if not isinstance(number, (int, float)):
            raise ValueError("Ожидается вещественное число")
        MAX_IEEE754 = 3.4028235e38
        if abs(number) > MAX_IEEE754:
            raise OverflowError(
                f"Число {number} переполняет IEEE-754 32 бита. "
                f"Максимум: ~{MAX_IEEE754:.3e}"
            )