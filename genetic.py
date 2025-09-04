from collections import defaultdict
from graphviz import Digraph

class EvolutionTree:
    def __init__(self, root):
        self.root = root
        self.nodes = {root: {"children": [], "parent": None, "depth": 0, "op": None}}
        self.leaves = set()
        self.edge_count = defaultdict(int)
    
    def find_evolution_path(self, root, leaf):
        root_list = list(root)
        leaf_list = list(leaf)
        path = []
        i = j = 0
        
        while j < len(leaf_list):
            if i < len(root_list) and root_list[i] == leaf_list[j]:
                i += 1
                j += 1
            else:
                found = -1
                for k in range(i, len(root_list)):
                    if root_list[k] == leaf_list[j]:
                        found = k
                        break
                
                if found != -1:
                    if found > i:
                        deleted = ''.join(root_list[i:found])
                        path.append(("del", deleted))
                        del root_list[i:found]
                    i += 1
                    j += 1
                else:
                    if i < len(root_list):
                        path.append(("sub", f"{root_list[i]}→{leaf_list[j]}"))
                        root_list[i] = leaf_list[j]
                        i += 1
                        j += 1
                    else:
                        path.append(("add", leaf_list[j]))
                        j += 1
        
        if i < len(root_list):
            path.append(("del", ''.join(root_list[i:])))
        return path

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
            if self.edge_count[current] >= 3:
                return False
                
            op_type, op_desc = op
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
    
    def find_alternative_path(self, target_leaf):
        best_path = None
        best_depth = float('inf')
        
        for node in self.nodes:
            if node in self.leaves or self.edge_count[node] >= 3:
                continue
                
            path = self.find_evolution_path(node, target_leaf)
            total_depth = self.nodes[node]["depth"] + len(path)
            
            if total_depth < best_depth:
                best_depth = total_depth
                best_path = (node, path)
        
        return best_path

    def visualize(self):
        dot = Digraph()
        dot.attr('node', shape='box', style='rounded')
        
        for node, data in self.nodes.items():
            label = f"{node}\n(depth: {data['depth'] + 1})"
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
    paths = []
    
    for leaf in leaves:
        path = tree.find_evolution_path(root, leaf)
        path_sorted = sorted(path, key=lambda x: (x[0] != "sub", x[0] != "del", x[0] != "add"))
        paths.append((leaf, path_sorted, len(path_sorted)))
    
    paths.sort(key=lambda x: -x[2])
    
    unprocessed = []
    for leaf, path, _ in paths:
        if not tree.add_path(leaf, path):
            unprocessed.append((leaf, path))
    
    while unprocessed:
        leaf, path = unprocessed.pop(0)
        result = tree.find_alternative_path(leaf)
        
        if result:
            node, alt_path = result
            if tree.add_path(leaf, alt_path):
                continue
        
        unprocessed.append((leaf, path))
        if len(unprocessed) == len(leaves):
            break
    
    return tree

# Пример использования
root = "TBCDEFG"
leaves = ["AB", "AXCD", "AXYEFG", "ABCDMN", "MN", "BCD"]

tree = build_optimal_tree(root, leaves)
dot = tree.visualize()
dot.render('evolution_tree', view=True, format='png')