from LogicalAnalyzer import LogicalAnalyzer
from FunctionProperties import FunctionProperties
from Minimizer import Minimizer

def main():
    print("=== АНАЛИЗАТОР БУЛЕВЫХ ФУНКЦИЙ ===")
    expr_input = input("Введите функцию (например, a&b->c): ").strip()
    
    if not expr_input:
        print("Ошибка: пустой ввод.")
        return

    try:
        # 1. Инициализация анализатора
        lab = LogicalAnalyzer(expr_input)
        
        # 2. Таблица истинности
        print("\n[ 1. ТАБЛИЦА ИСТИННОСТИ ]")
        print(" | ".join(lab.vars) + " |  F")
        print("-" * (len(lab.vars) * 4 + 5))
        for r in lab.table:
            vals_str = " | ".join(map(str, r['vals']))
            print(f"{vals_str} |  {r['res']}")

        # 3. Фиктивные переменные
        if hasattr(lab, 'find_fictitious_vars'):
            fictitious = lab.find_fictitious_vars()
            status = ', '.join(fictitious) if fictitious else "не найдены"
            print(f"\n[ 2. ФИКТИВНЫЕ ПЕРЕМЕННЫЕ ]: {status}")

        # 4. Формы и вектор
        f = lab.get_forms()
        print(f"\n[ 3. ОСНОВНЫЕ ФОРМЫ ]")
        print(f"Индексная форма функции: {f['vector']}\n")

        print("► СДНФ:")
        print(f"   Числовая:   {f['sdnf']['index']}")
        print(f"   Полная:     {f['sdnf']['full']}\n")

        print("► СКНФ:")
        print(f"   Числовая:   {f['sknf']['index']}")
        print(f"   Полная:     {f['sknf']['full']}")

        # 5. Полином Жегалкина и классы Поста
        p = FunctionProperties()
        print(f"\n[ 4. СВОЙСТВА ФУНКЦИИ ]")
        print(f"Полином Жегалкина: {p.get_zhegalkin(lab)}")
        if hasattr(p, 'get_post_classes'):
            print(f"Классы Поста: {p.get_post_classes(lab)}")
        
        # 6. Производная
        if hasattr(p, 'get_derivative'):
            print("\n[ 5. БУЛЕВА ПРОИЗВОДНАЯ ]")
            v_raw = input(f"Введите переменные через пробел или запятую ({', '.join(lab.vars)}): ").strip()
            if v_raw:
                v_input = v_raw.replace(',', ' ').split()
                if all(v in lab.vars for v in v_input):
                    res_deriv = p.get_derivative(lab, v_input)
                    print(f"Результат dF/d({', '.join(v_input)}): {res_deriv}")
                else:
                    print("Пропущено: неверные имена переменных.")

        # 7. МИНИМИЗАЦИЯ
        print("\n" + "="*50)
        print(" МИНИМИЗАЦИЯ ФУНКЦИИ (ПОШАГОВО) ")
        print("="*50)
        
        vector_list = [r['res'] for r in lab.table]
        mini = Minimizer(vector_list, lab.vars)

        # Универсальная функция для красивой печати (чтобы не было "хрени")
        def pretty_print(implicants, mode='ДНФ'):
            if not implicants: return "Константа"
            terms = []
            for imp in implicants:
                letters = []
                for i, val in enumerate(imp):
                    if val == '-': continue
                    var = lab.vars[i]
                    if mode == 'ДНФ':
                        letters.append(var if val == '1' else f"!{var}")
                    else:
                        # Для КНФ инвертируем значения (0 -> прямая, 1 -> инверсия)
                        letters.append(var if val == '0' else f"!{var}")
                
                sep = " & " if mode == 'ДНФ' else " | "
                term_str = sep.join(letters)
                terms.append(f"({term_str})" if len(letters) > 1 else term_str)
            
            main_sep = " | " if mode == 'ДНФ' else " & "
            return main_sep.join(terms)

        # --- 1. РАСЧЁТНЫЙ МЕТОД ---
        print("\n" + "="*50)
        print(" МИНИМИЗАЦИЯ: РАСЧЁТНЫЙ МЕТОД ")
        print("="*50)

        # 1. Получаем импликанты (чтобы переменные существовали для итоговой сводки)
        _, dnf_imp = mini.get_prime_implicants_with_steps(mini.get_initial_terms(1))
        _, knf_imp = mini.get_prime_implicants_with_steps(mini.get_initial_terms(0))

        # 2. Вывод стадий склеивания (ДНФ)
        print("\n► СТАДИИ СКЛЕИВАНИЯ (ДНФ):")
        steps_dnf, _ = mini.get_prime_implicants_with_steps(mini.get_initial_terms(1))
        for s in steps_dnf:
            # Передаем 'DNF' или 'ДНФ' -> метод сам разберется
            readable = [mini.term_to_str(t, 'DNF') for t in s['terms']]
            print(f"   Стадия {s['num']}: {', '.join(readable)}")

        # 3. Вывод стадий склеивания (КНФ)
        print("\n► СТАДИИ СКЛЕИВАНИЯ (КНФ):")
        steps_knf, _ = mini.get_prime_implicants_with_steps(mini.get_initial_terms(0))
        for s in steps_knf:
            readable = [mini.term_to_str(t, 'KNF') for t in s['terms']]
            print(f"   Стадия {s['num']}: {', '.join(readable)}")


        # 4. Итог расчётного метода
        print(f"\n✅ Результат (ДНФ): {pretty_print(dnf_imp, 'ДНФ')}")
        print(f"✅ Результат (КНФ): {pretty_print(knf_imp, 'КНФ')}")

        # --- 2. ТАБЛИЧНО-РАСЧЕТНЫЙ МЕТОД ---
        print("\n--- ТАБЛИЦА ДЛЯ ДНФ ---")
        mini.method_table_calc(mode='ДНФ')
        print(f"Результат (ДНФ): {pretty_print(dnf_imp, 'ДНФ')}") # Дублируем красиво
        
        print("\n--- ТАБЛИЦА ДЛЯ КНФ ---")
        mini.method_table_calc(mode='КНФ')
        print(f"Результат (КНФ): {pretty_print(knf_imp, 'КНФ')}") # Дублируем красиво

        # --- 3. МЕТОД КАРНО ---
        # Он в твоем классе уже более-менее норм, пусть отрисует слои
        mini.method_karnaugh()

        # --- 4. ФИНАЛЬНАЯ СВОДКА ---
        print("\n" + "="*60)
        print(" ИТОГОВЫЕ МИНИМАЛЬНЫЕ ФОРМЫ (СВОДКА) ")
        print("="*60)
        print(f"ФИНАЛЬНАЯ МДНФ: {pretty_print(dnf_imp, 'ДНФ')}")
        print(f"ФИНАЛЬНАЯ МКНФ: {pretty_print(knf_imp, 'КНФ')}")
        print("="*60)

    except Exception as e:
        print(f"\n[!] КРИТИЧЕСКАЯ ОШИБКА: {e}")

    except Exception as e:
        print(f"\n[!] КРИТИЧЕСКАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    main()