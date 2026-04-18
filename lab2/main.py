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

        # --- 1. РАСЧЁТНЫЙ МЕТОД ---
        print("\n► РАСЧЁТНЫЙ МЕТОД (ДНФ):")
        res_dnf_calc = mini.method_calculation(mode='ДНФ')

        print("\n► РАСЧЁТНЫЙ МЕТОД (КНФ):")
        res_knf_calc = mini.method_calculation(mode='КНФ')

        # --- 2. ТАБЛИЧНО-РАСЧЁТНЫЙ МЕТОД ---
        print("\n" + "-"*50)
        print("► ТАБЛИЧНО-РАСЧЁТНЫЙ МЕТОД (ДНФ):")
        res_dnf_tab = mini.method_table_calc(mode='ДНФ')

        print("\n► ТАБЛИЧНО-РАСЧЁТНЫЙ МЕТОД (КНФ):")
        res_knf_tab = mini.method_table_calc(mode='КНФ')

        # --- 3. МЕТОД КАРНО ---
        print("\n" + "-"*50)
        print("► МЕТОД КАРНО:")
        dnf_k, knf_k = mini.method_karnaugh() 

        # --- 4. ФИНАЛЬНАЯ СВОДКА ---
        print("\n" + "="*60)
        print(" ИТОГОВЫЕ МИНИМАЛЬНЫЕ ФОРМЫ (СВОДКА) ")
        print("="*60)
        print(f"МДНФ (расчётный):      {res_dnf_calc}")
        print(f"МДНФ (табличный):      {res_dnf_tab}")
        print(f"МДНФ (Карно):          {dnf_k}")
        print("-" * 60)
        print(f"МКНФ (расчётный):      {res_knf_calc}")
        print(f"МКНФ (табличный):      {res_knf_tab}")
        print(f"МКНФ (Карно):          {knf_k}")
        print("="*60)

    except Exception as e:
        print(f"\n[!] КРИТИЧЕСКАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    main()