from graphviz import Digraph

# Создаем граф
dot = Digraph(comment='Алгоритм построения эволюционного дерева', format='png')
dot.attr(rankdir='TB', fontname='Arial', fontsize='16')

# ----------------------------
# Блок-схема алгоритма
# ----------------------------
with dot.subgraph(name='cluster_algorithm') as algo:
    algo.attr(label='Алгоритм построения оптимального дерева', style='rounded', color='blue', fontsize='16', bgcolor='lightgray')
    
    # Узлы алгоритма
    algo.node('start', 'Начало', shape='ellipse', fillcolor='lightgreen', style='filled')
    algo.node('init', 'Инициализация дерева\nс корневым узлом', fillcolor='lightyellow', style='filled')
    algo.node('find_paths', 'Для каждого листа находим путь\nот корня (find_evolution_path)', fillcolor='lightblue', style='filled')
    algo.node('sort_paths', 'Сортируем пути по длине\n(от самого длинного)', fillcolor='lightcyan', style='filled')
    algo.node('add_longest', 'Добавляем самый длинный путь\nв дерево (add_path_to_tree)', fillcolor='lightcoral', style='filled')
    algo.node('process_others', 'Для каждого оставшегося листа:', fillcolor='lightyellow', style='filled')
    algo.node('get_available', 'Получаем доступные узлы\n(get_available_nodes)', fillcolor='lightblue', style='filled')
    algo.node('find_best', 'Для каждого доступного узла:\n- Находим путь до листа\n- Вычисляем score = (глубина, доступные ребра)', fillcolor='lightcyan', style='filled')
    algo.node('select_best', 'Выбираем лучший узел\nпо минимальному score', fillcolor='lightcoral', style='filled')
    algo.node('add_path', 'Добавляем путь от выбранного узла\nк листу (add_path_to_tree)', fillcolor='lightblue', style='filled')
    algo.node('check_more', 'Еще листы?', shape='diamond', fillcolor='lightyellow', style='filled')
    algo.node('visualize', 'Визуализируем дерево\n(visualize)', fillcolor='lightcyan', style='filled')
    algo.node('end', 'Конец', shape='ellipse', fillcolor='lightgreen', style='filled')

    # Связи между узлами
    algo.edge('start', 'init')
    algo.edge('init', 'find_paths')
    algo.edge('find_paths', 'sort_paths')
    algo.edge('sort_paths', 'add_longest')
    algo.edge('add_longest', 'process_others')
    algo.edge('process_others', 'get_available')
    algo.edge('get_available', 'find_best')
    algo.edge('find_best', 'select_best')
    algo.edge('select_best', 'add_path')
    algo.edge('add_path', 'check_more')
    algo.edge('check_more', 'process_others', label='Да')
    algo.edge('check_more', 'visualize', label='Нет')
    algo.edge('visualize', 'end')

# ----------------------------
# Детализация ключевых функций
# ----------------------------
with dot.subgraph(name='cluster_functions') as func:
    func.attr(label='Детализация функций', style='rounded', color='green', fontsize='14', bgcolor='lightyellow')
    
    # find_evolution_path
    func.node('find_path', 'find_evolution_path(root, leaf):\n1. Посимвольное сравнение\n2. Операции: add/del/sub\n3. Оптимизация пути', fillcolor='lightblue', style='filled')
    
    # add_path_to_tree
    func.node('add_path', 'add_path_to_tree(path, leaf, node):\n1. Обработка операций пути\n2. Создание узлов с проверкой\n3. Ограничение: ≤3 ребенка на узел', fillcolor='lightcyan', style='filled')
    
    # get_available_nodes
    func.node('get_avail', 'get_available_nodes():\nВозвращает узлы с <3 детей\n(node, depth, edge_count)', fillcolor='lightcoral', style='filled')
    
    # visualize
    func.node('viz', 'visualize():\n- Создание графа Graphviz\n- Цветовая кодировка операций\n- Отображение глубины', fillcolor='lightgreen', style='filled')

# ----------------------------
# Связи между алгоритмом и функциями
# ----------------------------
dot.edge('find_paths', 'find_path', style='dashed', color='gray')
dot.edge('add_longest', 'add_path', style='dashed', color='gray')
dot.edge('get_available', 'get_avail', style='dashed', color='gray')
dot.edge('visualize', 'viz', style='dashed', color='gray')
dot.edge('find_best', 'find_path', style='dashed', color='gray')
dot.edge('add_path', 'add_path', style='dashed', color='gray')

# ----------------------------
# Легенда
# ----------------------------
with dot.subgraph(name='cluster_legend') as legend:
    legend.attr(label='Легенда', style='rounded', color='purple', fontsize='12', bgcolor='white')
    
    legend.node('l1', 'Основной алгоритм', fillcolor='lightblue', style='filled')
    legend.node('l2', 'Функции реализации', fillcolor='lightcyan', style='filled')
    legend.node('l3', 'Условия/проверки', fillcolor='lightyellow', style='filled')
    legend.node('l4', 'Начало/Конец', fillcolor='lightgreen', style='filled')
    legend.node('l5', 'Связь с функциями', shape='point')
    
    dot.edge('l5', 'l5', label='dashed line', style='dashed', color='gray')

# Сохраняем и рендерим
dot.render('evolution_algorithm_visualization', view=True, cleanup=True)
print("Блок-схема алгоритма сохранена в файл 'evolution_algorithm_visualization.png'")