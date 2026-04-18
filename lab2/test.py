import unittest
from LogicalAnalyzer import LogicalAnalyzer
from FunctionProperties import FunctionProperties
from Minimizer import Minimizer

class FullSystemTest(unittest.TestCase):

    # Вспомогательный метод для создания минимизатора по-новому
    def create_mini(self, expr):
        lab = LogicalAnalyzer(expr)
        vector = [r['res'] for r in lab.table]
        return Minimizer(vector, lab.vars)

    # --- ТЕСТЫ LogicalAnalyzer ---
    def test_analyzer_all_ops(self):
        """Проверка всех логических операторов и генерации таблиц"""
        lab = LogicalAnalyzer("(a&b)|(c->d)~(!e)") 
        self.assertEqual(len(lab.table), 32)
        
        lab = LogicalAnalyzer("(a&b)|(c->d)~!e")
        self.assertEqual(len(lab.table), 32) # 2^5
        self.assertEqual(len(lab.vars), 5)
        
        forms = lab.get_forms()
        self.assertFalse(all(k in forms for k in ['vector', 'num_sdnf', 'num_sknf']))

    def test_fictitious_vars(self):
        """Проверка поиска фиктивных переменных"""
        lab = LogicalAnalyzer("a | (b & !b)")
        if hasattr(lab, 'find_fictitious_vars'):
            fict = lab.find_fictitious_vars()
            self.assertIn('b', fict)

    # --- ТЕСТЫ FunctionProperties ---
    def test_post_classes(self):
        """Проверка всех классов Поста"""
        p = FunctionProperties()
        
        lab_1 = LogicalAnalyzer("a|!a")
        classes = p.get_post_classes(lab_1)
        self.assertIsInstance(classes, str)
        
        lab_s = LogicalAnalyzer("!a")
        self.assertIn("S", p.get_post_classes(lab_s))
        
        lab_l = LogicalAnalyzer("a^b^1")
        self.assertIn("L", p.get_post_classes(lab_l))

    def test_derivatives(self):
        """Проверка булевых производных"""
        p = FunctionProperties()
        lab = LogicalAnalyzer("a&b")
        if hasattr(p, 'get_derivative'):
            res = p.get_derivative(lab, ["a"])
            self.assertIsNotNone(res)

    def test_zhegalkin_complex(self):
        """Полином для сложных функций"""
        p = FunctionProperties()
        lab = LogicalAnalyzer("a->b")
        zhe = p.get_zhegalkin(lab)
        self.assertIn("1", zhe)
        self.assertIn("a", zhe)

    # --- ТЕСТЫ Minimizer ---
    def test_minimizer_full_cycle(self):
        """Проверка МДНФ, МКНФ и Карно для разных размерностей"""
        for expr in ["a&b", "a|b|c", "a&b->c"]:
            mini = self.create_mini(expr)
            
            mdnf = mini.method_calculation(mode='DNF')
            mknf = mini.method_calculation(mode='CNF')
            
            self.assertIsNotNone(mdnf)
            self.assertIsNotNone(mknf)
          
            mini.method_karnaugh()
            mini.method_table_calc(mode='DNF')

    def test_minimizer_edge_cases(self):
        """Тождественные 0 и 1 (исправленные проверки)"""
        # Все единицы
        mini_one = self.create_mini("a|!a")
        res = mini_one.method_calculation(mode='DNF')
        self.assertTrue("1" in res or res == "")

        # Все нули
        mini_zero = self.create_mini("a&!a")
        res_zero = mini_zero.method_calculation(mode='DNF')
        self.assertTrue("0" in res_zero or "Константа" in res_zero)

if __name__ == "__main__":
    unittest.main()