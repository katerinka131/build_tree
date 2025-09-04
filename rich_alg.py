from collections import defaultdict, deque
from itertools import permutations
from graphviz import Digraph
import heapq

class EvolutionTree:
    def __init__(self, root):
        self.root = root
        self.nodes = {root: {"children": [], "parent": None, "depth": 0, "op": None, "edge_count": 0}}
        self.leaves = set()
        self.edge_count = defaultdict(int)
        self.edge_types = defaultdict(set)

    def find_evolution_path(self, root, leaf):
        root_list = list(root)
        leaf_list = list(leaf)
        path = []
        j = 0
        
        while j < len(leaf_list):
            if j < len(root_list) and root_list[j] == leaf_list[j]:
                
                j += 1
            else:
                found = -1
                for k in range(j, len(root_list)):
                    if root_list[k] == leaf_list[j]:
                        found = k
                        break
                
                if found != -1:
                    if found > j:
                        deleted = ''.join(root_list[j:found])
                        path.append(("del", deleted))
                        del root_list[j:found]
                    
                    j += 1
                else:
                    if j < len(root_list):
                        path.append(("sub", f"{root_list[j]}→{leaf_list[j]}"))
                        root_list[j] = leaf_list[j]
                        
                        j += 1
                    else:
                        break
        
        if j < len(leaf_list):
            added = ''.join(leaf_list[j:])
            path.append(("add", added))
        
        if j < len(root_list):
            deleted = ''.join(root_list[j:])
            path.append(("del", deleted))
        
        optimized_path = []
        adds = []
        dels = []
        subs = []
        
        for op in path:
            if op[0] == "add":
                adds.append(op)
            elif op[0] == "del":
                dels.append(op)
            elif op[0] == "sub":
                subs.append(op)
        
        while dels and subs:
            optimized_path.append(dels.pop(0))
            optimized_path.append(subs.pop(0))
        
        optimized_path.extend(dels)
        optimized_path.extend(subs)
        optimized_path.extend(adds)
        
        return optimized_path
    
    def add_node(self, parent, child, op, depth):
        """Добавить узел в дерево"""
        if child not in self.nodes:
            self.nodes[child] = {
                "children": [],
                "parent": parent,
                "depth": depth,
                "op": op,
                "edge_count": 0
            }
            self.nodes[parent]["children"].append({
                "node": child,
                "op": op
            })
            self.nodes[parent]["edge_count"] += 1
        return child
    
    def get_available_nodes(self, max_edges=3):
        """Получить узлы, к которым можно добавить детей (меньше 3 ребер)"""
        available = []
        for node, data in self.nodes.items():
            if data["edge_count"] < max_edges:
                available.append((node, data["depth"], data["edge_count"]))
        return available
    
    def find_best_insertion_point(self, path, available_nodes):
        """Найти лучшую точку вставки для пути"""
        best_score = float('-inf')
        best_insertion = None
        best_path_remainder = None
        
        for node, depth, edge_count in available_nodes:
            # Проверяем, можно ли вставить путь начиная с этого узла
            if node in path:
                node_index = path.index(node)
                path_remainder = path[node_index + 1:]
                
                # Вычисляем score по критериям
                # 1. Меньшее увеличение глубины (чем меньше новых узлов, тем лучше)
                depth_increase = len(path_remainder)
                
                # 2. Чем ниже начинается путь (большая глубина), тем лучше
                start_depth = depth
                
                # 3. Чем меньше ребер у вершины, тем лучше
                edges_available = 3 - edge_count
                
                # Комбинированный score (чем больше, тем лучше)
                score = (-depth_increase * 1000) + (start_depth * 100) + edges_available
                
                if score > best_score:
                    best_score = score
                    best_insertion = node
                    best_path_remainder = path_remainder
        
        return best_insertion, best_path_remainder
    
    def add_path_to_tree(self, path_sequence, leaf, current_node):
        """Добавить путь в дерево"""
        
        depth = 0
        
        for i, (op_type, op_value) in enumerate(path_sequence):
            # Генерируем имя дочернего узла
            if op_type == "add":
                child_node = current_node + op_value
            elif op_type == "del":
                child_node = current_node[:-len(op_value)] if len(op_value) <= len(current_node) else ""
            elif op_type == "sub":
                 old, new = op_value.split("→")
                 child_node = current_node.replace(old, new, 1)

                
            else:
                child_node = current_node
            
            # Если это последняя операция, используем leaf как имя
            if i == len(path_sequence) - 1 and leaf:
                child_node = leaf
            
            # Добавляем узел в дерево
            if child_node != current_node:
                depth += 1
                current_node = self.add_node(current_node, child_node, (op_type, op_value), depth)
        
        return current_node

    def visualize(self):
        dot = Digraph()
        dot.attr('node', shape='box', style='rounded')
        
        for node, data in self.nodes.items():
            label = f"{node}\n(depth: {data['depth']}, edges: {data['edge_count']})"
            if node in self.leaves:
                dot.node(node, label, color='green', penwidth='2')
            else:
                dot.node(node, label)
            
            for child in data["children"]:
                op = child["op"]
                edge_color = {
                    "add": "green",
                    "del": "red",
                    "sub": "blue"
                }[op[0]]
                dot.edge(node, child["node"], label=op[1], color=edge_color, fontcolor=edge_color)
        
        return dot

