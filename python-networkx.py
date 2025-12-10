import networkx as nx
import re
import time
import tracemalloc
import subprocess
import os
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import generate_graph



def parse_cpp_output(filename):
    edges_coloring = {}
    num_colors = 0

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.search(r'Edge\s+(\d+)\s*-\s*(\d+)\s*:\s*Color\s+(\d+)', line)
            if match:
                u, v, color = int(match.group(1)), int(match.group(2)), int(match.group(3))
                edge = (min(u, v), max(u, v))
                edges_coloring[edge] = color - 1
                num_colors = max(num_colors, color)

    return {
        'edges_coloring': edges_coloring,
        'num_colors': num_colors
    }

def check_validity(parsed_data, graph):
    edges_coloring = parsed_data['edges_coloring']

    for node in graph.nodes():
        incident_colors = set()
        for neighbor in graph.neighbors(node):
            edge = (min(node, neighbor), max(node, neighbor))
            if edge not in edges_coloring:
                return False, f"Edge {edge} not found"

            color = edges_coloring[edge]
            if color in incident_colors:
                return False, f"Node {node}: two edges with same color {color}"
            incident_colors.add(color)

    return True, "Valid coloring"

    return True, "✓ Розфарбування валідне!"

def benchmark_networkx(input_graph_file: str):
    start_time = time.time()
    tracemalloc.start()

    G = nx.read_edgelist(input_graph_file, nodetype=int)

    max_degree = max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0

    theoretical_minimum = max_degree

    line_graph = nx.line_graph(G)
    edge_coloring: dict = nx.greedy_color(line_graph)

    colors_used = max(edge_coloring.values()) + 1 if edge_coloring else 0

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_time = time.time() - start_time

    return {
        'graph': G,
        'colors_used': colors_used,
        'theoretical_minimum': theoretical_minimum,
        'edge_coloring': edge_coloring,
        'time': elapsed_time,
        'memory_mb': peak / 1024 / 1024
    }


def compile_cpp():
    result = subprocess.run(['g++', '-O2', 'main.cpp', '-o', 'main'],
                          capture_output=True, text=True)
    if result.returncode != 0:
        return False
    return True


def run_cpp(input_file):
    start_time = time.time()
    tracemalloc.start()

    result = subprocess.run(['./main'], capture_output=True, text=True)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_time = time.time() - start_time

    if result.returncode != 0:
        return None

    return {
        'time': elapsed_time,
        'memory_mb': peak / 1024 / 1024,
        'output': result.stdout
    }


def benchmark_comparison(input_file, cpp_output_file="output.txt", output_report="benchmark_report.txt"):
    with open(output_report, 'a') as report:
        report.write("\n" + "="*60 + "\n")
        report.write("BENCHMARK: C++ vs NetworkX\n")
        report.write("="*60 + "\n")

        if not compile_cpp():
            report.write("FAILED: C++ compilation error\n")
            return None

        cpp_result = run_cpp(input_file)
        if not cpp_result:
            report.write("FAILED: C++ execution error\n")
            return None

        nx_result = benchmark_networkx(input_file)

        report.write("\nRESULTS:\n")
        report.write("-" * 60 + "\n")

        cpp_data = parse_cpp_output(cpp_output_file)
        report.write(f"C++:\n")
        report.write(f"  Colors used: {cpp_data['num_colors']}\n")
        report.write(f"  Time: {cpp_result['time']:.4f} sec\n")
        report.write(f"  Memory: {cpp_result['memory_mb']:.2f} MB\n")

        report.write(f"\nNetworkX:\n")
        report.write(f"  Colors used: {nx_result['colors_used']}\n")
        report.write(f"  Theoretical minimum: {nx_result['theoretical_minimum']}\n")
        report.write(f"  Time: {nx_result['time']:.4f} sec\n")
        report.write(f"  Memory: {nx_result['memory_mb']:.2f} MB\n")

        G = nx.read_edgelist(input_file, nodetype=int)
        is_valid, msg = check_validity(cpp_data, G)
        report.write(f"\nValidity C++: {msg}\n")

        speedup = cpp_result['time'] / nx_result['time']
        report.write(f"\nSpeedup C++ over NetworkX: {speedup:.2f}x\n")

        report.write("="*60 + "\n")

        return {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'cpp_time': cpp_result['time'],
            'cpp_memory': cpp_result['memory_mb'],
            'cpp_colors': cpp_data['num_colors'],
            'nx_time': nx_result['time'],
            'nx_memory': nx_result['memory_mb'],
            'nx_colors': nx_result['colors_used'],
            'speedup': speedup
        }


