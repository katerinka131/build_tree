from graphviz import Digraph

def find_evolution_path(root, leaf):
    """
    Правильный алгоритм для ограниченных операций:
    - Добавление только в конец
    - Удаление любой подстроки
    - Замена символов
    """
    path = []
    current = root
    
    # Основная идея: идем по целевой строке и "подгоняем" текущую под нее
    i = 0  # индекс в current
    j = 0  # индекс в leaf
    
    while j < len(leaf):
        if i < len(current) and current[i] == leaf[j]:
            # Символы совпадают - двигаемся дальше
            i += 1
            j += 1
        else:
            if i < len(current):
                # Текущий символ не совпадает - нужно его обработать
                if current[i] in leaf[j:]:
                    # Символ понадобится позже - удаляем мешающие символы перед ним
                    # Находим, где этот символ понадобится
                    found_pos = leaf.find(current[i], j)
                    if found_pos != -1:
                        # Удаляем все от текущей позиции до нужного символа
                        to_delete = current[i:found_pos - j + i]
                        if to_delete:
                            path.append(("del", to_delete))
                            current = current[:i] + current[i + len(to_delete):]
                        continue
                
                # Заменяем текущий символ
                path.append(("sub", f"{current[i]}→{leaf[j]}"))
                current = current[:i] + leaf[j] + current[i+1:]
                i += 1
                j += 1
            else:
                # Достигли конца current - добавляем нужные символы в конец
                path.append(("add", leaf[j]))
                current += leaf[j]
                j += 1
    
    # Удаляем оставшиеся символы, если они есть
    if i < len(current):
        path.append(("del", current[i:]))
    
    return path

def simulate_operations(root, path):
    """Симулирует преобразование для проверки"""
    current = root
    steps = [f"Начало: '{current}'"]
    
    for op_type, op_desc in path:
        if op_type == "add":
            current += op_desc
            steps.append(f"Добавили '{op_desc}': '{current}'")
        elif op_type == "del":
            current = current.replace(op_desc, "", 1)
            steps.append(f"Удалили '{op_desc}': '{current}'")
        elif op_type == "sub":
            old, new = op_desc.split("→")
            # Заменяем первый найденный символ
            pos = current.find(old)
            if pos != -1:
                current = current[:pos] + new + current[pos+1:]
                steps.append(f"Заменили '{old}→{new}': '{current}'")
    
    return current, steps

def main():
    print("=== Правильный алгоритм преобразования ===")
    root = input("Корень: ").strip()
    leaf = input("Лист: ").strip()
    
    print(f"\nПреобразуем '{root}' -> '{leaf}'")
    
    path = find_evolution_path(root, leaf)
    
    print("\nОперации:")
    total_cost = len(path)
    for i, (op_type, op_desc) in enumerate(path, 1):
        print(f"{i}. {op_type} {op_desc}")
    
    print(f"\nОбщая стоимость: {total_cost}")
    
    # Проверяем корректность
    result, steps = simulate_operations(root, path)
    print(f"\nПроверка:")
    for step in steps:
        print(step)
    print(f"Результат: '{result}'")
    print(f"Совпадает с целью: {result == leaf}")

if __name__ == "__main__":
    main()