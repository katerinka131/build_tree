from collections import defaultdict, deque
from itertools import permutations
from graphviz import Digraph
import heapq

class EvolutionTree:
    def __init__(self, root):
        self.root = root
        self.nodes = {root: {"children": [], "parent": None, "depth": 0, "op": None, "edge_count": 0, "name":root}}
        self.leaves = set()
        self.edge_count = defaultdict(int)
        self.edge_types = defaultdict(set)
        self.max_depth = 0  # Переменная для отслеживания максимальной глубины
        
    def find_evolution_path(self, root, leaf):
        """Находит путь эволюции от root к leaf с использованием алгоритма редакционного расстояния"""
        n1, n2 = len(root), len(leaf)
        
        dp = [[0] * (n1 + 1) for _ in range(n2 + 1)]
        path = [[None] * (n1 + 1) for _ in range(n2 + 1)]
        
        for p in range(n1 + 1):
            dp[0][p] = p
            if p > 0:
                path[0][p] = ('delete', 0, p-1)
        
        for q in range(1, n2 + 1):
            dp[q][0] = q
            path[q][0] = ('insert', q-1, 0)
        
        # Заполнение DP таблицы
        for q in range(1, n2 + 1):
            for p in range(1, n1 + 1):
                i = p - 1  # Индекс в root
                j = q - 1  # Индекс в leaf
                
                cost = 0 if root[i] == leaf[j] else 1
                
                options = [
                    (dp[q-1][p] + 1, ('insert', q-1, p)),      # Вставка
                    (dp[q][p-1] + 1, ('delete', q, p-1)),      # Удаление
                    (dp[q-1][p-1] + cost, ('change', q-1, p-1)) # Замена/совпадение
                ]
                
                min_val, best_path = min(options, key=lambda x: x[0])
                dp[q][p] = min_val
                path[q][p] = best_path
        
        operations = []
        q, p = n2, n1
        
        while q > 0 or p > 0:
            if path[q][p] is None:
                break
                
            op_type, next_q, next_p = path[q][p]
            
            if op_type == 'insert':
                # Вставка символа leaf[q-1] перед позицией p
                operations.append(('add', leaf[q-1], p))
            elif op_type == 'delete':
                # Удаление символа root[p-1] на позиции p-1
                operations.append(('del', root[p-1], p-1))
            elif op_type == 'change':
                # Замена символа root[p-1] на leaf[q-1]
                if root[p-1] != leaf[q-1]:
                    operations.append(('sub', f"{root[p-1]}→{leaf[q-1]}", p-1))
                # Для совпадений не добавляем операцию
            
            q, p = next_q, next_p
        
        operations.reverse()
        
        # Преобразование в формат оригинальной функции
        formatted_path = []
        current_pos = 0
        
        for op in operations:
            op_type, value, pos = op
            
            if op_type == 'add':
                formatted_path.append(("add", value))
                current_pos += 1
                
            elif op_type == 'del':
                # Проверяем, есть ли следующие удаления для группировки
                delete_chars = [value]
                next_idx = operations.index(op) + 1 if operations.index(op) + 1 < len(operations) else -1
                
                if next_idx != -1 and operations[next_idx][0] == 'del' and operations[next_idx][2] == pos + 1:
                    # Группируем последовательные удаления
                    while next_idx < len(operations) and operations[next_idx][0] == 'del':
                        delete_chars.append(operations[next_idx][1])
                        next_idx += 1
                    
                    formatted_path.append(("del", ''.join(delete_chars)))
                    # Пропускаем уже обработанные операции
                    for _ in range(len(delete_chars) - 1):
                        operations.pop(operations.index(op) + 1)
                else:
                    formatted_path.append(("del", value))
                
            elif op_type == 'sub':
                formatted_path.append(("sub", value))
                current_pos += 1
        
        # Оптимизация пути (сохранение логики оригинальной функции)
        optimized_path = []
        adds = []
        dels = []
        subs = []
        
        for op in formatted_path:
            if op[0] == "add":
                adds.append(op)
            elif op[0] == "del":
                dels.append(op)
            elif op[0] == "sub":
                subs.append(op)
        
        # Сохраняем порядок: сначала удаления, затем замены, затем добавления
        while dels and subs:
            optimized_path.append(dels.pop(0))
            optimized_path.append(subs.pop(0))

        optimized_path.extend(dels)
        optimized_path.extend(subs)
        optimized_path.extend(adds)
        
        return optimized_path
    
    def add_node(self, parent, child, op, depth):
        """Добавить узел в дерево"""
        
        if depth > self.max_depth:
            self.max_depth = depth
        
        if child not in self.nodes:
            # Создаем новый узел
            self.nodes[child] = {
                "children": [],
                "parent": parent,
                "depth": depth,
                "op": op,
                "edge_count": 0,
                "name": child
            }
            self.nodes[parent]["children"].append({
                "node": child,
                "op": op
            })
            self.nodes[parent]["edge_count"] += 1
            return child
        
        elif self.nodes[child]["edge_count"] < 3:
            # Узел существует и у него есть место для детей
            # Просто возвращаем существующий узел
            return child
        
        else:
            # У узла уже 3 ребенка, создаем новый узел с уникальным именем
            i = 1
            while f"{child}_{i}" in self.nodes:
                i += 1
            
            new_child_name = f"{child}_{i-1}"
            if new_child_name in self.nodes and  self.nodes[new_child_name]["edge_count"] < 3:
                return new_child_name
            # Создаем новый узел
            new_child_name = f"{child}_{i}"
            self.nodes[new_child_name] = {
                "children": [],
                "parent": parent,
                "depth": depth,
                "op": op,
                "edge_count": 0,
                "name": child
            }
            self.nodes[parent]["children"].append({
                "node": new_child_name,
                "op": op
            })
            self.nodes[parent]["edge_count"] += 1
            
            return new_child_name
    
    def get_available_nodes(self, max_edges=3):
        """Получить узлы, к которым можно добавить детей (меньше 3 ребер)"""
        available = []
        for node, data in self.nodes.items():
            if data["edge_count"] < max_edges:
                available.append((node, data["depth"], data["edge_count"]))
        return available
    
    # def get_available_nodes_viktar(self, max_edges=3):
    #     """Получить узлы, к которым можно добавить детей (меньше 3 ребер)"""
    #     return map(lambda node, data: (node, data["depth"], data["edge_count"]), filter(lambda _node, data: data["edge_count"] < max_edges, self.nodes.items()))

   
    def add_path_to_tree(self, path_sequence, leaf, current_node):
            
        depth = self.nodes[current_node]["depth"]
        
        for i, (op_type, op_value) in enumerate(path_sequence):
            # Генерируем имя дочернего узла на основе ТЕКУЩЕГО узла
            current_node_name = current_node  # Сохраняем текущее имя
            
            if op_type == "add":
                child_node = current_node_name + op_value
            elif op_type == "del":
                child_node = current_node_name.replace(op_value, "", 1)
            elif op_type == "sub":
                old, new = op_value.split("→")
                child_node = current_node_name.replace(old, new, 1)
            else:
                child_node = current_node_name
            
            # Если это последняя операция, используем leaf как имя
            if i == len(path_sequence) - 1 and leaf:
                child_node = leaf
            
            
            # Добавляем узел в дерево
            if child_node != current_node_name:
                depth += 1
                result_node = self.add_node(current_node_name, child_node, (op_type, op_value), depth)
                
                current_node = result_node  # Обновляем current_node для следующей итерации
            
        
        # Помечаем конечный узел как лист
        if current_node == leaf:
            self.leaves.add(leaf)
        
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
        
        # Добавляем информацию о максимальной глубине
        dot.attr(label=f"Глубина дерева: {self.max_depth}", labelloc="t", labeljust="c")
        
        return dot

