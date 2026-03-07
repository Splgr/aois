from core.BitArray import BitArray
from representations.DirectCode import DirectCode
from representations.ReverseCode import ReverseCode
from representations.AdditionalCode import AdditionalCode
from representations.IEEE754 import IEEE754
from representations.BCD8421Code import BCD8421Code
from operations.AddOperation import AddOperation
from operations.SubstractOperation import SubtractOperation
from operations.MultiplyOperation import MultiplyOperation
from operations.DivideOperation import DivideOperation
from operations.OutputFormatter import OutputFormatter
from utils.RangeValidator import RangeValidator

def print_separator(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def get_int_input(prompt, validator_func):
    """Запрашивает ввод целого числа с проверкой диапазона"""
    while True:
        try:
            value = int(input(prompt))
            validator_func(value)
            return value
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
            print("   Попробуйте ввести число заново.\n")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("   Попробуйте ввести число заново.\n")

def get_float_input(prompt, validator_func):
    """Запрашивает ввод вещественного числа с проверкой диапазона"""
    while True:
        try:
            value = float(input(prompt))
            validator_func(value)
            return value
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
            print("   Попробуйте ввести число заново.\n")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("   Попробуйте ввести число заново.\n")

def main():
    print("ЛАБОРАТОРНАЯ РАБОТА 1")
    print("Представление чисел в памяти компьютера")
    
    # =========================================================================
    # ПУНКТ 1: Все коды
    # =========================================================================
    print_separator("ПУНКТ 1: Прямой, Обратный, Дополнительный код")
    
    a = get_int_input("Введите число A (целое): ", RangeValidator.validate_signed_int32)
    b = get_int_input("Введите число B (целое): ", RangeValidator.validate_signed_int32)
    
    direct = DirectCode(32)
    reverse = ReverseCode(32)
    additional = AdditionalCode(32)
    
    print(f"\nЧисло A = {a}")
    print(f"Прямой код:     {direct.to_binary(a)}")
    print(f"Обратный код:   {reverse.to_binary(a)}")
    print(f"Дополнительный: {additional.to_binary(a)}")
    
    print(f"\nЧисло B = {b}")
    print(f"Прямой код:     {direct.to_binary(b)}")
    print(f"Обратный код:   {reverse.to_binary(b)}")
    print(f"Дополнительный: {additional.to_binary(b)}")
    
    # =========================================================================
    # ПУНКТ 2-3: Сложение/Вычитание (Дополнительный код)
    # =========================================================================
    print_separator("ПУНКТ 2-3: Сложение/Вычитание (Доп. код)")
    
    try:
        bits_a = additional.to_binary(a)
        bits_b = additional.to_binary(b)
        
        add_op = AddOperation(32)
        result_add = add_op.execute(bits_a, bits_b)
        result_add_dec = additional.from_binary(result_add)
        
        print(OutputFormatter.format_result("Сложение (A + B)", a, b, result_add, result_add_dec, "Additional"))
        
        sub_op = SubtractOperation(32)
        result_sub = sub_op.execute(bits_a, bits_b)
        result_sub_dec = additional.from_binary(result_sub)
        
        print(OutputFormatter.format_result("Вычитание (A - B)", a, b, result_sub, result_sub_dec, "Additional"))
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # =========================================================================
    # ПУНКТ 4-5: Умножение/Деление (Прямой код)
    # =========================================================================
    print_separator("ПУНКТ 4-5: Умножение/Деление (Прямой код)")
    
    try:
        bits_a_dir = direct.to_binary(a)
        bits_b_dir = direct.to_binary(b)
        
        mul_op = MultiplyOperation(32)
        result_mul = mul_op.execute(bits_a_dir, bits_b_dir)
        result_mul_dec = direct.from_binary(result_mul)
        
        print(OutputFormatter.format_result("Умножение (A * B)", a, b, result_mul, result_mul_dec, "Direct"))
        
        # ✅ ВАЖНО: 16 бит на дробную часть (согласовано с OutputFormatter)
        div_op = DivideOperation(32, frac_bits=16)
        result_div = div_op.execute(bits_a_dir, bits_b_dir)
        result_div_dec = 0  # Декодирование происходит в OutputFormatter
        
        print(OutputFormatter.format_result("Деление (A / B)", a, b, result_div, result_div_dec, "Direct"))
        
    except ZeroDivisionError as e:
        print(f"❌ Ошибка: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # =========================================================================
    # ПУНКТ 6: IEEE-754 (вещественные числа)
    # =========================================================================
    print_separator("ПУНКТ 6: IEEE-754 (вещественные числа)")
    
    try:
        a_float = get_float_input("\nВведите число A (вещественное): ", RangeValidator.validate_ieee754)
        b_float = get_float_input("Введите число B (вещественное): ", RangeValidator.validate_ieee754)
        
        ieee = IEEE754()
        bits_a = ieee.to_binary(a_float)
        bits_b = ieee.to_binary(b_float)
        
        print(f"\nA в IEEE-754: {bits_a}")
        print(f"B в IEEE-754: {bits_b}")
        
        # Сложение
        result_add_bits = ieee.add(bits_a, bits_b)
        result_add_dec = ieee.from_binary(result_add_bits)
        print(OutputFormatter.format_result("Сложение (A + B)", a_float, b_float, result_add_bits, result_add_dec, "IEEE754"))
        
        # Вычитание
        result_sub_bits = ieee.subtract(bits_a, bits_b)
        result_sub_dec = ieee.from_binary(result_sub_bits)
        print(OutputFormatter.format_result("Вычитание (A - B)", a_float, b_float, result_sub_bits, result_sub_dec, "IEEE754"))
        
        # Умножение
        result_mul_bits = ieee.multiply(bits_a, bits_b)
        result_mul_dec = ieee.from_binary(result_mul_bits)
        print(OutputFormatter.format_result("Умножение (A * B)", a_float, b_float, result_mul_bits, result_mul_dec, "IEEE754"))
        
        # Деление
        result_div_bits = ieee.divide(bits_a, bits_b)
        result_div_dec = ieee.from_binary(result_div_bits)
        print(OutputFormatter.format_result("Деление (A / B)", a_float, b_float, result_div_bits, result_div_dec, "IEEE754"))
        
    except ZeroDivisionError as e:
        print(f"❌ Ошибка: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # =========================================================================
    # ПУНКТ 7: BCD 8421 (только положительные числа)
    # =========================================================================
    print_separator("ПУНКТ 7: BCD 8421")
    print("⚠️  BCD поддерживает только положительные числа!\n")
    
    try:
        a_bcd = get_int_input("Введите число A (BCD, макс 8 цифр, ≥0): ", RangeValidator.validate_bcd32)
        b_bcd = get_int_input("Введите число B (BCD, макс 8 цифр, ≥0): ", RangeValidator.validate_bcd32)
        
        bcd = BCD8421Code()
        bits_a_bcd = bcd.to_binary(a_bcd)
        bits_b_bcd = bcd.to_binary(b_bcd)
        
        print(f"\nA в BCD: {bits_a_bcd}")
        print(f"B в BCD: {bits_b_bcd}")
        
        result_bcd = bcd.add_with_correction(bits_a_bcd, bits_b_bcd)
        result_bcd_dec = bcd.from_binary(result_bcd)
        
        print(OutputFormatter.format_result("Сложение BCD", a_bcd, b_bcd, result_bcd, result_bcd_dec, "BCD8421"))
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # =========================================================================
    # Завершение
    # =========================================================================
    print("\n" + "=" * 60)
    print("  Лабораторная работа завершена!")
    print("=" * 60)

if __name__ == "__main__":
    main()
