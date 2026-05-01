from StorageNode import StorageNode
import math

TABLE_CAPACITY = 20
ALPHABET_MAP = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

def encode_key(phrase: str) -> int:
    clean = phrase.strip().lower()
    if not clean: return 0
    c1 = clean[0]
    c2 = clean[1] if len(clean) > 1 else "а"
    v1 = ALPHABET_MAP.find(c1) if c1 in ALPHABET_MAP else 0
    v2 = ALPHABET_MAP.find(c2) if c2 in ALPHABET_MAP else 0
    return v1 * 33 + v2

class MathHashRegistry:
    def __init__(self, capacity=TABLE_CAPACITY):
        self.capacity = capacity
        self.cells = [StorageNode(i) for i in range(capacity)]
        self.active_count = 0

    def _hash_primary(self, v: int) -> int: return v % self.capacity
    def _hash_step(self, v: int) -> int:
        step = 1 + (v % (self.capacity - 1))
        while math.gcd(step, self.capacity) != 1:
            step += 1
        return step

    def _locate(self, keyword: str) -> int:
        """Поиск строго по цепочке P0, начиная с h(V)"""
        val = encode_key(keyword)
        h1 = self._hash_primary(val)
        curr = h1
        for _ in range(self.capacity):
            cell = self.cells[curr]
            if cell.flag_deleted == 1:
                if cell.pointer_next == curr: break
                curr = cell.pointer_next
                continue
            if cell.flag_used == 1 and cell.keyword == keyword:
                return curr
            if cell.pointer_next == curr:
                break
            curr = cell.pointer_next
        return -1

    def add_entry(self, term: str, description: str) -> tuple:
        if self._locate(term) != -1:
            return False, "Термин уже зарегистрирован"

        val = encode_key(term)
        h1 = self._hash_primary(val)
        h2 = self._hash_step(val)

        if self.cells[h1].flag_used == 0 or self.cells[h1].flag_deleted == 1:
            target = h1
            self.cells[target].pointer_next = target
            self.cells[target].flag_collision = 0
        else:
            self.cells[h1].flag_collision = 1
            curr = h1
            while self.cells[curr].pointer_next != curr:
                curr = self.cells[curr].pointer_next
            
            target = -1
            for i in range(1, self.capacity):
                cand = (h1 + i * h2) % self.capacity
                if self.cells[cand].flag_used == 0 or self.cells[cand].flag_deleted == 1:
                    target = cand
                    break
            if target == -1:
                return False, "Хранилище переполнено"

            self.cells[curr].pointer_next = target
            self.cells[curr].flag_terminal = 0
            self.cells[target].pointer_next = target
            self.cells[target].flag_collision = 0

        cell = self.cells[target]
        cell.keyword = term
        cell.payload = description
        cell.val_v = val
        cell.base_h = h1
        cell.flag_used = 1
        cell.flag_deleted = 0
        cell.flag_link = 0
        cell.flag_terminal = 1
        self.active_count += 1
        return True, target

    def _reset_c_flag(self, h_idx: int):
        """Сбрасывает C=0, если в цепочке остался только 1 активный элемент"""
        head = self.cells[h_idx]
        if head.flag_used == 1 and head.flag_collision == 1:
            active_count = 0
            curr = h_idx
            for _ in range(self.capacity):
                cell = self.cells[curr]
                if cell.flag_used == 1 and cell.flag_deleted == 0:
                    active_count += 1
                if cell.pointer_next == curr: break
                curr = cell.pointer_next
            if active_count <= 1:
                head.flag_collision = 0

    def remove_entry(self, keyword: str) -> tuple:
        pos = self._locate(keyword)
        if pos == -1:
            return False, "Запись не обнаружена"

        node = self.cells[pos]
        h_del = node.base_h
        node.flag_deleted = 1 

        pred_idx = -1
        for other in self.cells:
            if other.flag_used == 1 and other.flag_deleted == 0 and other.pointer_next == pos:
                pred_idx = other.position
                break

        if pred_idx == -1:
            node.flag_used = 0
            node.flag_deleted = 0
            self.active_count -= 1
            self._reset_c_flag(h_del)
            return True, "Одиночная запись удалена (п.а)"

        if node.flag_terminal == 1:
            self.cells[pred_idx].flag_terminal = 1
            self.cells[pred_idx].pointer_next = pred_idx 
            node.flag_used = 0
            node.flag_deleted = 0
            self.active_count -= 1
            self._reset_c_flag(h_del)
            return True, f"Конец цепочки удален (п.б). T=1 передан строке {pred_idx}"

        next_idx = node.pointer_next
        if 0 <= next_idx < self.capacity and self.cells[next_idx].flag_used == 1:
            succ = self.cells[next_idx]
            
            node.keyword = succ.keyword
            node.payload = succ.payload
            node.val_v = succ.val_v
            node.base_h = succ.base_h
            node.flag_terminal = succ.flag_terminal
            node.flag_collision = succ.flag_collision
            node.pointer_next = succ.pointer_next
            node.flag_deleted = 0

            succ.flag_used = 0
            succ.flag_deleted = 0
            self.active_count -= 1
            self._reset_c_flag(h_del)
            return True, f"Сдвиг данных из {next_idx} в {pos} (п.в/г)"

        node.flag_used = 0
        self.active_count -= 1
        return True, f"Запись {pos} удалена"

    def print_state(self):
        print(f"\n{'№':<3} | {'V':<5} | {'h':<4} | {'Термин':<16} | {'U C T L D':<9} | {'P0':<3} | {'Данные'}")
        print("-" * 100)
        
        for cell in self.cells:
            if cell.flag_deleted == 1:
                flags = f"{cell.flag_used} {cell.flag_collision} {cell.flag_terminal} {cell.flag_link} {cell.flag_deleted}"
                print(f"{cell.position:<3} | {cell.val_v:<5} | {cell.base_h:<4} | {cell.keyword:<16} | {flags:<9} | {cell.pointer_next:<3} | [УДАЛЕНО]")
                continue

            if cell.flag_used == 0:
                print(f"{cell.position:<3} | {'-':<5} | {'-':<4} | {'-':<16} | {'0 0 - 0 0':<9} | {'-':<3} | -")
                continue

            flags = f"{cell.flag_used} {cell.flag_collision} {cell.flag_terminal} {cell.flag_link} {cell.flag_deleted}"
            data_short = (cell.payload[:40] + "..") if len(cell.payload) > 40 else cell.payload
            print(f"{cell.position:<3} | {cell.val_v:<5} | {cell.base_h:<4} | {cell.keyword:<16} | {flags:<9} | {cell.pointer_next:<3} | {data_short}")
            
        print(f"\nКоэффициент заполнения: {self.active_count / self.capacity:.2f}\n")

    def run_menu(self):
        while True:
            print("\n[1] Вывести таблицу  [2] Добавить  [3] Удалить  [4] Поиск  [0] Выход")
            cmd = input("Ваш выбор: ").strip()
            if cmd == "1":
                self.print_state()
            elif cmd == "2":
                t = input("Термин: ").strip()
                d = input("Определение: ").strip()
                if t and d:
                    ok, msg = self.add_entry(t, d)
                    print(f"{msg}" if ok else f" {msg}")
            elif cmd == "3":
                t = input("Термин для удаления: ").strip()
                ok, msg = self.remove_entry(t)
                print(f"{msg}" if ok else f"{msg}")
            elif cmd == "4":
                t = input("Поиск термина: ").strip()
                idx = self._locate(t)
                if idx != -1:
                    c = self.cells[idx]
                    print(f"Найдено в строке {idx}: {c.keyword} — {c.payload}")
                else:
                    print("Не найдено.")
            elif cmd == "0":
                print("Завершение работы.")
                break
            else:
                print("Неверная команда.")