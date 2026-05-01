# test_lab6.py
import unittest
import math
import io
from unittest.mock import patch
from MathHashRegistry import MathHashRegistry, encode_key

class TestLab6Hash(unittest.TestCase):
    def setUp(self):
        self.ht = MathHashRegistry(20)

    def test_encode_key_standard(self):
        self.assertEqual(encode_key("Интеграл"), 311)
    def test_encode_key_single(self):
        self.assertEqual(encode_key("а"), 0)
    def test_encode_key_empty(self):
        self.assertEqual(encode_key(""), 0)
    def test_hash_primary(self):
        self.assertEqual(self.ht._hash_primary(25), 5)
    def test_hash_step_coprime(self):
        for v in range(50):
            s = self.ht._hash_step(v)
            self.assertGreaterEqual(s, 1)
            self.assertEqual(math.gcd(s, 20), 1)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_add_success(self, mock_enc):
        ok, idx = self.ht.add_entry("Test", "Desc")
        self.assertTrue(ok)
        self.assertEqual(idx, 0)
        self.assertEqual(self.ht.cells[0].keyword, "Test")
        self.assertEqual(self.ht.active_count, 1)

    @patch('MathHashRegistry.encode_key', return_value=40)
    @patch.object(MathHashRegistry, '_hash_step', return_value=3)
    def test_add_collision(self, mock_step, mock_enc):
        self.ht.cells[0].flag_used = 1
        self.ht.cells[0].pointer_next = 0
        self.ht.active_count = 1
        ok, idx = self.ht.add_entry("Coll", "Desc")
        self.assertTrue(ok)
        self.assertNotEqual(idx, 0)
        self.assertEqual(self.ht.cells[0].flag_collision, 1)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_add_duplicate(self, mock_enc):
        self.ht.add_entry("Test", "Desc")
        ok, _ = self.ht.add_entry("Test", "Desc2")
        self.assertFalse(ok)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_locate_found(self, mock_enc):
        self.ht.cells[0].keyword = "Цель"
        self.ht.cells[0].flag_used = 1
        self.ht.cells[0].base_h = 0
        self.ht.cells[0].pointer_next = 0
        self.assertEqual(self.ht._locate("Цель"), 0)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_locate_middle(self, mock_enc):
        self.ht.cells[0].keyword = "Первый"; self.ht.cells[0].flag_used = 1; self.ht.cells[0].pointer_next = 5
        self.ht.cells[5].keyword = "Средний"; self.ht.cells[5].flag_used = 1; self.ht.cells[5].pointer_next = 5
        self.assertEqual(self.ht._locate("Средний"), 5)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_locate_skip_deleted(self, mock_enc):
        self.ht.cells[0].keyword = "Дел"; self.ht.cells[0].flag_used = 1; self.ht.cells[0].flag_deleted = 1; self.ht.cells[0].pointer_next = 2
        self.ht.cells[2].keyword = "Актив"; self.ht.cells[2].flag_used = 1; self.ht.cells[2].pointer_next = 2
        self.assertEqual(self.ht._locate("Актив"), 2)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_locate_not_found(self, mock_enc):
        self.ht.cells[0].flag_used = 0
        self.assertEqual(self.ht._locate("Нет"), -1)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_remove_single(self, mock_enc):
        self.ht.cells[0].keyword = "Один"; self.ht.cells[0].flag_used = 1
        self.ht.cells[0].flag_terminal = 1; self.ht.cells[0].flag_collision = 0
        self.ht.cells[0].base_h = 0; self.ht.cells[0].pointer_next = 0
        self.ht.active_count = 1
        ok, msg = self.ht.remove_entry("Один")
        self.assertTrue(ok)
        self.assertIn("Одиночная", msg)
        self.assertEqual(self.ht.cells[0].flag_used, 0)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_remove_chain_end(self, mock_enc):

        self.ht.cells[0].keyword="Начало"; self.ht.cells[0].flag_used=1; self.ht.cells[0].flag_terminal=0; self.ht.cells[0].flag_collision=1; self.ht.cells[0].base_h=0; self.ht.cells[0].pointer_next=1
        self.ht.cells[1].keyword="Конец"; self.ht.cells[1].flag_used=1; self.ht.cells[1].flag_terminal=1; self.ht.cells[1].flag_collision=0; self.ht.cells[1].base_h=0; self.ht.cells[1].pointer_next=1
        self.ht.active_count = 2
        ok, msg = self.ht.remove_entry("Конец")
        self.assertTrue(ok)
        self.assertIn("Конец цепочки", msg)
        self.assertEqual(self.ht.cells[0].flag_terminal, 1)
        self.assertEqual(self.ht.cells[0].pointer_next, 0)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_remove_middle_shift(self, mock_enc):
        self.ht.cells[0].keyword="Первый"; self.ht.cells[0].flag_used=1; self.ht.cells[0].flag_terminal=0; self.ht.cells[0].flag_collision=1; self.ht.cells[0].base_h=0; self.ht.cells[0].pointer_next=1
        self.ht.cells[1].keyword="Середина"; self.ht.cells[1].flag_used=1; self.ht.cells[1].flag_terminal=0; self.ht.cells[1].flag_collision=0; self.ht.cells[1].base_h=0; self.ht.cells[1].pointer_next=2
        self.ht.cells[2].keyword="Конец"; self.ht.cells[2].flag_used=1; self.ht.cells[2].flag_terminal=1; self.ht.cells[2].flag_collision=0; self.ht.cells[2].base_h=0; self.ht.cells[2].pointer_next=2
        self.ht.active_count = 3
        ok, msg = self.ht.remove_entry("Середина")
        self.assertTrue(ok)
        self.assertIn("Сдвиг", msg)
        self.assertEqual(self.ht.cells[1].keyword, "Конец")
        self.assertEqual(self.ht.cells[1].flag_deleted, 0)
        self.assertEqual(self.ht.cells[2].flag_used, 0)

    @patch('MathHashRegistry.encode_key', return_value=40)
    def test_remove_not_found(self, mock_enc):
        ok, msg = self.ht.remove_entry("Нет")
        self.assertFalse(ok)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_state(self, mock_stdout):
        self.ht.cells[5].flag_used=1; self.ht.cells[5].keyword="Тест"; self.ht.cells[5].payload="Данные"; self.ht.cells[5].pointer_next=5
        self.ht.cells[6].flag_used=1; self.ht.cells[6].flag_deleted=1; self.ht.cells[6].keyword="Удал"; self.ht.cells[6].payload="Д"; self.ht.cells[6].pointer_next=6
        self.ht.active_count = 1
        self.ht.print_state()
        out = mock_stdout.getvalue()
        self.assertIn("Тест", out)
        self.assertIn("УДАЛЕНО", out)

    @patch('builtins.input', side_effect=["1", "2", "Ключ", "Опр", "4", "Ключ", "3", "Ключ", "0"])
    def test_run_menu(self, mock_input):
        self.ht.run_menu()  

if __name__ == '__main__':
    unittest.main()