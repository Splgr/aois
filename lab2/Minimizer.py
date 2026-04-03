class Minimizer:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.vars = analyzer.vars
        self.minterms = [i for i, r in enumerate(analyzer.table) if r['res'] == 1]

    def _qm_steps(self, targets):
        if not targets: return [], {}
        n = len(self.vars)
        # Инициализация групп по количеству единиц
        groups = {}
        for m in targets:
            b = format(m, f'0{n}b')
            groups.setdefault(b.count('1'), []).append(b)
        
        all_stages = []
        primes = set()
        current_groups = groups
        
        stage = 0
        while current_groups:
            all_stages.append(current_groups)
            next_g, used = {}, set()
            keys = sorted(current_groups.keys())
            
            for i in range(len(keys)-1):
                for b1 in current_groups[keys[i]]:
                    for b2 in current_groups[keys[i+1]]:
                        diff = [j for j in range(n) if b1[j] != b2[j]]
                        if len(diff) == 1:
                            nb = list(b1); nb[diff[0]] = '-'
                            snb = "".join(nb)
                            next_g.setdefault(keys[i], []).append(snb)
                            used.update([b1, b2])
            
            for g in current_groups.values():
                for b in g:
                    if b not in used: primes.add(b)
            
            current_groups = {k: list(set(v)) for k, v in next_g.items()}
            stage += 1
            
        return sorted(list(primes)), all_stages

    def print_steps(self):
        print("\n[ СТАДИЯ 1: СКЛЕИВАНИЕ (РАСЧЕТНЫЙ МЕТОД) ]")
        primes, stages = self._qm_steps(self.minterms)
        
        for i, stage_data in enumerate(stages):
            print(f"--- Итерация {i+1} ---")
            for count in sorted(stage_data.keys()):
                for term in stage_data[count]:
                    print(f" Группа {count}: {term}")
        
        print(f"\nПростые импликанты: {', '.join(primes)}")
        
        print("\n[ СТАДИЯ 2: ТАБЛИЦА ПОКРЫТИЙ (РАСЧЕТНО-ТАБЛИЧНЫЙ МЕТОД) ]")
        self._print_table(self.minterms, primes)
        return primes

    def _print_table(self, targets, primes):
        header = " Импликанта | " + " | ".join([format(m, 'd').center(3) for m in targets])
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        
        for p in primes:
            row = f" {p.ljust(10)} | "
            for m in targets:
                mb = format(m, f'0{len(self.vars)}b')
                match = all(p[j] == '-' or p[j] == mb[j] for j in range(len(self.vars)))
                row += (" X ".center(3) if match else " . ".center(3)) + " | "
            print(row)
        print("-" * len(header))

    def draw_karno(self):
        n = len(self.vars)
        if n == 3:
            cols = ['00', '01', '11', '10']
            print("\n[ КАРТА КАРНО (3 переменные) ]")
            print("      00 01 11 10 (bc)")
            for r in ['0', '1']:
                print(f" {r}(a) |", end="")
                for c in cols:
                    idx = int(r + c, 2)
                    print(f" {self.analyzer.table[idx]['res']} ", end="")
                print()
        elif n == 2:
            print("\n[ КАРТА КАРНО (2 переменные) ]")
            print("    0 1 (b)")
            for r in ['0', '1']:
                idx_0 = int(r + '0', 2)
                idx_1 = int(r + '1', 2)
                print(f"{r}(a)| {self.analyzer.table[idx_0]['res']} {self.analyzer.table[idx_1]['res']}")

    def get_mdnf(self):
        primes, _ = self._qm_steps(self.minterms)
        # Упрощенный выбор покрытия для МДНФ
        final = self._get_cover(self.minterms, primes)
        return self._format_final(final, True)

    def get_mknf(self):
        maxterms = [i for i, r in enumerate(self.analyzer.table) if r['res'] == 0]
        primes, _ = self._qm_steps(maxterms)
        final = self._get_cover(maxterms, primes)
        return self._format_final(final, False)

    def _get_cover(self, targets, primes):
        if not targets: return []
        uncovered = set(targets)
        final = []
        while uncovered and primes:
            best_p = max(primes, key=lambda p: len(self._get_matches(p, uncovered)))
            if not self._get_matches(best_p, uncovered): break
            final.append(best_p)
            uncovered -= self._get_matches(best_p, uncovered)
            primes = [p for p in primes if p != best_p]
        return final

    def _get_matches(self, p, targets):
        matches = set()
        for m in targets:
            mb = format(m, f'0{len(self.vars)}b')
            if all(p[j] == '-' or p[j] == mb[j] for j in range(len(self.vars))):
                matches.add(m)
        return matches

    def _format_final(self, final, is_dnf):
        # Обработка пустых случаев (константы 0 и 1)
        if not final: 
            return "1" if is_dnf else "0"
            
        res = []
        for p in final:
            term = []
            for i, char in enumerate(p):
                if char == '-': 
                    continue
                v = self.vars[i]
                
                # --- ВОТ ТУТ ГЛАВНОЕ ИСПРАВЛЕНИЕ ---
                if is_dnf:
                    # Для МДНФ: 1 -> прямая (a), 0 -> отрицание (!a)
                    term.append(v if char == '1' else "!" + v)
                else:
                    # Для МКНФ: 0 -> прямая (a), 1 -> отрицание (!a)
                    term.append(v if char == '0' else "!" + v)
                # -----------------------------------
                
            res.append(("&" if is_dnf else "|").join(term))
        
        if is_dnf:
            return " | ".join(res)
        else:
            # Для МКНФ всегда оборачиваем в скобки и соединяем через И (&)
            return " & ".join([f"({t})" for t in res])