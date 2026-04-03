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
            # Исправлено форматирование для ровных колонок
            vals_str = " | ".join(map(str, r['vals']))
            print(f"{vals_str} |  {r['res']}")

        # 3. Фиктивные переменные
        if hasattr(lab, 'find_fictitious_vars'):
            fictitious = lab.find_fictitious_vars()
            status = ', '.join(fictitious) if fictitious else "не найдены"
            print(f"\n[ 2. ФИКТИВНЫЕ ПЕРЕМЕННЫЕ ]: {status}")

        # 4. Формы и вектор (ИСПРАВЛЕНО ЗДЕСЬ)
        f = lab.get_forms()
        print(f"\n[ 3. ОСНОВНЫЕ ФОРМЫ ]")
        print(f"Вектор функции: {f['vector']}")
        
        print(f"СДНФ (числовая): {f.get('num_sdnf', 'н/д')}")
        print(f"СДНФ (полная):   {f.get('sdnf', 'н/д')}") # Добавили вывод букв
        
        print("-" * 30)
        
        print(f"СКНФ (числовая): {f.get('num_sknf', 'н/д')}")
        print(f"СКНФ (полная):   {f.get('sknf', 'н/д')}") # Добавили вывод букв

        # 5. Полином Жегалкина и классы Поста
        p = FunctionProperties()
        print(f"\n[ 4. СВОЙСТВА ФУНКЦИИ ]")
        print(f"Полином Жегалкина: {p.get_zhegalkin(lab)}")
        if hasattr(p, 'get_post_classes'):
            print(f"Классы Поста: {p.get_post_classes(lab)}")
        
        # 6. Производная (Улучшен ввод)
        if hasattr(p, 'get_derivative'):
            print("\n[ 5. БУЛЕВА ПРОИЗВОДНАЯ ]")
            v_raw = input(f"Введите переменные через пробел или запятую ({', '.join(lab.vars)}): ").strip()
            if v_raw:
                # Убираем запятые, если пользователь их ввел, и делим на список
                v_input = v_raw.replace(',', ' ').split()
                if all(v in lab.vars for v in v_input):
                    res_deriv = p.get_derivative(lab, v_input)
                    print(f"Результат dF/d({', '.join(v_input)}): {res_deriv}")
                else:
                    print("Пропущено: неверные имена переменных (используйте английскую раскладку).")

        # 7. МИНИМИЗАЦИЯ
        print("\n" + "="*50)
        print(" МИНИМИЗАЦИЯ ФУНКЦИИ (ПОШАГОВО) ")
        print("="*50)
        
        mini = Minimizer(lab)
        mini.draw_karno()

        if hasattr(mini, 'print_steps'):
            mini.print_steps()

        print("\n[ ИТОГОВЫЕ МИНИМАЛЬНЫЕ ФОРМЫ ]")
        print(f"МДНФ: {mini.get_mdnf()}")
        print(f"МКНФ: {mini.get_mknf()}")
        print("="*50)

    except Exception as e:
        print(f"\n[!] КРИТИЧЕСКАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    main()