def build_optimal_tree(root, leaves):
    tree = EvolutionTree(root)
    tree.leaves = set(leaves)
    
    # Шаг 1: Находим все пути до листьев и сортируем по длине
    paths = []
    for leaf in leaves:
        path = tree.find_evolution_path(root, leaf)
        print("пути до листьев:", path)
        paths.append((len(path), path, leaf))
    
    # Сортируем пути по убыванию длины
    paths.sort(key=lambda x: x[0], reverse=True)
    
    # Шаг 2: Строим самый длинный путь
    if paths:
        longest_path_length, longest_path, longest_leaf = paths[0]
        tree.add_path_to_tree(longest_path, longest_leaf, root)
    
    # Шаг 3: Обрабатываем остальные пути
    for path_length, path, leaf in paths[1:]:
        print("path", path)
        print("leaf", leaf)
        # Получаем доступные узлы (с менее чем 3 ребрами)
        available_nodes = tree.get_available_nodes()
        
        # Преобразуем путь в последовательность узлов для анализа
        path_nodes = [root]
        current = root
        for op_type, op_value in path:
            if op_type == "add":
                current = current + op_value
            elif op_type == "del":
                current = current[:-len(op_value)] if len(op_value) <= len(current) else ""
            elif op_type == "sub":
                old, new = op_value.split("→")
                current = current.replace(old, new, 1)
            path_nodes.append(current)
        print(path_nodes)
        # Находим лучшую точку вставки
        insertion_point, path_remainder = tree.find_best_insertion_point(path_nodes, available_nodes)
        print ("insertion_point, path_remainder", insertion_point, path_remainder)
        if insertion_point:
            # Находим индекс точки вставки в path_nodes
            insertion_index = path_nodes.index(insertion_point)
            print("insertion_index:", insertion_index)
            
            # Определяем, сколько операций уже выполнено до этой точки
            # Каждая операция создает новый узел, поэтому количество операций = индекс узла
            ops_completed = insertion_index
            print("ops_completed:", ops_completed)
            
            # Берем оставшиеся операции
            remaining_ops = tree.find_evolution_path(insertion_point, leaf)
            print("path", path)
            print("remaining_ops:", remaining_ops, "\n\n\n")
            
            # Добавляем путь от точки вставки
            tree.add_path_to_tree(remaining_ops, leaf, insertion_point)
        else:
            # Если не нашли подходящую точку вставки, добавляем полный путь от корня
            print("Добавляем от корня:", path)
            tree.add_path_to_tree(path, leaf, root)
    
    return tree

if __name__ == "__main__":
    root = "fdxc"
    # leaves = ["dx", "xc", "c", "fn", "mn"]
    leaves = ["fdm","fdl", "fdk","fdo"]

    tree = build_optimal_tree(root, leaves)
    dot = tree.visualize()
    dot.render('evolution_tree', view=True, format='png')
    print("Дерево построено успешно!")