def plot_results(results, report_file):
    edges = [r['edges'] for r in results]
    cpp_times = [r['cpp_time'] for r in results]
    nx_times = [r['nx_time'] for r in results]
    cpp_memory = [r['cpp_memory'] for r in results]
    nx_memory = [r['nx_memory'] for r in results]
    speedups = [r['speedup'] for r in results]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    ax1.plot(edges, cpp_times, 'o-', label='C++', linewidth=2, markersize=8)
    ax1.plot(edges, nx_times, 's-', label='NetworkX', linewidth=2, markersize=8)
    ax1.set_xlabel('Number of Edges')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Execution Time Comparison')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(edges, cpp_memory, 'o-', label='C++', linewidth=2, markersize=8)
    ax2.plot(edges, nx_memory, 's-', label='NetworkX', linewidth=2, markersize=8)
    ax2.set_xlabel('Number of Edges')
    ax2.set_ylabel('Memory (MB)')
    ax2.set_title('Memory Usage Comparison')
    ax2.set_xscale('log')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3.plot(edges, speedups, 'ro-', linewidth=2, markersize=8)
    ax3.axhline(y=1, color='k', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Number of Edges')
    ax3.set_ylabel('Speedup (x)')
    ax3.set_title('C++ Speedup over NetworkX')
    ax3.set_xscale('log')
    ax3.grid(True, alpha=0.3)

    colors_data = [[r['cpp_colors'], r['nx_colors']] for r in results]
    x = range(len(edges))
    width = 0.35
    ax4.bar([i - width/2 for i in x], [c[0] for c in colors_data], width, label='C++')
    ax4.bar([i + width/2 for i in x], [c[1] for c in colors_data], width, label='NetworkX')
    ax4.set_xlabel('Test Size')
    ax4.set_ylabel('Number of Colors')
    ax4.set_title('Coloring Quality Comparison')
    ax4.set_xticks(x)
    ax4.set_xticklabels([str(e) for e in edges])
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('benchmark_results.png', dpi=300, bbox_inches='tight')

    with open(report_file, 'a') as f:
        f.write("\nGraphs saved as 'benchmark_results.png'\n")


if __name__ == "__main__":
    if not os.path.exists("main.cpp"):
        print("ERROR: main.cpp not found")
        exit(1)

    test_configs = [
        (5, 10),
        (10, 100),
        (100, 100),
        (32, 1000),
        (1000, 1000)
    ]
    results = []
    report_file = "benchmark_report.txt"

    with open(report_file, 'w') as f:
        f.write("BENCHMARK REPORT\n")
        f.write("Using bipartite graph generator\n")
        f.write("="*60 + "\n\n")

    for n, m in test_configs:
        test_file = "test.txt"

        print(f"Generating bipartite graph: {n} nodes in part 1, {m} nodes in part 2...")
        generate_graph(n, m, "test")

        print(f"Running benchmark for {n}x{m} bipartite graph...")
        result = benchmark_comparison(test_file, "output.txt", report_file)
        if result:
            results.append(result)
            print(f"  Completed: {result['edges']} edges\n")

    with open(report_file, 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("SUMMARY\n")
        f.write("="*60 + "\n\n")
        for r in results:
            f.write(f"Nodes: {r['nodes']}, Edges: {r['edges']}\n")
            f.write(f"  C++: {r['cpp_time']:.4f}s, {r['cpp_memory']:.2f}MB, Colors: {r['cpp_colors']}\n")
            f.write(f"  NetworkX: {r['nx_time']:.4f}s, {r['nx_memory']:.2f}MB, Colors: {r['nx_colors']}\n")
            f.write(f"  Speedup: {r['speedup']:.2f}x\n\n")

    plot_results(results, report_file)

    plot_results(results, report_file)

