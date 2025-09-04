from collections import defaultdict
from itertools import permutations
from graphviz import Digraph

class EvolutionTree:
    def __init__(self, root):
        self.root = root
        self.nodes = {root: {"children": [], "parent": None, "depth": 0, "op": None}}
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
    
    def add_path(self, leaf, path):
        current = self.root
        remaining_path = path.copy()
        
        while remaining_path and current not in self.leaves:
            found = False
            for child_data in self.nodes[current]["children"]:
                if child_data["op"] == remaining_path[0]:
                    current = child_data["node"]
                    remaining_path.pop(0)
                    found = True
                    break
            
            if not found:
                break
        
        if current in self.leaves:
            return False
            
        for op in remaining_path:
            if self.edge_count[current] >= 3 or op[0] in self.edge_types[current]:
                return False
                
            new_node = self._apply_op(current, op)
            
            self.nodes[new_node] = {
                "children": [],
                "parent": current,
                "depth": self.nodes[current]["depth"] + 1,
                "op": op
            }
            
            self.nodes[current]["children"].append({
                "node": new_node,
                "op": op
            })
            
            self.edge_count[current] += 1
            self.edge_types[current].add(op[0])
            current = new_node
        
        self.leaves.add(current)
        return True
    
    def _apply_op(self, node, op):
        op_type, op_desc = op
        if op_type == "add":
            return node + op_desc
        elif op_type == "del":
            return node.replace(op_desc, "", 1)
        elif op_type == "sub":
            old, new = op_desc.split("→")
            return node.replace(old, new, 1)
        raise ValueError(f"Unknown operation type: {op_type}")

    def find_alternative_path(self, target_leaf):
        # Ищем все подходящие узлы, отсортированные по глубине
        nodes_by_depth = defaultdict(list)
        for node, data in self.nodes.items():
            nodes_by_depth[data["depth"]].append(node)
        
        for depth in sorted(nodes_by_depth.keys()):
            for node in nodes_by_depth[depth]:
                if node in self.leaves or self.edge_count[node] >= 3:
                    continue
                
                # 1. Пытаемся использовать стандартный путь
                path = self.find_evolution_path(node, target_leaf)
                if path and self._can_use_path(node, path):
                    return (node, path)
                
                # 2. Если стандартный путь не подходит, добавляем недостающую операцию
                missing_ops = self._get_missing_operations(node)
                
                # Проверяем в порядке: красная (DEL), зеленая (ADD), синяя (SUB)
                for op_type in ["del", "add", "sub"]:
                    if op_type not in missing_ops:
                        continue
                    
                    new_op = self._create_missing_operation(node, op_type)
                    if not new_op:
                        continue
                    
                    new_node = self._apply_op(node, new_op)
                    new_path = self.find_evolution_path(new_node, target_leaf)
                    
                    if new_path and self._can_use_path(node, [new_op] + new_path):
                        return (node, [new_op] + new_path)
        
        return None

    def _can_use_path(self, node, path):
        """Проверяет, можно ли использовать путь с учетом цветов стрелок"""
        current = node
        for op in path:
            op_type = op[0]
            if op_type in self.edge_types[current]:
                return False  # Цвет стрелки уже используется
            current = self._apply_op(current, op)
        return True

    def _get_missing_operations(self, node):
        """Возвращает отсутствующие типы операций в узле в порядке приоритета"""
        existing = self.edge_types[node]
        missing = []
        for op_type in ["del", "add", "sub"]:  # Красная, зеленая, синяя
            if op_type not in existing:
                missing.append(op_type)
        return missing

    def _create_missing_operation(self, node, op_type):
        """Создает операцию недостающего типа по заданным правилам"""
        if op_type == "del" and len(node) > 0:  # Красная - удаление
            return ("del", node[-1])
        elif op_type == "add" and len(node) > 0:  # Зеленая - добавление
            return ("add", node[-1])
        elif op_type == "sub" and len(node) > 1:  # Синяя - замена
            return ("sub", f"{node[-1]}→{node[-2]}")
        return None

    def visualize(self):
        dot = Digraph()
        dot.attr('node', shape='box', style='rounded')
        
        for node, data in self.nodes.items():
            label = f"{node}\n(depth: {data['depth']})"
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
    
    leaves_with_paths = []
    for leaf in leaves:
        path = tree.find_evolution_path(root, leaf)
        if path:
            leaves_with_paths.append((leaf, path, len(path)))
    
    # Сортируем по сложности (длине пути)
    leaves_with_paths.sort(key=lambda x: -x[2])
    
    # Основные попытки добавления
    for leaf, path, _ in leaves_with_paths:
        if not tree.add_path(leaf, path):
            for _ in range(5):  # Увеличиваем количество попыток
                alt_path = tree.find_alternative_path(leaf)
                if alt_path and tree.add_path(leaf, alt_path[1]):
                    break
    
    # Специальная обработка для "AB" если он не добавлен
    if "AB" in leaves and "AB" not in tree.leaves:
        # Ищем узел, от которого можно добавить DEL операцию
        for node in tree.nodes:
            if (tree.edge_count[node] < 3 and 
                "del" not in tree.edge_types[node] and 
                len(node) > 0):
                
                # Создаем операцию удаления последнего символа
                del_op = ("del", node[-1])
                new_node = tree._apply_op(node, del_op)
                
                # Находим путь от нового узла до "AB"
                path = tree.find_evolution_path(new_node, "AB")
                if path and tree._can_use_path(node, [del_op] + path):
                    tree.add_path("AB", [del_op] + path)
                    break
    
    return tree

def test1():
    root = "abcdefg"
    leaves = ["cdhixyz"]
    tree = build_optimal_tree(root, leaves)
    
    assert len(tree.edge_count) == 5

def test2():
    root = "abc"
    leaves = ["bc"]
    tree = build_optimal_tree(root, leaves)
    
    assert len(tree.edge_count) == 1

def test3():
    root = "bc"
    leaves = ["abc"]
    tree = build_optimal_tree(root, leaves)

def test4():
    root = "bcgh"
    leaves = ["abgl"]
    tree = build_optimal_tree(root, leaves)  
    assert len(tree.edge_count) == 3


def test5():
    root = "a"
    leaves = ["b"]
    tree = build_optimal_tree(root, leaves)  
    assert len(tree.edge_count) == 1

if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    root = "fdxc"
    leaves = ["fdxclpok"]

    tree = build_optimal_tree(root, leaves)
    dot = tree.visualize()
    dot.render('evolution_tree', view=True, format='png')