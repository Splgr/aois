#!/usr/bin/env python3
"""
Комплексные тесты для лабораторной работы №1
Представление чисел в памяти компьютера
"""

import unittest
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.BitArray import BitArray
from core.exceptions import InvalidBitArrayError, OverflowError

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


# =============================================================================
# ТЕСТЫ BITARRAY
# =============================================================================

class TestBitArray(unittest.TestCase):
    """Тесты класса BitArray"""
    
    def test_init_default(self):
        """Создание BitArray по умолчанию (32 бита, все 0)"""
        ba = BitArray()
        self.assertEqual(len(ba), 32)
        self.assertEqual(str(ba), '0' * 32)
    
    def test_init_custom_size(self):
        """Создание BitArray с custom размером"""
        ba = BitArray(size=8)
        self.assertEqual(len(ba), 8)
    
    def test_init_with_bits(self):
        """Создание BitArray из списка битов"""
        bits = [1, 0, 1, 0]
        ba = BitArray(bits=bits, size=4)
        self.assertEqual(str(ba), '1010')
    
    def test_getitem_setitem(self):
        """Доступ к битам по индексу"""
        ba = BitArray(size=8)
        ba[0] = 1
        ba[7] = 1
        self.assertEqual(ba[0], 1)
        self.assertEqual(ba[7], 1)
    
    def test_setitem_invalid(self):
        """Установка недопустимого значения бита"""
        ba = BitArray(size=8)
        with self.assertRaises(InvalidBitArrayError):
            ba[0] = 2
    
    def test_copy(self):
        """Копирование BitArray"""
        ba1 = BitArray(size=8)
        ba1[0] = 1
        ba2 = ba1.copy()
        ba2[0] = 0
        self.assertEqual(ba1[0], 1)  # Оригинал не изменился
        self.assertEqual(ba2[0], 0)
    
    def test_invert(self):
        """Инверсия битов"""
        ba = BitArray(bits=[0, 1, 0, 1], size=4)
        ba.invert()
        self.assertEqual(str(ba), '1010')
    
    def test_invert_range(self):
        """Инверсия в диапазоне"""
        ba = BitArray(bits=[0, 0, 0, 0], size=4)
        ba.invert(start=1, end=3)
        self.assertEqual(str(ba), '0110')
    
    def test_add_one(self):
        """Прибавление 1"""
        ba = BitArray(bits=[0, 0, 0, 1], size=4)
        ba.add_one()
        self.assertEqual(str(ba), '0010')
    
    def test_add_one_carry(self):
        """Прибавление 1 с переносом"""
        ba = BitArray(bits=[0, 1, 1, 1], size=4)
        ba.add_one()
        self.assertEqual(str(ba), '1000')
    
    def test_str(self):
        """Строковое представление"""
        ba = BitArray(bits=[1, 0, 1, 0], size=4)
        self.assertEqual(str(ba), '1010')


# =============================================================================
# ТЕСТЫ КОДОВ (Direct, Reverse, Additional)
# =============================================================================

class TestDirectCode(unittest.TestCase):
    def setUp(self):
        self.direct = DirectCode(32)
    
    def test_positive_number(self):
        bits = self.direct.to_binary(5)
        self.assertEqual(self.direct.from_binary(bits), 5)
    
    def test_negative_number(self):
        bits = self.direct.to_binary(-5)
        self.assertEqual(self.direct.from_binary(bits), -5)
    
    def test_zero(self):
        bits = self.direct.to_binary(0)
        self.assertEqual(self.direct.from_binary(bits), 0)
    
    def test_max_positive(self):
        """Максимальное положительное"""
        bits = self.direct.to_binary(2147483647)
        self.assertEqual(self.direct.from_binary(bits), 2147483647)
    
    def test_min_negative(self):
        """Минимальное отрицательное для прямого кода"""
        # -2147483647, а НЕ -2147483648 (он не влезает в прямой код)
        bits = self.direct.to_binary(-2147483647)
        self.assertEqual(self.direct.from_binary(bits), -2147483647)


