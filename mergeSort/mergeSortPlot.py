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
    time_keywords = ['SEQUENTIAL', 'OPENMP', 'MPI', 'HYBRID', 'Execution', 'MERGE']
    
    for line in output.split('\n'):
        # Check for time information
        if any(keyword in line for keyword in time_keywords):
            if "time:" in line:
                time_str = line.split('time:')[1].strip().split()[0]
            else:
                parts = line.split()
                for part in parts:
                    try:
                        time = float(part)
                        break
                    except ValueError:
                        continue
                continue
            
            try:
                time = float(time_str)
            except ValueError:
                continue
        
        # Check for array elements (numbers only)
        elif line.strip() and line[0].isdigit():
            try:
                sorted_array.extend(map(int, line.strip().split()))
            except ValueError:
                continue
    
    return sorted_array, time

def run_sequential(input_file):
    """Run sequential merge sort"""
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(["./merge_sort"], stdin=f, stdout=subprocess.PIPE, text=True)
        output = proc.communicate()[0]
    return parse_output(output)

def run_openmp(input_file, threads=4):
    """Run OpenMP merge sort"""
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(["./merge_sort_openmp"], stdin=f, stdout=subprocess.PIPE, 
                              text=True, env=env)
        output = proc.communicate()[0]
    return parse_output(output)

def run_mpi(input_file, processes=4):
    """Run MPI merge sort"""
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(["mpirun", "-n", str(processes), "./merge_sort_mpi"], 
                              stdin=f, stdout=subprocess.PIPE, text=True)
        output = proc.communicate()[0]
    return parse_output(output)

def run_hybrid(input_file, mpi_processes=2, omp_threads=2):
    """Run Hybrid (MPI+OpenMP) merge sort"""
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(omp_threads)
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(
            ["mpirun", "-n", str(mpi_processes), "./hybrid_merge_sort"],
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
    for impl, data in results.items():
        if ref_array is None:
            ref_array = data['sorted_array']
        else:
            if data['sorted_array'] != ref_array:
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
    plt.title('Merge Sort Performance Comparison')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.6f}',
                 ha='center', va='bottom')
    
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('merge_sort_performance.png')
    plt.show()

def print_full_array(arr, max_display=50):
    """Print full array with truncation indication if too large"""
    if len(arr) <= max_display:
        print(arr)
    else:
        print(f"[{', '.join(map(str, arr[:max_display//2]))}, ..., {', '.join(map(str, arr[-max_display//2:]))}]")
        print(f"(Showing first and last {max_display//2} elements of {len(arr)} total elements)")

def main():
    # Compile all programs first
    subprocess.run(["gcc", "-o", "merge_sort", "merge_sort.c"])
    subprocess.run(["gcc", "-fopenmp", "-o", "merge_sort_openmp", "merge_sort_openmp.c"])
    subprocess.run(["mpicc", "-o", "merge_sort_mpi", "merge_sort_mpi.c"])
    subprocess.run(["mpicc", "-fopenmp", "-o", "hybrid_merge_sort", "hybrid_merge_sort.c"])
    
    # Get user input once
    n, elements = get_user_input()
    input_file = save_input_to_file(n, elements)
    
    # Run all implementations with the same input
    results = {
        "Sequential": {},
        "OpenMP (4 threads)": {},
        "MPI (4 processes)": {},
        "Hybrid (2 MPI × 2 OMP)": {}
    }
    
    # Run implementations
    sorted_array, time = run_sequential(input_file)
    results["Sequential"]['sorted_array'] = sorted_array
    results["Sequential"]['time'] = time
    
    sorted_array, time = run_openmp(input_file, 4)
    results["OpenMP (4 threads)"]['sorted_array'] = sorted_array
    results["OpenMP (4 threads)"]['time'] = time
    
    sorted_array, time = run_mpi(input_file, 4)
    results["MPI (4 processes)"]['sorted_array'] = sorted_array
    results["MPI (4 processes)"]['time'] = time
    
    sorted_array, time = run_hybrid(input_file, 2, 2)
    results["Hybrid (2 MPI × 2 OMP)"]['sorted_array'] = sorted_array
    results["Hybrid (2 MPI × 2 OMP)"]['time'] = time
    
    # Verify all implementations produced the same sorted array
    if verify_sorted_arrays(results):
        print("\nAll implementations produced identical sorted arrays")
    else:
        print("\nWarning: Sorting implementations produced different results!")
    
    # Print complete sorted array
    print("\nComplete sorted array from Sequential implementation:")
    print_full_array(results["Sequential"]['sorted_array'])
    
    # Print performance results
    print("\nPerformance Results:")
    for impl, data in results.items():
        print(f"{impl}: {data['time']:.6f} seconds")
    
    # Plot results
    plot_results(results)

if __name__ == "__main__":
    main()