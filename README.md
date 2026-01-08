# SOFAI-Core

## Overview

SOFAI-Core is a domain-agnostic neurosymbolic framework that implements the **"Thinking, Fast and Slow"** paradigm for solving Constraint Satisfaction Problems (CSPs). The framework integrates:

- **System 1 (S1)**: Fast, experience-driven solving using Large Language Models (LLMs)
- **System 2 (S2)**: Slow, deliberate solving using Large Reasoning Models (LRMs) with potentially different model
- **Episodic Memory**: Leverages past solutions to improve future performance
- **Iterative Refinement**: Feedback-driven learning loop

SOFAI-Core provides an abstract framework where different problem domains (graph coloring, planning, etc.) can be easily plugged in.

## Features

- **Domain-Agnostic Architecture**: Clean separation between core logic and domain implementations
- **Modular Design**: Easy to add new domains by implementing the `DomainInterface`
- **LLM Integration**: Uses Ollama for local LLM inference
- **Episodic Memory**: BM25-based retrieval of similar past solutions
- **Adaptive Solving**: Automatically switches to S2 LLM when S1 struggles

## Currently Implemented Domains

### Graph Coloring
- **S1 Solver**: LLM (Mistral-7B or other Ollama models) - fast, iterative
- **S2 Solver**: LRM (Ollama model) - deliberate reasoning
- **Problem Generator**: Erdős–Rényi random graphs
- **Validator**: Constraint checking for adjacent vertices

### Code Debugging
- **S1 Solver**: LLM (Mistral-7B or other Ollama models) - fast, iterative debugging
- **S2 Solver**: LRM (Ollama model) - deliberate debugging
- **Dataset**: DebugBench (4,253 debugging instances, Python3)
- **Validator**: LeetCode API with real test case execution
- **Bug Types**: 17 categories (condition, variable_misuse, function_misuse, etc.)

## Project Structure

```
SOFAI-Core/
├── core/                          # Domain-agnostic framework
│   ├── domain.py                  # Abstract domain interface
│   ├── metacognitive_module.py    # Main metacognitive module
│   ├── llm_solver.py              # LLM wrapper (System 1)
│   ├── episodic_memory.py         # Memory retrieval system
│   └── improvement_trend_evaluator.py  # Progress tracking
│
├── domains/                       # Domain implementations
│   ├── graph_coloring/            # Graph coloring domain
│   │   ├── graph_coloring_domain.py  # Domain implementation
│   │   ├── generator.py           # Problem generator
│   │   ├── validator.py           # Solution validator
│   │   ├── s2_solver.py           # LRM
│   │   ├── prompt_builder.py      # LLM prompt construction
│   │   ├── solution_parser.py     # Parse LLM output
│   │   └── utils.py               # DIMACS parser
│   └── code_debugging/            # Code debugging domain
│       ├── code_debugging_domain.py  # Domain implementation
│       ├── data_loader.py         # Load DebugBench problems
│       ├── validator.py           # LeetCode API wrapper
│       ├── prompt_builder.py      # Build IO_INTENTION_PROMPT
│       ├── solution_parser.py     # Parse <code></code> tags
│       └── utils.py               # Helper functions
│
├── main.py                        # CLI entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Setup Instructions

### 1️⃣ Install Ollama (Required for LLM)

SOFAI-Core uses **Ollama** for local LLM inference.

#### **For macOS & Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### **For Windows:**
Download from: [https://ollama.com/download](https://ollama.com/download)

Verify installation:
```bash
ollama list
```

### 2️⃣ Install Python Dependencies

Ensure **Python 3.10+** is installed, then:

```bash
pip install -r requirements.txt
```

Dependencies include:
- `networkx` - Graph structures
- `matplotlib` - Visualization utilities
- `ollama` - LLM inference
- `rank_bm25` - Episodic memory retrieval

### 3️⃣ Pull the LLM Model

```bash
ollama pull mistral
```

### 4️⃣ (Optional) Setup LeetCode Session for Code Debugging

For the code debugging domain with LeetCode validation:

```bash
# Set your LeetCode session cookie
export LEETCODE_SESSION='your_session_cookie_value'
```

## Usage

### Command-Line Interface

Run SOFAI-Core using the CLI:

```bash
python main.py --domain graph_coloring --nodes 10 --edge-prob 0.6
```

#### Available Arguments

**General:**
- `--domain`: Domain to solve (`graph_coloring`, `code_debugging`)
- `--model`: Ollama model name for S1 (default: `mistral`)
- `--s2-model`: Ollama model name for S2 (default: same as `--model`)
- `--max-iterations`: Maximum S1 refinement iterations (default: `5`)
- `--verbose`: Enable detailed output

**Graph Coloring Specific:**
- `--nodes`: Number of nodes in the graph (default: `10`)
- `--edge-prob`: Edge probability for Erdős–Rényi model (default: `0.5`)

**Code Debugging Specific:**
- `--bug-type`: Specific bug type (e.g., `condition`, `variable_misuse`). Random if not specified.
- `--problem-index`: Specific problem index within bug type file. Random if not specified.

### Examples

#### Graph Coloring

```bash
# Solve a 15-node graph with 60% edge probability
python main.py --domain graph_coloring --nodes 15 --edge-prob 0.6 --verbose

# Use a different LLM model
python main.py --domain graph_coloring --model llama2 --nodes 10
```

#### Code Debugging

```bash
# Solve code debugging problem (random bug type)
python main.py --domain code_debugging

# Solve specific bug type with verbose output
python main.py --domain code_debugging --bug-type condition --verbose

# Use different models for S1 and S2
python main.py --domain code_debugging --model mistral --s2-model llama2
```

## Adding New Domains

To add a new domain (e.g., planning), implement the `DomainInterface`:

1. Create `domains/your_domain/your_domain.py`
2. Implement all abstract methods:
   - `generate_problem()` - Create problem instances
   - `validate_solution()` - Check solution correctness
   - `build_prompt()` - Construct LLM prompts
   - `parse_solution()` - Parse LLM responses
   - `run_s2_solver()` - Exact solver implementation
   - `get_problem_representation()` - For episodic memory
   - `format_solution_for_memory()` - Store solutions
   - `format_feedback()` - Format validation errors

3. Register in `main.py`

See `domains/graph_coloring/graph_coloring_domain.py` for a complete example.

## How It Works

1. **Problem Generation**: A domain-specific problem is generated
2. **Initial Prompt**: Episodic memory retrieves similar past problems
3. **S1 Iteration Loop** (up to max_iterations):
   - LLM proposes a solution
   - Solution is validated
   - If valid: Store in memory and return
   - If invalid: Provide feedback and retry
4. **S2 Fallback**: If S1 fails or shows no improvement, invoke exact solver
5. **Memory Update**: Successful solutions added to episodic memory