class TestReverseCode(unittest.TestCase):
    def setUp(self):
        self.reverse = ReverseCode(32)
    
    def test_positive_number(self):
        bits = self.reverse.to_binary(5)
        self.assertEqual(self.reverse.from_binary(bits), 5)
    
    def test_negative_number(self):
        bits = self.reverse.to_binary(-5)
        self.assertEqual(self.reverse.from_binary(bits), -5)
    
    def test_zero(self):
        bits = self.reverse.to_binary(0)
        self.assertEqual(self.reverse.from_binary(bits), 0)
    
    def test_min_negative(self):
        """Минимальное для обратного кода"""
        bits = self.reverse.to_binary(-2147483647)
        self.assertEqual(self.reverse.from_binary(bits), -2147483647)


class TestAdditionalCode(unittest.TestCase):
    def setUp(self):
        self.additional = AdditionalCode(32)
    
    def test_positive_number(self):
        bits = self.additional.to_binary(5)
        self.assertEqual(self.additional.from_binary(bits), 5)
    
    def test_negative_number(self):
        bits = self.additional.to_binary(-5)
        self.assertEqual(self.additional.from_binary(bits), -5)
    
    def test_zero(self):
        bits = self.additional.to_binary(0)
        self.assertEqual(self.additional.from_binary(bits), 0)
    
    def test_minus_one(self):
        """-1 (все единицы в доп. коде)"""
        bits = self.additional.to_binary(-1)
        self.assertEqual(self.additional.from_binary(bits), -1)
    
    def test_max_negative(self):
        """-2147483648 (особый случай — работает только в доп. коде)"""
        bits = self.additional.to_binary(-2147483648)
        self.assertEqual(self.additional.from_binary(bits), -2147483648)
    
    def test_roundtrip(self):
        """Конвертация туда-обратно для разных чисел"""
        # Для дополнительного кода -2147483648 допустим
        test_values = [0, 1, -1, 100, -100, 2147483647, -2147483648]
        for val in test_values:
            bits = self.additional.to_binary(val)
            result = self.additional.from_binary(bits)
            self.assertEqual(result, val, f"Failed for {val}")


# =============================================================================
# ТЕСТЫ АРИФМЕТИЧЕСКИХ ОПЕРАЦИЙ
# =============================================================================

class TestAddOperation(unittest.TestCase):
    """Тесты сложения"""
    
    def setUp(self):
        self.add = AddOperation(32)
        self.additional = AdditionalCode(32)
    
    def test_positive_add(self):
        """Сложение положительных"""
        a = self.additional.to_binary(5)
        b = self.additional.to_binary(3)
        result = self.add.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), 8)
    
    def test_negative_add(self):
        """Сложение отрицательных"""
        a = self.additional.to_binary(-5)
        b = self.additional.to_binary(-3)
        result = self.add.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), -8)
    
    def test_mixed_add(self):
        """Сложение разных знаков"""
        a = self.additional.to_binary(5)
        b = self.additional.to_binary(-3)
        result = self.add.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), 2)
    
    def test_add_zero(self):
        """Сложение с нулём"""
        a = self.additional.to_binary(10)
        b = self.additional.to_binary(0)
        result = self.add.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), 10)


class TestSubtractOperation(unittest.TestCase):
    """Тесты вычитания"""
    
    def setUp(self):
        self.sub = SubtractOperation(32)
        self.additional = AdditionalCode(32)
    
    def test_positive_subtract(self):
        """Вычитание положительных"""
        a = self.additional.to_binary(10)
        b = self.additional.to_binary(3)
        result = self.sub.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), 7)
    
    def test_negative_result(self):
        """Отрицательный результат"""
        a = self.additional.to_binary(3)
        b = self.additional.to_binary(10)
        result = self.sub.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), -7)
    
    def test_subtract_negative(self):
        """Вычитание отрицательного (фактически сложение)"""
        a = self.additional.to_binary(5)
        b = self.additional.to_binary(-3)
        result = self.sub.execute(a, b)
        self.assertEqual(self.additional.from_binary(result), 8)


