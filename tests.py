import unittest
from genetic import EvolutionTree, build, build_optimal_tree

class TestEvolutionTree(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.tree = EvolutionTree("root")
    
    def test_initialization(self):
        """Тест инициализации дерева"""
        self.assertEqual(self.tree.root, "root")
        self.assertIn("root", self.tree.nodes)
        self.assertEqual(self.tree.nodes["root"]["depth"], 0)
        self.assertEqual(self.tree.nodes["root"]["edge_count"], 0)
    
    def test_find_evolution_path_simple(self):
        """Тест поиска пути эволюции для простых случаев"""
        # Добавление символов
        path = self.tree.find_evolution_path("abc", "abcd")
        self.assertEqual(path, [("add", "d")])
        
        # Удаление символов
        path = self.tree.find_evolution_path("abcd", "abc")
        self.assertEqual(path, [("del", "d")])
        
        # Замена символов
        path = self.tree.find_evolution_path("abc", "axc")
        self.assertEqual(path, [("sub", "b→x")])
    
    
    def test_add_node(self):
        """Тест добавления узлов"""
        child = self.tree.add_node("root", "child1", ("add", "x"), 1)
        self.assertEqual(child, "child1")
        self.assertIn("child1", self.tree.nodes)
        self.assertEqual(self.tree.nodes["root"]["edge_count"], 1)
        self.assertEqual(self.tree.nodes["child1"]["depth"], 1)
    

    def test_get_available_nodes(self):
        """Тест получения доступных узлов"""
        available = self.tree.get_available_nodes()
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0][0], "root")
        
        # Добавляем узел и проверяем доступность
        self.tree.add_node("root", "child", ("add", "x"), 1)
        available = self.tree.get_available_nodes()
        self.assertEqual(len(available), 2)  # root и child
    
    def test_add_path_to_tree(self):
        """Тест добавления пути в дерево"""
        path = [("add", "a"), ("add", "b")]
        result = self.tree.add_path_to_tree(path, "rootab", "root")
        self.assertEqual(result, "rootab")
        self.assertIn("rootab", self.tree.leaves)
        self.assertEqual(self.tree.nodes["roota"]["depth"], 1)
        self.assertEqual(self.tree.nodes["rootab"]["depth"], 2)
    
    def test_build_function(self):
        """Тест функции build"""
        leaves = ["abc", "axc", "abcd"]
        tree = build("root", leaves)
        
        self.assertEqual(len(tree.leaves), 3)
        self.assertGreater(len(tree.nodes), 1)
        for leaf in leaves:
            self.assertIn(leaf, tree.leaves)
    
    def test_build_optimal_tree(self):
        """Тест функции build_optimal_tree"""
        leaves = ["abc", "axc", "abcd", "ab"]
        tree = build_optimal_tree("root", leaves)
        
        self.assertEqual(len(tree.leaves), 4)
        self.assertGreater(len(tree.nodes), 1)
        for leaf in leaves:
            self.assertIn(leaf, tree.leaves)
    
    def test_visualize(self):
        """Тест визуализации (проверяем, что функция не падает)"""
        self.tree.add_node("root", "child", ("add", "x"), 1)
        dot = self.tree.visualize()
        self.assertIsNotNone(dot)
        self.assertTrue(hasattr(dot, 'node'))
        self.assertTrue(hasattr(dot, 'edge'))

class TestEdgeCases(unittest.TestCase):
    
    def test_empty_leaves(self):
        """Тест с пустым списком листьев"""
        tree = build("root", [])
        self.assertEqual(len(tree.leaves), 0)
        self.assertEqual(len(tree.nodes), 1)
    
    def test_same_root_and_leaf(self):
        """Тест когда корень и лист одинаковы"""
        tree = build("root", ["root"])
        self.assertEqual(len(tree.leaves), 1)
        self.assertEqual(len(tree.nodes), 1)
    
    def test_duplicate_leaves(self):
        """Тест с дублирующимися листьями"""
        tree = build("root", ["leaf", "leaf"])
        self.assertEqual(len(tree.leaves), 1)  # Дубликаты должны быть удалены
    
    def test_long_paths(self):
        """Тест с длинными путями"""
        long_string = "a" * 100
        leaves = [long_string + str(i) for i in range(3)]
        tree = build("root", leaves)
        
        self.assertEqual(len(tree.leaves), 3)
        self.assertGreater(len(tree.nodes), 3)

if __name__ == "__main__":
    unittest.main()