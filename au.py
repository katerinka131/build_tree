def find_evolution_path(w1: str, w2: str):
    """
    Находит максимальную общую последовательность символов, где позиции в w2
    не раньше, чем соответствующие позиции в w1.
    Возвращает список кортежей (pos_w1, pos_w2, char)
    """
    n1, n2 = len(w1), len(w2)
    common = []
    kol = 0
    last = -1
    list_ind_w1 = []
    list_ind_w2 = []
    for i in range(n1):
        if last == -1:
            for j in range(min(i+1, n2)):  # Здесь ошибки нет
                if w1[i] == w2[j]:
                    list_ind_w1.append(i)
                    list_ind_w2.append(j)
                    kol += 1
                    last = j
                    continue
        else:
            for j in range(last+1, min(last +i-list_ind_w1[-1]+1, n2)):  # ИСПРАВЛЕНО: range(last, max(i, n2))
                if w1[i] == w2[j]:
                    list_ind_w1.append(i)
                    list_ind_w2.append(j)
                    kol += 1
                    last = j
                    continue
    operations = []
    ind = 0
    for i in range(len(list_ind_w2) - 1):
        for j in range(ind,list_ind_w2[i]):
            operations.append(('sub', f"{w1[j]}->{w2[j]}"))
            ind = list_ind_w2[i]+1
        operations.append(('del', list_ind_w2[i], list_ind_w1[i]))
    
    print(list_ind_w1)
    print(list_ind_w2)
    l = 0
    if len(list_ind_w1 ) == 0:
        for i in range(n2):
            if i <= n1 -1:
                operations.append(('sub', f"{w1[i]}-> {w2[i]}"))
            else:
                operations.append(('add', w2[i]))
        print(operations)
        return list_ind_w1, list_ind_w2, kol
    for i in range(min(list_ind_w2[-1]+1, n2 - 1), n2): 
        
        if list_ind_w1[-1]+1+l  <= n1-1 and (i <= list_ind_w1[-1]+1 + l):

            operations.append(('sub', f"{w1[list_ind_w1[-1]+1 + l]}-> {w2[i]}"))
            l += 1
            
        else:
            operations.append(('add', w2[i]))
    if n1 > n2:
        operations.append(("del", w1[n2-1], n2))
    print(operations)
    return list_ind_w1, list_ind_w2, kol

    
    
if __name__ == "__main__":
    # from tree_data import root, leaves - закомментировал, так как этого файла нет
    
    list_ind_w1, list_ind_w2, kol = find_evolution_path("abc", "mlbc")
    print(kol)
    print(list_ind_w1)
    print(list_ind_w2)