def build_optimal_tree(root, leaves):
    tree = EvolutionTree(root)
    tree.leaves = set(leaves)
    
    # Шаг 1: Находим все пути до листьев и сортируем по длине
    paths = []
    for leaf in leaves:
        path = tree.find_evolution_path(root, leaf)
        paths.append((len(path), path, leaf))
    paths.sort(key=lambda x: x[0], reverse=True)
    longest_path_length, longest_path, longest_leaf = paths[0]
    
    tree.add_path_to_tree(longest_path, longest_leaf, root)
    
            
    leaves = []     
    for _,_, leaf in paths[1:]:
        best_candidates = []
        available_nodes = tree.get_available_nodes()
        for node, depth_node, edge_count in available_nodes:
            path = tree.find_evolution_path(tree.nodes[node]["name"], leaf)

            depth_increase = len(path) + depth_node
            
            edges_available = edge_count
            
            # Добавляем кандидата с его критериями
            best_candidates.append({
                'node': node,
                'path_remainder': path,
                'score': (depth_increase, edges_available) 
            })
        
        best_candidates.sort(key=lambda x: x['score'], reverse=False)
        best_candidate = best_candidates[0]
        best_node = best_candidate['node']
        best_path = best_candidate['path_remainder']
        path = tree.find_evolution_path(tree.nodes[best_node]["name"], leaf)
        
        tree.add_path_to_tree(best_path, leaf, best_node)
        
    return tree



if __name__ == "__main__":
    from tree_data import root, leaves
    
    tree = build_optimal_tree(root, leaves)
    dot = tree.visualize()
    dot.render('evolution_tree', view=True, format='png')
    
    