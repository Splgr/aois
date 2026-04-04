import re
from itertools import product

class LogicalAnalyzer:
    def __init__(self, expr):
        self.expr = expr
        self.vars = sorted(list(set(re.findall(r'[a-e]', expr))))
        if not self.vars:
            raise ValueError("Переменные a-e не найдены.")
        self.py_expr = self._prepare_expr(expr)
        self.table = self._build_table()

    def _prepare_expr(self, expr):
        # 1. Убираем все пробелы и в нижний регистр
        res = "".join(expr.split()).lower()
        
        # 2. Порядок замен ВАЖЕН:
        # Сначала сложные операторы, потом простые
        res = res.replace('->', ' <= ')  # Импликация
        res = res.replace('~', ' == ')   # Эквивалентность
        
        # 3. Отрицание !x меняем на (1-x). 
        # Это работает и для переменных, и для скобок: !(a|b) -> (1-(a|b))
        res = res.replace('!', ' (1-')
        
        # Считаем, сколько " (1-" мы добавили, столько скобок в конце и закроем
        # Но лучше просто заменять адресно, чтобы не плодить лишние скобки
        # Вернемся к классике, но БЕЗ лишних открывающих скобок:
        res = expr.replace(" ", "").lower()
        res = res.replace('->', ' <= ').replace('~', ' == ')
        res = res.replace('&', ' & ').replace('|', ' | ').replace('^', ' ^ ')
        
        # Самый надежный способ для '!' в Python eval:
        # Заменяем ! на ^1 (инверсия бита)
        # Если ! стоит перед скобкой !(a&b) -> (a&b)^1
        # Если перед переменной !a -> a^1
        
        # Давай применим самый стабильный метод:
        final_res = ""
        i = 0
        while i < len(res):
            if res[i] == '!':
                # Если видим !, ищем что за ним (переменная или скобка)
                if i + 1 < len(res) and res[i+1] == '(':
                    # Находим закрывающую скобку для этой группы
                    count = 0
                    j = i + 1
                    while j < len(res):
                        if res[j] == '(': count += 1
                        elif res[j] == ')': count -= 1
                        if count == 0: break
                        j += 1
                    final_res += "(" + res[i+1:j+1] + "^1)"
                    i = j + 1
                else:
                    # Просто переменная
                    final_res += "(" + res[i+1] + "^1)"
                    i += 2
            else:
                final_res += res[i]
                i += 1
        
        # Финальные правки операторов
        final_res = final_res.replace('->', ' <= ').replace('~', ' == ')
        return final_res

    def _build_table(self):
        table = []
        for v in product([0, 1], repeat=len(self.vars)):
            ctx = dict(zip(self.vars, v))
            try:
                expr_to_eval = self.py_expr
                res = eval(expr_to_eval, {"__builtins__": {}}, ctx)
                table.append({'vals': v, 'res': int(res)})
            except Exception as e:
                print(f"Ошибка при вычислении для {ctx}: {e}")
                raise
        return table

    def get_forms(self):
        sdnf_idx = [i for i, r in enumerate(self.table) if r['res'] == 1]
        sknf_idx = [i for i, r in enumerate(self.table) if r['res'] == 0]
        vector = "".join(str(r['res']) for r in self.table)
        
        # Внутренняя функция для сборки буквенных форм
        def build_f(indices, is_sdnf):
            if not indices: return "0" if is_sdnf else "1"
            terms = []
            for idx in indices:
                b = self.table[idx]['vals']
                p = []
                for i, bit in enumerate(b):
                    if is_sdnf:
                        # СДНФ: 1 -> x, 0 -> !x
                        p.append(self.vars[i] if bit else f"!{self.vars[i]}")
                    else:
                        # СКНФ: 0 -> x, 1 -> !x
                        p.append(f"!{self.vars[i]}" if bit else self.vars[i])
                sep = " & " if is_sdnf else " | "
                terms.append(f"({'#'.join(p)})".replace('#', sep)) # Костыль для красоты сепаратора
            return (" | " if is_sdnf else " & ").join(terms)

        return {
            "sdnf": build_f(sdnf_idx, True),     # Полная СДНФ (буквы)
            "sknf": build_f(sknf_idx, False),    # Полная СКНФ (буквы)
            "num_sdnf": f"∑({', '.join(map(str, sdnf_idx))})",
            "num_sknf": f"∏({', '.join(map(str, sknf_idx))})",
            "vector": vector
        }
    
    def find_fictitious_vars(self):
        fictitious = []
        n = len(self.vars)
        for idx, var in enumerate(self.vars):
            is_fictitious = True
            for vals in product([0, 1], repeat=n):
                vals0 = list(vals); vals0[idx] = 0
                vals1 = list(vals); vals1[idx] = 1
                
                idx0 = next(i for i, r in enumerate(self.table) if list(r['vals']) == vals0)
                idx1 = next(i for i, r in enumerate(self.table) if list(r['vals']) == vals1)
                
                if self.table[idx0]['res'] != self.table[idx1]['res']:
                    is_fictitious = False
                    break
            if is_fictitious:
                fictitious.append(var)
        return fictitious