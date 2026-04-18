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
   
        res = res.replace('->', ' <= ')  # Импликация
        res = res.replace('~', ' == ')   # Эквивалентность
     
        res = res.replace('!', ' (1-')

        res = expr.replace(" ", "").lower()
        res = res.replace('->', ' <= ').replace('~', ' == ')
        res = res.replace('&', ' & ').replace('|', ' | ').replace('^', ' ^ ')
        
        
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

    def _tokenize(self, expr: str) -> list[str]:
        tokens = []
        i = 0
        expr = expr.strip().lower()
        while i < len(expr):
            c = expr[i]
            if c.isspace(): 
                i += 1
                continue
            # Добавлены '0' и '1' как допустимые операнды
            if c in 'abcde01':
                tokens.append(c); i += 1
            elif c == '(':
                tokens.append('('); i += 1
            elif c == ')':
                tokens.append(')'); i += 1
            elif c == '-' and i+1 < len(expr) and expr[i+1] == '>':
                tokens.append('->'); i += 2
            elif c in '!&|^~':
                tokens.append(c); i += 1
            else:
                raise ValueError(f"Неизвестный символ '{c}'")
        return tokens

    def _to_rpn(self, expr: str) -> list[str]:
        tokens = self._tokenize(expr)
        prec = {'!': 4, '&': 3, '^': 2, '|': 1, '~': 0, '->': -1}
        assoc = {'!': 'right', '->': 'right', '&': 'left', '^': 'left', '|': 'left', '~': 'left'}
        output, stack = [], []
        
        for t in tokens:
            # Переменные И константы сразу в вывод
            if t in 'abcde01':
                output.append(t)
            elif t in prec:
                while (stack and stack[-1] != '(' and stack[-1] in prec and
                      (prec[stack[-1]] > prec[t] or 
                       (prec[stack[-1]] == prec[t] and assoc[t] == 'left'))):
                    output.append(stack.pop())
                stack.append(t)
            elif t == '(':
                stack.append(t)
            elif t == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack: raise ValueError("Несбалансированные скобки")
                stack.pop()
        while stack:
            if stack[-1] == '(': raise ValueError("Несбалансированные скобки")
            output.append(stack.pop())
        return output

    def _eval_rpn(self, rpn: list[str], ctx: dict[str, int]) -> int:
        stack = []
        for t in rpn:
            if t in 'abcde':
                stack.append(ctx[t])
            elif t in '01':  # <-- Добавлена обработка констант
                stack.append(int(t))
            elif t == '!':
                stack.append(stack.pop() ^ 1)
            else:
                b, a = stack.pop(), stack.pop()
                if t == '&': stack.append(a & b)
                elif t == '|': stack.append(a | b)
                elif t == '^': stack.append(a ^ b)
                elif t == '->': stack.append(1 if a <= b else 0)
                elif t == '~': stack.append(1 if a == b else 0)
        return stack[0] if stack else 0
    
    def _build_table(self):
        """Построение таблицы истинности"""
        # Компилируем выражение в ОПН один раз
        self.rpn = self._to_rpn(self.expr)
        
        table = []
        for v in product([0, 1], repeat=len(self.vars)):
            ctx = dict(zip(self.vars, v))
            try:
                res = self._eval_rpn(self.rpn, ctx)
                table.append({'vals': v, 'res': int(res)})
            except Exception as e:
                print(f"Ошибка при вычислении для {ctx}: {e}")
                raise
        return table

    def get_forms(self):
        sdnf_idx = [i for i, r in enumerate(self.table) if r['res'] == 1]
        sknf_idx = [i for i, r in enumerate(self.table) if r['res'] == 0]
        vector = "".join(str(r['res']) for r in self.table)
        
        # Сборка полной буквенной формы
        def build_literal(indices, is_sdnf):
            if not indices: return "0" if is_sdnf else "1"
            terms = []
            sep_in = " & " if is_sdnf else " | "
            sep_out = " | " if is_sdnf else " & "
            for idx in indices:
                b = self.table[idx]['vals']
                lits = []
                for i, bit in enumerate(b):
                    if is_sdnf:
                        lits.append(self.vars[i] if bit else f"!{self.vars[i]}")
                    else:
                        lits.append(f"!{self.vars[i]}" if bit else self.vars[i])
                terms.append(f"({sep_in.join(lits)})")
            return sep_out.join(terms)

        return {
            "vector": vector,
            "sdnf": {
                "index": f"∑({', '.join(map(str, sdnf_idx))})" if sdnf_idx else "∅",
                "numeric": vector,
                "full": build_literal(sdnf_idx, True)
            },
            "sknf": {
                "index": f"∏({', '.join(map(str, sknf_idx))})" if sknf_idx else "∅",
                "numeric": vector,
                "full": build_literal(sknf_idx, False)
            }
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