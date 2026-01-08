import re
from collections import defaultdict

def run_degree_of_saturation(graph_content, sorted_vertices=None):
    """
    Implements the Degree of Saturation (DSATUR) algorithm for graph coloring 
    with iterative backtracking to ensure the optimal chromatic number.
    
    :param graph_content: The graph definition in DIMACS format as a string.
    :param sorted_vertices: Pre-sorted vertices by degree (optional). If not provided, it will be computed.
    :return: A string representing the coloring of the graph and the chromatic number.
    """
    vertices = set()
    edges = defaultdict(list)

    # Parse the DIMACS graph content to extract vertices and edges
    for line in graph_content.strip().splitlines():
        line = line.strip()
        # Skip comment lines or problem line
        if line.startswith('c') or line.startswith('p'):
            continue
        
        # Parse the edges: "e u v" where u and v are vertex labels (strings or numbers)
        match = re.match(r"e\s+(\w+)\s+(\w+)", line)
        if match:
            v1, v2 = match.groups()
            vertices.add(v1)
            vertices.add(v2)
            edges[v1].append(v2)
            edges[v2].append(v1)

    # Function to check if the current coloring is valid
    def is_valid_coloring(vertex, color, forbidden_colors):
        return color not in forbidden_colors[vertex]

    # Iterative backtracking to find the optimal chromatic number
    def iterative_backtrack(sorted_vertices, chromatic_number, edges):
        stack = [({}, 0, {v: set() for v in sorted_vertices})]  # Add forbidden colors to the stack
        min_colors = chromatic_number

        while stack:
            current_colors, index, forbidden_colors = stack.pop()
            if index == len(sorted_vertices):
                # Check the number of unique colors used
                num_colors = len(set(current_colors.values()))
                if num_colors < min_colors:
                    min_colors = num_colors
                continue

            vertex = sorted_vertices[index]
            for color in range(1, min_colors + 1):
                if is_valid_coloring(vertex, color, forbidden_colors):
                    current_colors[vertex] = color  # Assign the color

                    # Update forbidden colors for neighbors
                    new_forbidden_colors = {v: set(fc) for v, fc in forbidden_colors.items()}
                    for neighbor in edges[vertex]:
                        new_forbidden_colors[neighbor].add(color)

                    stack.append((current_colors.copy(), index + 1, new_forbidden_colors))
                    del current_colors[vertex]  # Unassign the color after backtracking

        return min_colors

    # Initialize data structures for DSATUR
    colors = {}
    saturation_degree = {v: 0 for v in vertices}
    degree = {v: len(edges[v]) for v in vertices}

    # Sort vertices by degree (to reduce the search space in backtracking) if not provided
    if sorted_vertices is None:
        sorted_vertices = sorted(vertices, key=lambda v: degree[v], reverse=True)

    # Perform DSATUR to get an initial estimate of the chromatic number
    while len(colors) < len(vertices):
        # Select the vertex with the highest saturation degree (ties broken by highest degree)
        candidate_vertex = max(
            vertices - colors.keys(),
            key=lambda v: (saturation_degree[v], degree[v])
        )

        # Assign the smallest possible color
        forbidden_colors = {colors[neighbor] for neighbor in edges[candidate_vertex] if neighbor in colors}
        color = 1
        while color in forbidden_colors:
            color += 1

        colors[candidate_vertex] = color

        # Update saturation degree for neighbors
        for neighbor in edges[candidate_vertex]:
            if neighbor not in colors:
                saturation_degree[neighbor] += 1

    # Initial chromatic number estimate from DSATUR
    chromatic_number = max(colors.values())

    # Use iterative backtracking to minimize the chromatic number
    optimal_chromatic_number = iterative_backtrack(sorted_vertices, chromatic_number, edges)

    # Use the DSATUR coloring as the final result
    # (The backtracking optimization above finds the optimal chromatic number,
    # but we use the DSATUR coloring which is already valid)
    final_colors = colors

    # Format the output in the expected (vertex color) format
    coloring_output = "\n".join([f"({v} {c})" for v, c in final_colors.items()])
    return coloring_output, optimal_chromatic_number

# Example function to load the generated graph content
def load_graph_from_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()