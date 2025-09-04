from graphviz import Digraph

# Создаем граф
dot = Digraph(comment='Алгоритм построения дерева', format='png')
dot.attr(rankdir='TB', fontname='Arial', fontsize='12')

# ----------------------------
# 1. Блок-схема алгоритма
# ----------------------------
with dot.subgraph(name='cluster_algorithm') as algo:
    algo.attr(label='Алгоритм', style='rounded', color='gray', fontsize='14')
    
    # Узлы
    algo.node('start', 'Начало', shape='ellipse', fillcolor='lightpink', style='filled')
    algo.node('step1', 'Построить кратчайшие пути\nот корня до всех листьев\nи отсортировать по длине')
    algo.node('step2', 'Построить самый длинный путь\nот корня к листу')
    algo.node('step3', 'Для каждого оставшегося пути:')
    algo.node('step3_1', 'Проверяем есть ли общий узел с текущим графом\nот которого отходит меньше 3 стрелок')
    algo.node('step3_1_yes', 'Достроить путь', fillcolor='lightyellow', style='filled')
    algo.node('step3_1_no', 'Находим кратчайший путь\nот узлов с < 3 стрелками и  добавляем его ' , fillcolor='lightblue', style='filled')
    algo.node('end', 'Граф построен', shape='ellipse', fillcolor='lightpink', style='filled')

    # Связи (исправлено - сначала все рёбра без label)
    algo.edge('start', 'step1')
    algo.edge('step1', 'step2')
    algo.edge('step2', 'step3')
    algo.edge('step3', 'step3_1')
    algo.edge('step3_1', 'step3_1_yes', label='Да')
    algo.edge('step3_1', 'step3_1_no', label='Нет')
    algo.edge('step3_1_yes', 'step3')
    algo.edge('step3_1_no', 'step3')

    algo.edge('step3', 'end', label='Все пути обработаны')

# ----------------------------
# 2. Пример построения графа
# ----------------------------


# Сохраняем и рендерим
dot.render('algorithm_visualization', view=True)
print("Граф сохранен в файл 'algorithm_visualization.png'")