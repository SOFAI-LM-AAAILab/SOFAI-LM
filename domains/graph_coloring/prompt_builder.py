def prompt_generator(graph_content, min_colors, additional_examples=None):
    """
    Generates a prompt for graph coloring with optional examples from episodic memory.
    
    Args:
        graph_content (str): The graph details in a specific format.
        min_colors (int): The maximum number of distinct colors that can be used.
        additional_examples (list of str, optional): Additional examples of colorings, if any.
    
    Returns:
        str: A formatted prompt string for the problem description.
    """
    example_section = ""
    if additional_examples:
        example_section = "\nPrevious Examples:\n"
        for example in additional_examples:
            example_section += f"{example}\n"

    return f"""
    Problem Description:
    You are given an undirected graph with {min_colors} colors available. Your task is to assign a color to each vertex such that no two adjacent vertices share the same color.

    Graph Representation:
    - Number of vertices and edges: `p edge <number_of_vertices> <number_of_edges>`.
    - Edges between vertices are listed as follows:
    {graph_content}

    Objective:
    Assign a unique color to each vertex, ensuring that no two vertices connected by an edge have the same color. Use no more than {min_colors} distinct colors. Provide the color assignments for each vertex in the format:
    (Vertex Color)
    
    Example Format:
    (a 1)
    (b 2)
    (c 1)

    {example_section}Please provide the color assignment directly below:
    """

# # Example usage:
# if __name__ == "__main__":
#     graph_content = """
#     p edge 10 15
#     e a b
#     e a c
#     e a e
#     e a g
#     e a i
#     e b g
#     e b h
#     e b j
#     e c f
#     e c h
#     e c j
#     e d f
#     e d h
#     e g j
#     e h i
#     """
#     min_colors = 3
#     print(preprocess_graph_coloring_input(graph_content, min_colors))

# # Example usage:
# if __name__ == "__main__":
#     graph_content = """
#     Vertices: A, B, C, D
#     Edges: (A-B), (B-C), (C-D), (D-A)
#     """
#     min_colors = 3
#     print(preprocess_graph_coloring_input(graph_content, min_colors))

# def preprocess_graph_coloring_input(graph_content, min_colors):
#     return f"""
#     Graph Coloring Problem
    
#     Problem Description:
#     You are provided with an undirected graph represented by vertices and edges. Each vertex should be colored in such a way that no two adjacent vertices share the same color. The goal is to use at most {min_colors} colors.

#     Graph Details:
#     {graph_content}

#     Instructions:
#     Provide a valid coloring for the graph using no more than {min_colors} colors. Ensure that no two adjacent vertices share the same color.

#     Output Format:
#     Please list the color assignments for each vertex as follows:
#     (Vertex Color)
#     Example: (A 1), (B 2), (C 1)

#     Note: Use the vertex names from the graph content provided.
#     """

# # def preprocess_n_queens_input(board_size):
# #     user_input = f"""
# #     N-Queens Problem

# #     Problem Description:
# #     Place {board_size} queens on a {board_size}x{board_size} chessboard so that no two queens threaten each other.

# #     Instructions:
# #     Provide the positions of the queens on the board. No two queens should be able to attack each other horizontally, vertically, or diagonally.

# #     Output Format:
# #     List the positions of the queens, with each position represented by the row number followed by the column number, starting from the top-left of the board.
# #     Example for a 4x4 board: (1, 2), (2, 4), (3, 1), (4, 3)

# #     Note: Row and column indices should start from 1.
# #     """
# #     return user_input

# # Example usage:
# if __name__ == "__main__":
#     graph_content = "Vertices: A, B, C, D; Edges: (A-B), (B-C), (C-D), (D-A)"
#     min_colors = 3
#     print(preprocess_graph_coloring_input(graph_content, min_colors))

#     # board_size = 8
#     # print(preprocess_n_queens_input(board_size))