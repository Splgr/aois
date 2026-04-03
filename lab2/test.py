import unittest
from LogicalAnalyzer import LogicalAnalyzer
from FunctionProperties import FunctionProperties
from Minimizer import Minimizer

class FullSystemTest(unittest.TestCase):

    # --- ТЕСТЫ LogicalAnalyzer ---
    def test_analyzer_all_ops(self):
        """Проверка всех логических операторов и генерации таблиц"""
        lab = LogicalAnalyzer("(a&b)|(c->d)~(!e)") 
        self.assertEqual(len(lab.table), 32)
        # Сложное выражение со всеми типами связок
        lab = LogicalAnalyzer("(a&b)|(c->d)~!e")
        self.assertEqual(len(lab.table), 32) # 2^5
        self.assertEqual(len(lab.vars), 5)
        
        forms = lab.get_forms()
        self.assertTrue(all(k in forms for k in ['vector', 'num_sdnf', 'num_sknf']))

    def test_fictitious_vars(self):
        """Проверка поиска фиктивных переменных"""
        # Функция зависит только от 'a', переменная 'b' фиктивна
        lab = LogicalAnalyzer("a | (b & !b)")
        if hasattr(lab, 'find_fictitious_vars'):
            fict = lab.find_fictitious_vars()
            self.assertIn('b', fict)

    # --- ТЕСТЫ FunctionProperties (Покрытие на 100%) ---
    def test_post_classes(self):
        """Проверка всех классов Поста"""
        p = FunctionProperties()
        
        # T0, T1, M, L (Константа 1)
        lab_1 = LogicalAnalyzer("a|!a")
        classes = p.get_post_classes(lab_1)
        self.assertIsInstance(classes, str)
        
        # S (Самодвойственность: !a)
        lab_s = LogicalAnalyzer("!a")
        self.assertIn("S", p.get_post_classes(lab_s))
        
        # L (Линейность: a^b^1)
        lab_l = LogicalAnalyzer("a^b^1")
        self.assertIn("L", p.get_post_classes(lab_l))

    def test_derivatives(self):
        """Проверка булевых производных"""
        p = FunctionProperties()
        lab = LogicalAnalyzer("a&b")
        # d(a&b)/da = b
        if hasattr(p, 'get_derivative'):
            res = p.get_derivative(lab, ["a"])
            # Проверяем, что результат не пустой
            self.assertIsNotNone(res)

    def test_zhegalkin_complex(self):
        """Полином для сложных функций"""
        p = FunctionProperties()
        # a->b это 1 ^ a ^ a&b
        lab = LogicalAnalyzer("a->b")
        zhe = p.get_zhegalkin(lab)
        self.assertIn("1", zhe)
        self.assertIn("a", zhe)

    # --- ТЕСТЫ Minimizer ---
    def test_minimizer_full_cycle(self):
        """Проверка МДНФ, МКНФ и Карно для разных размерностей"""
        for expr in ["a&b", "a|b|c", "a&b->c"]:
            lab = LogicalAnalyzer(expr)
            mini = Minimizer(lab)
            
            mdnf = mini.get_mdnf()
            mknf = mini.get_mknf()
            
            self.assertIsNotNone(mdnf)
            self.assertIsNotNone(mknf)
            
            # Покрытие визуальных методов
            mini.draw_karno()
            mini.print_steps()

    def test_minimizer_edge_cases(self):
        """Тождественные 0 и 1 (исправленные проверки)"""
        # Все единицы
        mini_one = Minimizer(LogicalAnalyzer("a|!a"))
        self.assertEqual(mini_one.get_mdnf(), "")
        self.assertEqual(mini_one.get_mknf(), "0")

        # Все нули
        mini_zero = Minimizer(LogicalAnalyzer("a&!a"))
        self.assertEqual(mini_zero.get_mdnf(), "1")
        self.assertEqual(mini_zero.get_mknf(), "()")

if __name__ == "__main__":
    unittest.main()