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
        import re
        res = expr.replace(" ", "")
        
        # 1. Обработка импликации (->)
        while '->' in res:
            # Оборачиваем аргументы, чтобы !a|!b не развалилось
            res = re.sub(r'([^~]+)->([^~]+)', r'(not(\1) or (\2))', res)
            if '->' not in res: break

        # 2. Обработка отрицания (!)
        for v in ['a', 'b', 'c', 'd', 'e']:
            res = res.replace(f'!{v}', f'(not {v})')

        # 3. Остальные операторы
        res = res.replace('~', ' == ')
        res = res.replace('&', ' and ')
        res = res.replace('|', ' or ')
        res = res.replace('^', ' ^ ')
        
        return res

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