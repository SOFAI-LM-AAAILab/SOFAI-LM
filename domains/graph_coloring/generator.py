import networkx as nx
import os
from itertools import product
import pickle
from string import ascii_lowercase

class GraphColoringGenerator:
    def __init__(self, output_dir="domains/graph_coloring/problems"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def label_generator(self, n):
        """Generates labels for nodes based on the number of vertices."""
        length = 1
        while True:
            for item in product(ascii_lowercase, repeat=length):
                yield "".join(item)
                n -= 1
                if n == 0:
                    return
            length += 1

    def generate_graph(self, n_vertices, p):
        """Generates a planar Erdős–Rényi graph with labeled nodes."""
        # while True:
        # for i in range(n_graphs):
        labels = list(self.label_generator(n_vertices))
        G = nx.erdos_renyi_graph(n_vertices, p)
        relabel_mapping = {i: labels[i] for i in range(n_vertices)}
        G = nx.relabel_nodes(G, relabel_mapping)
            # if nx.check_planarity(G)[0]:
        return G

    def chromatic_number(self, G):
        """Calculates the chromatic number using a greedy coloring algorithm."""
        coloring = nx.coloring.greedy_color(G, strategy="largest_first")
        return max(coloring.values()) + 1  # Colors start from 0

    # def write_dimacs(self, G, file_name, chromatic_num):
    def write_dimacs(self, G, file_name):
        """Exports graph data in DIMACS format."""
        with open(file_name, 'w') as f:
            # f.write(f"c Chromatic Number: {chromatic_num}\n")
            f.write(f"p edge {len(G.nodes)} {len(G.edges)}\n")
            for u, v in G.edges():
                f.write(f"e {u} {v}\n")

    def generate_and_save_graphs(self, n_graphs, n_vertices_list, p):
        """Generates multiple graphs and saves them to files."""
        chromatic_nums = dict()
        for n_vertices in n_vertices_list:
            for i in range(n_graphs):
                G = self.generate_graph(n_vertices, p)
                # save this as pickle file 
                file_name = f"{self.output_dir}/graph_n{n_vertices}_graph{i}.pickle"
                pickle.dump(G, open(file_name, "wb"))
                chromatic_num = self.chromatic_number(G)
                file_name = f"{self.output_dir}/graph_n{n_vertices}_graph{i}.col"
                # self.write_dimacs(G, file_name, chromatic_num)
                self.write_dimacs(G, file_name)
                chromatic_nums[file_name] = chromatic_num
                # print(f"Generated graph with {n_vertices} vertices, chromatic number {chromatic_num}, saved to {file_name}")

        return chromatic_nums
# Example usage:
if __name__ == "__main__":
    generator = GraphColoringGenerator()
    generator.generate_and_save_graphs(100, [5,6,7,8,9,10,15,20,25,30,35,40,45,50], 0.4)
