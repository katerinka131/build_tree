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
            for m in range(j, len(leaf_list)):
                path.append(("add", leaf_list[m]))
        
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
        dot.attr(label=f"Максимальная глубина дерева: {self.max_depth}", labelloc="t", labeljust="c")
        
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
    print("first:", longest_path, longest_leaf, root)
            
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
        print(leaf, path)
        tree.add_path_to_tree(best_path, leaf, best_node)
        print(best_path, leaf, best_node)
        print("node", best_node)
        print("leaf",leaf, "\n")
    return tree

if __name__ == "__main__":
    root = "XYZ"
    leaves = ["XYZA", "XYZB", "XYZC", "XYA", "XZA", "YZ", "XY", "ZA", "XYZD"]

    tree = build_optimal_tree(root, leaves)
    dot = tree.visualize()
    dot.render('evolution_tree', view=True, format='png')
    
    