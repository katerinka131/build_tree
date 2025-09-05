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
        
    def find_evolution_path(self, w1, w2):
        """
        Находит максимальную общую последовательность символов, где позиции в w2
        не раньше, чем соответствующие позиции в w1.
        Возвращает список операций в формате [('op_type', value), ...]
        """
        w1 = str(w1)
        w2 = str(w2)
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
    
    