class Minimizer:
    def __init__(self, vector, variables):
        self.vector = vector
        self.variables = variables
        self.n = len(variables)

    def _is_dnf(self, mode):
        """Универсальная проверка: ДНФ или КНФ"""
        return str(mode).upper() in ['DNF', 'ДНФ']

    def get_initial_terms(self, target_value):
        return [f"{i:0{self.n}b}" for i, val in enumerate(self.vector) if val == target_value]

    def get_prime_implicants_with_steps(self, initial_terms):
        steps = []
        current = set(initial_terms)
        all_prime = set()
        step_num = 1
        while current:
            next_step = set()
            used = set()
            items = list(current)
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    diffs = [k for k in range(self.n) if items[i][k] != items[j][k]]
                    if len(diffs) == 1:
                        pos = diffs[0]
                        new_term = list(items[i])
                        new_term[pos] = '-'
                        next_step.add("".join(new_term))
                        used.add(items[i])
                        used.add(items[j])
            
            steps.append({'num': step_num, 'terms': sorted(list(current))})
            all_prime.update(current - used)
            if not next_step: 
                break
            current = next_step
            step_num += 1
        return steps, sorted(list(all_prime))

    def term_to_str(self, term, mode='ДНФ'):
        """Преобразует терм '10-1' в читаемую строку с учётом режима"""
        parts = []
        for i in range(self.n):
            if term[i] == '-': 
                continue
            var = self.variables[i]
            if self._is_dnf(mode):
                # ДНФ: 1 → x, 0 → !x
                parts.append(var if term[i] == '1' else f"!{var}")
            else:
                # КНФ: 0 → x, 1 → !x
                parts.append(var if term[i] == '0' else f"!{var}")
        
        if not parts: 
            return "1" if self._is_dnf(mode) else "0"
        
        if self._is_dnf(mode):
            # ДНФ: литералы через &
            return " & ".join(parts)
        else:
            # КНФ: литералы через |, терм в скобках
            return "(" + " | ".join(parts) + ")"

    def format_result(self, terms, mode='ДНФ'):
        """Формирует итоговое выражение из списка термов"""
        if not terms: 
            return "0" if self._is_dnf(mode) else "1"
        
        sep = " | " if self._is_dnf(mode) else " & "
        formatted = [self.term_to_str(t, mode) for t in terms]
        return sep.join(sorted(formatted))

    def method_calculation(self, mode='ДНФ'):
        """Расчётный метод с выводом стадий склеивания"""
        target = 1 if self._is_dnf(mode) else 0
        name = "ДНФ" if self._is_dnf(mode) else "КНФ"
        print(f"\n► РАСЧЁТНЫЙ МЕТОД ({name})")
        
        initial = self.get_initial_terms(target)
        if not initial:
            print("   Нет наборов для построения.")
            return "Константа"
            
        steps, primes = self.get_prime_implicants_with_steps(initial)
        
        # Вывод стадий склеивания
        for s in steps:
            readable = [self.term_to_str(t, mode) for t in s['terms']]
            print(f"   Стадия {s['num']}: {', '.join(readable)}")
            
        res = self.format_result(primes, mode)
        print(f"\n   ✅ Итог ({name}): {res}")
        return res

    def method_table_calc(self, mode='ДНФ'):
        """Таблично-расчётный метод (импликантная матрица)"""
        target = 1 if self._is_dnf(mode) else 0
        name = "ДНФ" if self._is_dnf(mode) else "КНФ"
        print(f"\n► ТАБЛИЧНО-РАСЧЁТНЫЙ МЕТОД ({name})")
        
        initial = self.get_initial_terms(target)
        if not initial: 
            print("   Нет наборов для построения.")
            return "Константа"
        
        steps, primes = self.get_prime_implicants_with_steps(initial)
        
        # Заголовок таблицы
        initial_labels = [f"#{int(t,2)}" for t in initial]
        header = f"{'Импликанта':<20} | " + " | ".join(f"{lbl:>3}" for lbl in initial_labels)
        print(header)
        print("-" * len(header))
        
        # Построение таблицы покрытия
        table = {}
        for p in primes:
            row_label = self.term_to_str(p, mode)
            row_display = f"{row_label:<20} |"
            matches = []
            for term in initial:
                is_match = all(p[k] == '-' or p[k] == term[k] for k in range(self.n))
                row_display += "  X  |" if is_match else "     |"
                if is_match: 
                    matches.append(term)
            table[p] = matches
            print(row_display)
        
        # Выбор существенных импликант
        selected = set()
        covered = set()
        
        # 1. Существенные (покрывают уникальный набор)
        for term in initial:
            covers = [p for p, targets in table.items() if term in targets]
            if len(covers) == 1:
                selected.add(covers[0])
                covered.update(table[covers[0]])
        
        # 2. Жадное дополнение
        remaining = [t for t in initial if t not in covered]
        while remaining:
            best = max(
                (p for p in primes if p not in selected),
                key=lambda p: sum(1 for t in table[p] if t in remaining),
                default=None
            )
            if not best: 
                break
            selected.add(best)
            covered.update(table[best])
            remaining = [t for t in initial if t not in covered]
        
        res = self.format_result(selected, mode)
        print(f"\n✅ Итог ({name}): {res}")
        return res

    def method_karnaugh(self):
        """Метод карт Карно (2-5 переменных)"""
        def gray_code(n):
            if n == 0:
                return ['']
            prev = gray_code(n - 1)
            return ['0' + x for x in prev] + ['1' + x for x in reversed(prev)]

        def differ_by_one_bit(a, b):
            return sum(x != y for x, y in zip(a, b)) == 1

        def merge_terms(a, b):
            return ''.join([x if x == y else '-' for x, y in zip(a, b)])

        def term_covers(term, bits):
            return all(t == b or t == '-' for t, b in zip(term, bits))

        def minimize(target_value):
            terms = []
            for i, v in enumerate(self.vector):
                if v == target_value:
                    terms.append(format(i, f'0{n}b'))

            if not terms:
                return "0" if target_value == 1 else "1"

            groups = {}
            for t in terms:
                groups.setdefault(t.count('1'), []).append(t)

            prime_implicants = set()

            while groups:
                new_groups = {}
                used = set()
                keys = sorted(groups.keys())
                
                for i in range(len(keys) - 1):
                    for a in groups[keys[i]]:
                        for b in groups[keys[i + 1]]:
                            if differ_by_one_bit(a, b):
                                merged = merge_terms(a, b)
                                new_groups.setdefault(merged.count('1'), []).append(merged)
                                used.add(a)
                                used.add(b)

                for group in groups.values():
                    for term in group:
                        if term not in used:
                            prime_implicants.add(term)

                groups = {}
                for k, v in new_groups.items():
                    groups[k] = list(set(v))

            coverage = {t: [] for t in terms}
            for pi in prime_implicants:
                for t in terms:
                    if term_covers(pi, t):
                        coverage[t].append(pi)

            essential = set()
            for t, pis in coverage.items():
                if len(pis) == 1:
                    essential.add(pis[0])

            covered = set()
            for pi in essential:
                for t in terms:
                    if term_covers(pi, t):
                        covered.add(t)

            remaining = set(terms) - covered
            for pi in prime_implicants:
                if remaining:
                    covers = [t for t in remaining if term_covers(pi, t)]
                    if covers:
                        essential.add(pi)
                        for t in covers:
                            remaining.discard(t)

            def term_to_expr(term, is_dnf):
                parts = []
                for i, ch in enumerate(term):
                    if ch == '-':
                        continue
                    var = self.variables[i]
                    if is_dnf:
                        parts.append(var if ch == '1' else f"!{var}")
                    else:
                        parts.append(var if ch == '0' else f"!{var}")
                if not parts:
                    return "1" if is_dnf else "0"
                if is_dnf:
                    return " & ".join(parts)
                else:
                    return "(" + " | ".join(parts) + ")"

            if target_value == 1:
                return " | ".join(term_to_expr(t, True) for t in essential)
            else:
                return " & ".join(term_to_expr(t, False) for t in essential)

        n = len(self.variables)
        if n < 2 or n > 5:
            print("Карта Карно: поддержка 2–5 переменных")
            return

        print("\n" + "="*40)
        print(" КАРТА КАРНО ")
        print("="*40)
        
        if n == 5:
            row_vars = self.variables[:2]
            col_vars = self.variables[2:4]
            extra_var = self.variables[4]
        else:
            row_vars = self.variables[:n//2]
            col_vars = self.variables[n//2:]
            extra_var = None

        row_gray = gray_code(len(row_vars))
        col_gray = gray_code(len(col_vars))

        def get_value(bits):
            return self.vector[int(bits, 2)]

        if not extra_var:
            print("    ", "  ".join(col_gray))
            for r in row_gray:
                row = [str(get_value(r + c)) for c in col_gray]
                print(f"{r} |  " + "  ".join(row))
        else:
            for e in ['0', '1']:
                print(f"\nСлой {extra_var} = {e}")
                print("    ", "  ".join(col_gray))
                for r in row_gray:
                    row = [str(get_value(r + c + e)) for c in col_gray]
                    print(f"{r} |  " + "  ".join(row))

        dnf = minimize(1)
        knf = minimize(0)

        print("\n" + "-"*40)
        print(" РЕЗУЛЬТАТ МИНИМИЗАЦИИ КАРНО")
        print("-"*40)
        print(f"Минимальная ДНФ: {dnf}")
        print(f"Минимальная КНФ: {knf}")