class TestMultiplyOperation(unittest.TestCase):
    """Тесты умножения"""
    
    def setUp(self):
        self.mul = MultiplyOperation(32)
        self.direct = DirectCode(32)
    
    def test_positive_multiply(self):
        """Умножение положительных"""
        a = self.direct.to_binary(5)
        b = self.direct.to_binary(4)
        result = self.mul.execute(a, b)
        self.assertEqual(self.direct.from_binary(result), 20)
    
    def test_negative_multiply(self):
        """Умножение с отрицательным"""
        a = self.direct.to_binary(-5)
        b = self.direct.to_binary(4)
        result = self.mul.execute(a, b)
        self.assertEqual(self.direct.from_binary(result), -20)
    
    def test_both_negative(self):
        """Умножение двух отрицательных"""
        a = self.direct.to_binary(-5)
        b = self.direct.to_binary(-4)
        result = self.mul.execute(a, b)
        self.assertEqual(self.direct.from_binary(result), 20)
    
    def test_zero_multiply(self):
        """Умножение на ноль"""
        a = self.direct.to_binary(5)
        b = self.direct.to_binary(0)
        result = self.mul.execute(a, b)
        self.assertEqual(self.direct.from_binary(result), 0)
    
    def test_multiply_by_one(self):
        """Умножение на 1"""
        a = self.direct.to_binary(42)
        b = self.direct.to_binary(1)
        result = self.mul.execute(a, b)
        self.assertEqual(self.direct.from_binary(result), 42)


class TestDivideOperation(unittest.TestCase):
    """Тесты деления"""
    
    def setUp(self):
        self.div = DivideOperation(32, 5)
        self.direct = DirectCode(32)
    
    def test_positive_divide(self):
        """Деление положительных"""
        a = self.direct.to_binary(10)
        b = self.direct.to_binary(2)
        result = self.div.execute(a, b)
        value = self.direct.from_binary(result) / 100000
        self.assertAlmostEqual(value, 5.0, places=5)
    
    def test_fractional_divide(self):
        """Деление с дробной частью"""
        a = self.direct.to_binary(7)
        b = self.direct.to_binary(2)
        result = self.div.execute(a, b)
        value = self.direct.from_binary(result) / 100000
        self.assertAlmostEqual(value, 3.5, places=5)
    
    def test_negative_divide(self):
        """Деление с отрицательным результатом"""
        a = self.direct.to_binary(7)
        b = self.direct.to_binary(-2)
        result = self.div.execute(a, b)
        value = self.direct.from_binary(result) / 100000
        self.assertAlmostEqual(value, -3.5, places=5)
    
    def test_divide_by_zero(self):
        """Деление на ноль"""
        a = self.direct.to_binary(10)
        b = self.direct.to_binary(0)
        with self.assertRaises(ZeroDivisionError):
            self.div.execute(a, b)


# =============================================================================
# ТЕСТЫ IEEE-754
# =============================================================================

