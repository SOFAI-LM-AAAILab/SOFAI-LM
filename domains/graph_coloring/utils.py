"""
Domain-specific utilities for graph coloring.

This module contains helper functions for parsing DIMACS graph format.
"""

import re


def parse_graph(file_path):
    """
    Parse graph content from a file in DIMACS format.

    Args:
        file_path (str): The file path of the graph data in DIMACS format.

    Returns:
        tuple: (graph_description, num_edges, num_vertices, edges, vertices)
            - graph_description (str): String representation suitable for prompts
            - num_edges (str): Number of edges
            - num_vertices (str): Number of vertices
            - edges (list): List of edges as strings "v1 v2"
            - vertices (list): List of unique vertex labels
    """
    edges = []
    num_vertices = 0
    num_edges = 0
    vertices = list()

    # Open and read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) > 0:
            if parts[0] == 'p':
                _, _, num_vertices, num_edges = parts
            elif parts[0] == 'e' and len(parts) == 3:
                _, v1, v2 = parts
                edges.append(f"{v1} {v2}")
                vertices.append(v1)
                vertices.append(v2)

    vertices = list(set(vertices))

    # Preparing the string to be added to the prompt
    graph_description = f"p edge {num_vertices} {num_edges}\n" + "\n".join(f"e {edge}" for edge in edges)
    return graph_description, num_edges, num_vertices, edges, vertices
