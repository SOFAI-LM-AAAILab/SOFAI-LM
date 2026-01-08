import networkx as nx

class GraphColoringValidator:
    def __init__(self, dimacs_file):
        self.graph = self.load_graph_from_dimacs(dimacs_file)

    def load_graph_from_dimacs(self, file_path):
        """Loads a graph from a DIMACS format file."""
        G = nx.Graph()
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('e'):
                    _, u, v = line.strip().split()
                    G.add_edge(u, v)  # Treat u and v as strings (compatible with alphanumeric labels)
        return G

    def validate_coloring(self, coloring, confidence=False):
        """Validates the coloring of the graph and optionally calculates the completion score.
        
        Args:
            coloring (dict): A dictionary where keys are node labels (as strings),
                             and values are assigned colors (as integers).
            confidence (bool): If set to True, also returns the completion score.
        
        Returns:
            bool: True if the coloring is valid, False otherwise.
            list: List of edges where coloring fails.
            float (optional): Completion score, only returned if confidence is True.
        """
        errors = []
        for u, v in self.graph.edges():
            if coloring.get(u) == coloring.get(v):
                errors.append((u, v))

        is_valid = len(errors) == 0
        if confidence:
            completion_score = self.calculate_completion_score(coloring)
            return is_valid, errors, completion_score
        else:
            return is_valid, errors

    def calculate_completion_score(self, coloring):
        """Calculates the completion score as the percentage of nodes correctly colored.
        
        Args:
            coloring (dict): Coloring of the nodes.
        
        Returns:
            float: Completion score percentage.
        """
        total_nodes = len(self.graph.nodes())
        correctly_colored_nodes = sum(1 for n in self.graph.nodes() if coloring.get(n) is not None)
        completion_score = (correctly_colored_nodes / total_nodes) * 100
        return completion_score

# # Example Usage
# if __name__ == "__main__":
#     # The DIMACS file should correspond to the one used by your generator and solver
#     validator = GraphColoringValidator("/work/vedant/2024/final_cpde/coling-CODE/problem_generator/graph_coloring_problems/graph_n50_graph0.col")
    
#     # Sample coloring output from the solver (adjust to your actual output)
#     coloring = {
#         'aa': 0, 'f': 1, 'i': 2, 'x': 3, 'at': 0, 'af': 1, 'o': 4, 'm': 5, 
#         'c': 5, 'w': 2, 'l': 3, 't': 4, 'b': 5, 'ak': 4, 'as': 0, 'aj': 4,
#         'aq': 5, 'ab': 6, 'ai': 3, 'g': 7, 'd': 0, 'aw': 7, 'q': 2, 'v': 4,
#         'e': 3, 'p': 7, 'av': 6, 'u': 1, 'z': 0, 'ar': 3, 'an': 6, 'a': 1,
#         'ah': 8, 'au': 6, 's': 5, 'r': 7, 'n': 1, 'ag': 8, 'ap': 3, 'ac': 1,
#         'am': 2, 'j': 6, 'ae': 2, 'al': 0, 'ax': 1, 'h': 0, 'y': 3, 'k': 5,
#         'ao': 2, 'ad': 2
#     }

#     is_valid, errors, completion_score = validator.validate_coloring(coloring, confidence=True)
    
#     if is_valid:
#         print("The coloring is valid.")
#         print(f"Completion Score: {completion_score:.2f}%")
#     else:
#         print("The coloring is invalid. Errors found at the following edges:")
#         for u, v in errors:
#             print(f"Edge ({u}, {v}) - both vertices are colored {coloring[u]}.")
#         print(f"Completion Score: {completion_score:.2f}%")