class TestIEEE754(unittest.TestCase):
    """Тесты IEEE-754"""
    
    def setUp(self):
        self.ieee = IEEE754()
    
    def test_conversion_positive(self):
        """Конвертация положительного числа"""
        bits = self.ieee.to_binary(5.5)
        result = self.ieee.from_binary(bits)
        self.assertAlmostEqual(result, 5.5, places=4)
    
    def test_conversion_negative(self):
        """Конвертация отрицательного числа"""
        bits = self.ieee.to_binary(-5.5)
        result = self.ieee.from_binary(bits)
        self.assertAlmostEqual(result, -5.5, places=4)
    
    def test_conversion_zero(self):
        """Конвертация нуля"""
        bits = self.ieee.to_binary(0.0)
        result = self.ieee.from_binary(bits)
        self.assertEqual(result, 0.0)
    
    def test_addition(self):
        """Сложение"""
        a = self.ieee.to_binary(5.5)
        b = self.ieee.to_binary(3.5)
        result = self.ieee.add(a, b)
        res_val = self.ieee.from_binary(result)
        self.assertAlmostEqual(res_val, 9.0, places=4)
    
    def test_subtraction(self):
        """Вычитание"""
        a = self.ieee.to_binary(10.0)
        b = self.ieee.to_binary(3.0)
        result = self.ieee.subtract(a, b)
        res_val = self.ieee.from_binary(result)
        self.assertAlmostEqual(res_val, 7.0, places=4)
    
    def test_multiplication(self):
        """Умножение"""
        a = self.ieee.to_binary(5.0)
        b = self.ieee.to_binary(4.0)
        result = self.ieee.multiply(a, b)
        res_val = self.ieee.from_binary(result)
        self.assertAlmostEqual(res_val, 20.0, places=4)
    
    def test_division(self):
        """Деление"""
        a = self.ieee.to_binary(10.0)
        b = self.ieee.to_binary(2.0)
        result = self.ieee.divide(a, b)
        res_val = self.ieee.from_binary(result)
        self.assertAlmostEqual(res_val, 5.0, places=4)
    
    def test_negative_addition(self):
        """Сложение с отрицательным"""
        a = self.ieee.to_binary(8.99)
        b = self.ieee.to_binary(-3.45)
        result = self.ieee.add(a, b)
        res_val = self.ieee.from_binary(result)
        self.assertAlmostEqual(res_val, 5.54, places=2)


# =============================================================================
# ТЕСТЫ BCD8421
# =============================================================================

class TestBCD8421(unittest.TestCase):
    """Тесты BCD 8421"""
    
    def setUp(self):
        self.bcd = BCD8421Code()
    
    def test_conversion_positive(self):
        """Конвертация положительного числа"""
        bits = self.bcd.to_binary(56)
        result = self.bcd.from_binary(bits)
        self.assertEqual(result, 56)
    
    # ❌ УДАЛИ ИЛИ ЗАКОММЕНТИРУЙ ЭТОТ ТЕСТ (отрицательные не поддерживаются)
    # def test_conversion_negative(self):
    #     """Конвертация отрицательного числа"""
    #     bits = self.bcd.to_binary(-56)
    #     result = self.bcd.from_binary(bits)
    #     self.assertEqual(result, -56)
    
    def test_conversion_zero(self):
        """Конвертация нуля"""
        bits = self.bcd.to_binary(0)
        result = self.bcd.from_binary(bits)
        self.assertEqual(result, 0)
    
    def test_addition(self):
        """Сложение BCD"""
        a = self.bcd.to_binary(56)
        b = self.bcd.to_binary(8652)
        result = self.bcd.add_with_correction(a, b)
        res_val = self.bcd.from_binary(result)
        self.assertEqual(res_val, 8708)  # 56 + 8652 = 8708
    
    def test_addition_simple(self):
        """Простое сложение BCD"""
        a = self.bcd.to_binary(67)
        b = self.bcd.to_binary(786)
        result = self.bcd.add_with_correction(a, b)
        res_val = self.bcd.from_binary(result)
        self.assertEqual(res_val, 853)  # 67 + 786 = 853
    
    def test_addition_with_carry(self):
        """Сложение с переносом через тетрады"""
        a = self.bcd.to_binary(99)
        b = self.bcd.to_binary(1)
        result = self.bcd.add_with_correction(a, b)
        res_val = self.bcd.from_binary(result)
        self.assertEqual(res_val, 100)  # 99 + 1 = 100
    
    def test_large_number(self):
        """Сложение больших чисел"""
        a = self.bcd.to_binary(9999)
        b = self.bcd.to_binary(1)
        result = self.bcd.add_with_correction(a, b)
        res_val = self.bcd.from_binary(result)
        self.assertEqual(res_val, 10000)  # 9999 + 1 = 10000
    
    def test_rejects_negative(self):
        """Тест что отрицательные числа отклоняются"""
        from utils.RangeValidator import RangeValidator
        with self.assertRaises(ValueError):
            RangeValidator.validate_bcd32(-1)
        with self.assertRaises(ValueError):
            RangeValidator.validate_bcd32(-100)


# =============================================================================
# ТЕСТЫ VALIDATORS
# =============================================================================

