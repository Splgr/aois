from core.BitArray import BitArray

class OutputFormatter:
    @staticmethod
    def format_result(operation, a_decimal, b_decimal, result_bits, result_decimal, code_type="Additional"):
        output = []
        output.append("=" * 60)
        output.append(f"Операция: {operation}")
        output.append(f"Код: {code_type}")
        output.append("-" * 60)
        
        # Для деления в DirectCode
        if code_type == "Direct" and "Деление" in operation:
            result_decimal = OutputFormatter._decode_division_result(result_bits)
            result_decimal = f"{result_decimal:.5f}"
        
        # Для IEEE-754: умное округление
        if code_type == "IEEE754":
            result_decimal = OutputFormatter._smart_round(result_decimal)
            a_decimal = OutputFormatter._smart_round(a_decimal)
            b_decimal = OutputFormatter._smart_round(b_decimal)
        
        output.append(f"Число A: {a_decimal} (10-й)")
        output.append(f"Число B: {b_decimal} (10-й)")
        output.append("-" * 60)
        output.append(f"Результат (2-й): {result_bits}")
        output.append(f"Результат (10-й): {result_decimal}")
        output.append("=" * 60)
        
        return "\n".join(output)
    
    @staticmethod
    def _smart_round(value, max_decimals=6):
        """
        Округляет число, убирая погрешности плавающей точки.
        Если число близко к «красивому» значению — округляет до него.
        """
        # Пробуем округлять с разной точностью, начиная с 2 знаков
        for decimals in range(2, max_decimals + 1):
            rounded = round(value, decimals)
            # Если после округления «хвост» исчез — возвращаем
            if abs(rounded - value) < 10 ** -(decimals + 1):
                # Форматируем без лишних нулей
                formatted = f"{rounded:.{decimals}f}".rstrip('0').rstrip('.')
                # Если дробная часть пустая — добавляем .0 для наглядности
                if '.' not in formatted:
                    formatted += '.0'
                return formatted
        
        # Если не удалось «очистить» — возвращаем стандартное округление
        return f"{round(value, max_decimals):.{max_decimals}f}".rstrip('0').rstrip('.')
    
    @staticmethod
    def _decode_division_result(bits):
        """Декодировать результат деления"""
        sign = -1 if bits[0] == 1 else 1
        value = 0
        for i in range(1, 32):
            value = value * 2 + bits[i]
        integer_part = value // 100000
        fractional_part = value % 100000
        return sign * (integer_part + fractional_part / 100000)