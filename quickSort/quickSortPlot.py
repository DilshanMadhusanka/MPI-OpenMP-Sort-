import subprocess
import matplotlib.pyplot as plt
import os
from collections import defaultdict

def get_user_input():
    """Get input size and elements from user"""
    n = int(input("Enter number of elements: "))
    print(f"Enter {n} integers (space separated):")
    elements = list(map(int, input().split()))
    return n, elements

def save_input_to_file(n, elements, filename="input.txt"):
    """Save user input to a file"""
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        f.write("\n".join(map(str, elements)))
    return filename

def parse_output(output):
    """Parse the output to get sorted array and execution time"""
    sorted_array = []
    time = None
    for line in output.split('\n'):
        if line.startswith(('Execution', 'HYBRID', 'Hybrid')):
            if "time:" in line:
                time = float(line.split(':')[1].strip().split()[0])
            elif line.startswith(('HYBRID', 'Hybrid')):
                time = float(line.split()[-2])
        elif line.strip() and line[0].isdigit():  # Only process lines starting with digits
            try:
                sorted_array.extend(map(int, line.strip().split()))
            except ValueError:
                continue
    return sorted_array, time

def run_sequential(input_file):
    """Run sequential quick sort"""
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(["./quick_sort"], stdin=f, stdout=subprocess.PIPE, text=True)
        output = proc.communicate()[0]
    return parse_output(output)

def run_openmp(input_file, threads=4):
    """Run OpenMP quick sort"""
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(["./quick_sort_openmp"], stdin=f, stdout=subprocess.PIPE, 
                              text=True, env=env)
        output = proc.communicate()[0]
    return parse_output(output)

def run_mpi(input_file, processes=4):
    """Run MPI quick sort"""
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(["mpirun", "-n", str(processes), "./quick_sort_mpi"], 
                              stdin=f, stdout=subprocess.PIPE, text=True)
        output = proc.communicate()[0]
    return parse_output(output)

def run_hybrid(input_file, mpi_processes=2, omp_threads=2):
    """Run Hybrid (MPI+OpenMP) quick sort"""
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(omp_threads)
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(
            ["mpirun", "-n", str(mpi_processes), "./hybrid_quick_sort"],
            stdin=f,
            stdout=subprocess.PIPE,
            text=True,
            env=env
        )
        output = proc.communicate()[0]
    return parse_output(output)

def verify_sorted_arrays(results):
    """Verify that all implementations produced the same sorted array"""
    ref_array = None
    for impl in results:
        if ref_array is None:
            ref_array = results[impl]['sorted_array']
        else:
            if results[impl]['sorted_array'] != ref_array:
                print(f"Warning: {impl} produced different sorted array!")
                return False
    return True

def plot_results(results):
    """Plot the performance comparison results"""
    implementations = list(results.keys())
    execution_times = [data['time'] for data in results.values()]
    
    colors = ['blue', 'green', 'red', 'purple']
    plt.figure(figsize=(12, 6))
    bars = plt.bar(implementations, execution_times, color=colors[:len(implementations)])
    
    plt.xlabel('Implementation')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Quick Sort Performance Comparison')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.6f}',
                 ha='center', va='bottom')
    
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('quick_sort_performance.png')
    plt.show()

def print_full_array(arr, max_display=50):
    """Print full array with truncation indication if too large"""
    if len(arr) <= max_display:
        print(arr)
    else:
        print(f"[{', '.join(map(str, arr[:max_display//2]))}, ..., {', '.join(map(str, arr[-max_display//2:]))}]")
        print(f"(Showing first and last {max_display//2} elements of {len(arr)} total elements)")

def compile_quick_sort_programs():
    """Compile all quick sort programs"""
    # Compile quick sort programs
    subprocess.run(["gcc", "-o", "quick_sort", "quick_sort.c"])
    subprocess.run(["gcc", "-fopenmp", "-o", "quick_sort_openmp", "quick_sort_openmp.c"])
    subprocess.run(["mpicc", "-o", "quick_sort_mpi", "quick_sort_mpi.c"])
    # Compile hybrid version
    subprocess.run(["mpicc", "-fopenmp", "-o", "hybrid_quick_sort", "hybrid_quick_sort.c"])

def main():
    # Compile all quick sort programs first
    compile_quick_sort_programs()
    
    # Get user input once
    n, elements = get_user_input()
    input_file = save_input_to_file(n, elements)
    
    # Run all quick sort implementations with the same input
    results = {
        "Sequential": {},
        "OpenMP (4 threads)": {},
        "MPI (4 processes)": {},
        "Hybrid (2 MPI × 2 OMP)": {}
    }
    
    # Run sequential quick sort
    sorted_array, time = run_sequential(input_file)
    results["Sequential"]['sorted_array'] = sorted_array
    results["Sequential"]['time'] = time
    
    # Run OpenMP quick sort
    sorted_array, time = run_openmp(input_file, 4)
    results["OpenMP (4 threads)"]['sorted_array'] = sorted_array
    results["OpenMP (4 threads)"]['time'] = time
    
    # Run MPI quick sort
    sorted_array, time = run_mpi(input_file, 4)
    results["MPI (4 processes)"]['sorted_array'] = sorted_array
    results["MPI (4 processes)"]['time'] = time
    
    # Run Hybrid quick sort (2 MPI processes × 2 OpenMP threads each)
    sorted_array, time = run_hybrid(input_file, 2, 2)
    results["Hybrid (2 MPI × 2 OMP)"]['sorted_array'] = sorted_array
    results["Hybrid (2 MPI × 2 OMP)"]['time'] = time
    
    # Verify all implementations produced the same sorted array
    if verify_sorted_arrays(results):
        print("\nAll quick sort implementations produced identical sorted arrays")
    else:
        print("\nWarning: Quick sort implementations produced different results!")
    
    # Print complete sorted array from sequential implementation
    print("\nComplete sorted array from Sequential Quick Sort:")
    print_full_array(results["Sequential"]['sorted_array'])
    
    # Print performance results
    print("\nQuick Sort Performance Results:")
    for impl, data in results.items():
        print(f"{impl}: {data['time']:.6f} seconds")
    
    # Plot results
    plot_results(results)

if __name__ == "__main__":
    main()