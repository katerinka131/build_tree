def find_evolution_path(w1: str, w2: str):
    """
    Находит максимальную общую последовательность символов, где позиции в w2
    не раньше, чем соответствующие позиции в w1.
    Возвращает список операций в формате [('op_type', value), ...]
    """
    n1, n2 = len(w1), len(w2)
    
    # Находим максимальную общую подпоследовательность
    common = []
    last = -1
    list_ind_w1 = []
    list_ind_w2 = []
    
    for i in range(n1):
        if last == -1:
            for j in range(min(i+1, n2)):
                if w1[i] == w2[j]:
                    list_ind_w1.append(i)
                    list_ind_w2.append(j)
                    last = j
                    break
        else:
            for j in range(last+1, min(last + i - list_ind_w1[-1] + 1, n2)):
                if w1[i] == w2[j]:
                    list_ind_w1.append(i)
                    list_ind_w2.append(j)
                    last = j
                    break
    
    # Строим операции на основе найденной общей подпоследовательности
    operations = []
    current_w2_pos = 0
    current_w1_pos = 0
    
    # Обрабатываем символы до первой общей позиции
    for i in range(len(list_ind_w2)):
        if i == 0:
            # Символы перед первым общим символом
            for j in range(list_ind_w2[0]):
                if current_w1_pos < n1:
                    operations.append(('sub', f"{w1[current_w1_pos]}→{w2[j]}"))
                    current_w1_pos += 1
                else:
                    operations.append(('add', w2[j]))
                current_w2_pos = j + 1
        
        # Добавляем общий символ (не добавляем операцию для совпадений)
        if current_w1_pos < list_ind_w1[i]:
            # Удаляем лишние символы из w1
            for k in range(current_w1_pos, list_ind_w1[i]):
                operations.append(('del', w1[k]))
        
        current_w1_pos = list_ind_w1[i] + 1
        current_w2_pos = list_ind_w2[i] + 1
        
        # Обрабатываем символы между общими символами
        if i < len(list_ind_w2) - 1:
            next_w2_pos = list_ind_w2[i+1]
            for j in range(current_w2_pos, next_w2_pos):
                if current_w1_pos < n1:
                    operations.append(('sub', f"{w1[current_w1_pos]}→{w2[j]}"))
                    current_w1_pos += 1
                else:
                    operations.append(('add', w2[j]))
                current_w2_pos = j + 1
    
    # Обрабатываем символы после последней общей позиции
    # Оставшиеся символы в w2
    for j in range(current_w2_pos, n2):
        if current_w1_pos < n1:
            operations.append(('sub', f"{w1[current_w1_pos]}→{w2[j]}"))
            current_w1_pos += 1
        else:
            operations.append(('add', w2[j]))
    
    # Оставшиеся символы в w1 (удаления)
    for k in range(current_w1_pos, n1):
        operations.append(('del', w1[k]))
    
    # Оптимизация пути (группировка последовательных операций одного типа)
    optimized_path = []
    i = 0
    
    while i < len(operations):
        op_type, value = operations[i]
        
        if op_type == 'del':
            # Группируем последовательные удаления
            delete_chars = [value]
            j = i + 1
            while j < len(operations) and operations[j][0] == 'del':
                delete_chars.append(operations[j][1])
                j += 1
            
            if len(delete_chars) > 1:
                optimized_path.append(('del', ''.join(delete_chars)))
                i = j
            else:
                optimized_path.append(('del', value))
                i += 1
        
        elif op_type == 'add':
            # Группируем последовательные добавления
            add_chars = [value]
            j = i + 1
            while j < len(operations) and operations[j][0] == 'add':
                add_chars.append(operations[j][1])
                j += 1
            
            if len(add_chars) > 1:
                optimized_path.append(('add', ''.join(add_chars)))
                i = j
            else:
                optimized_path.append(('add', value))
                i += 1
        
        else:  # sub
            optimized_path.append(('sub', value))
            i += 1
    
    return optimized_path

    
    
if __name__ == "__main__":
    # from tree_data import root, leaves - закомментировал, так как этого файла нет
    
    kol = find_evolution_path("abxcd", "ch")
    print(kol)