class TestRangeValidator(unittest.TestCase):
    """Тесты валидаторов диапазона"""
    
    def test_validate_signed_int32_valid(self):
        """Валидация корректного int32"""
        RangeValidator.validate_signed_int32(0)
        RangeValidator.validate_signed_int32(2147483647)
        RangeValidator.validate_signed_int32(-2147483648)
    
    def test_validate_signed_int32_overflow(self):
        """Валидация переполнения int32"""
        with self.assertRaises(Exception) as context:
            RangeValidator.validate_signed_int32(2147483648)
        self.assertIn("не помещается", str(context.exception))
        
        with self.assertRaises(Exception) as context:
            RangeValidator.validate_signed_int32(-2147483649)
        self.assertIn("не помещается", str(context.exception))
    
    def test_validate_bcd32_valid(self):
        """Валидация корректного BCD"""
        RangeValidator.validate_bcd32(0)
        RangeValidator.validate_bcd32(99999999)
    
    def test_validate_bcd32_overflow(self):
        """Валидация переполнения BCD"""
        with self.assertRaises(Exception) as context:
            RangeValidator.validate_bcd32(100000000)
        self.assertIn("не помещается", str(context.exception))
    
    def test_validate_bcd32_negative(self):
        """Валидация отрицательного BCD"""
        with self.assertRaises(Exception) as context:
            RangeValidator.validate_bcd32(-1)
        self.assertIn("положительные", str(context.exception))
    
    def test_validate_ieee754_valid(self):
        """Валидация корректного IEEE-754"""
        RangeValidator.validate_ieee754(0.0)
        RangeValidator.validate_ieee754(3.4e38)
        RangeValidator.validate_ieee754(-3.4e38)
    
    def test_validate_ieee754_overflow(self):
        """Валидация переполнения IEEE-754"""
        with self.assertRaises(Exception) as context:
            RangeValidator.validate_ieee754(3.5e38)
        self.assertIn("переполняет", str(context.exception))

# =============================================================================
# ТЕСТЫ OUTPUT FORMATTER
# =============================================================================

class TestOutputFormatter(unittest.TestCase):
    """Тесты форматирования вывода"""
    
    def test_format_result_basic(self):
        """Базовое форматирование"""
        from core.BitArray import BitArray
        bits = BitArray(size=32)
        output = OutputFormatter.format_result(
            "Тест", 5, 3, bits, 8, "Additional"
        )
        self.assertIn("Тест", output)
        self.assertIn("5", output)
        self.assertIn("3", output)
        self.assertIn("8", output)
    
    def test_smart_round(self):
        """Умное округление"""
        result = OutputFormatter._smart_round(5.539999)
        self.assertEqual(result, '5.54')
    
    def test_smart_round_clean(self):
        """Округление чистого числа"""
        result = OutputFormatter._smart_round(2.0)
        self.assertEqual(result, '2.0')


# =============================================================================
# ЗАПУСК ТЕСТОВ
# =============================================================================

if __name__ == '__main__':
    # Создаём тестовый загрузчик
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тесты
    suite.addTests(loader.loadTestsFromTestCase(TestBitArray))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectCode))
    suite.addTests(loader.loadTestsFromTestCase(TestReverseCode))
    suite.addTests(loader.loadTestsFromTestCase(TestAdditionalCode))
    suite.addTests(loader.loadTestsFromTestCase(TestAddOperation))
    suite.addTests(loader.loadTestsFromTestCase(TestSubtractOperation))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiplyOperation))
    suite.addTests(loader.loadTestsFromTestCase(TestDivideOperation))
    suite.addTests(loader.loadTestsFromTestCase(TestIEEE754))
    suite.addTests(loader.loadTestsFromTestCase(TestBCD8421))
    suite.addTests(loader.loadTestsFromTestCase(TestRangeValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormatter))
    
    # Запускаем с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим итоговую статистику
    print("\n" + "=" * 60)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("=" * 60)
    
    # Выход с кодом ошибки если есть провалы
    sys.exit(0 if result.wasSuccessful() else 1)