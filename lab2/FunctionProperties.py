class FunctionProperties:
    @staticmethod
    def get_zhegalkin(analyzer):
        n_rows = len(analyzer.table)
        res = [r['res'] for r in analyzer.table]
        coeffs = [res[0]]
        for i in range(1, n_rows):
            for j in range(n_rows-1, i-1, -1):
                res[j] ^= res[j-1]
            coeffs.append(res[i])
        
        terms = []
        n_vars = len(analyzer.vars)
        for i, c in enumerate(coeffs):
            if c:
                if i == 0: terms.append("1")
                else:
                    p = [analyzer.vars[k] for k in range(n_vars) if (i >> (n_vars-1-k)) & 1]
                    if p:
                        terms.append("&".join(p))
        return " ^ ".join(terms) or "0"

    @staticmethod
    def get_post_classes(analyzer):
        vals = [r['res'] for r in analyzer.table]
        t0, t1 = vals[0] == 0, vals[-1] == 1
        s = all(vals[i] != vals[-1-i] for i in range(len(vals)//2))
        m = True
        for i in range(len(vals)):
            for j in range(i+1, len(vals)):
                if all(analyzer.table[i]['vals'][k] <= analyzer.table[j]['vals'][k] for k in range(len(analyzer.vars))):
                    if vals[i] > vals[j]:
                        m = False; break
            if not m: break
        z = FunctionProperties.get_zhegalkin(analyzer)
        l = not any('&' in t for t in z.split(' ^ '))
        return f"T0:{t0}, T1:{t1}, S:{s}, M:{m}, L:{l}"

    @staticmethod
    def get_derivative(analyzer, diff_vars):
        n = len(analyzer.vars)
        vec = [r['res'] for r in analyzer.table]
        
        for v in diff_vars:
            if v not in analyzer.vars:
                continue
            v_idx = analyzer.vars.index(v)
            shift = 1 << (n - 1 - v_idx)
            new_vec = []
            for i in range(0, len(vec), shift*2):
                for j in range(shift):
                    if i + j + shift < len(vec):
                        new_vec.append(vec[i + j] ^ vec[i + j + shift])
            vec = new_vec
            n -= 1
        
        if not vec:
            return "0"
        
        class Temp: pass
        t = Temp()
        t.table = [{'res': r} for r in vec]
        # Оставшиеся переменные
        remaining_vars = [v for v in analyzer.vars if v not in diff_vars]
        t.vars = remaining_vars
        return FunctionProperties.get_zhegalkin(t)