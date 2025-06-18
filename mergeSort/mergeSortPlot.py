import subprocess
import matplotlib.pyplot as plt
import os

# --- Get user input for sorting ---
def get_user_input():
    n = int(input("Enter number of elements: "))
    print(f"Enter {n} integers (space separated):")
    elements = list(map(int, input().split()))
    return n, elements

# --- Save input to file ---
def save_input_to_file(n, elements, filename="input.txt"):
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        f.write("\n".join(map(str, elements)))
    return filename

# --- Parse output to extract sorted array and execution time ---
def parse_output(output):
    sorted_array = []
    time = None
    time_keywords = ['SEQUENTIAL', 'OPENMP', 'MPI', 'HYBRID', 'Execution', 'MERGE']

    for line in output.split('\n'):
        if any(keyword in line.upper() for keyword in time_keywords):
            for token in line.split():
                try:
                    time = float(token)
                    break
                except ValueError:
                    continue
        elif line.strip() and line[0].isdigit():
            try:
                sorted_array.extend(map(int, line.strip().split()))
            except ValueError:
                continue

    if time is None:
        print("[Warning] Could not parse execution time from output!")

    return sorted_array, time

# --- Run a compiled C/C++ program with input file ---
def run_program(command, input_file, env=None):
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(command, stdin=f, stdout=subprocess.PIPE, text=True, env=env)
        output = proc.communicate()[0]
    return parse_output(output)

# --- Wrappers for different implementations ---
def run_sequential(input_file):
    return run_program(["./merge_sort"], input_file)

def run_openmp(input_file, threads=4):
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)
    return run_program(["./merge_sort_openmp"], input_file, env)

def run_mpi(input_file, processes=4):
    return run_program(["mpirun", "-n", str(processes), "./merge_sort_mpi"], input_file)

def run_hybrid(input_file, mpi_processes=2, omp_threads=2):
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(omp_threads)
    return run_program(["mpirun", "-n", str(mpi_processes), "./hybrid_merge_sort"], input_file, env)

# --- Compare output arrays ---
def verify_sorted_arrays(results):
    ref = None
    for impl, data in results.items():
        if ref is None:
            ref = data['sorted_array']
        elif data['sorted_array'] != ref:
            print(f"Warning: {impl} produced different sorted array!")
            return False
    return True

# --- Plot bar chart for execution times ---
def plot_results(results):
    impls = list(results.keys())
    times = [data['time'] if data['time'] is not None else 0 for data in results.values()]
    colors = ['blue', 'green', 'red', 'purple']

    plt.figure(figsize=(12, 6))
    bars = plt.bar(impls, times, color=colors[:len(impls)])

    plt.xlabel('Implementation')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Merge Sort Performance Comparison')

    for bar, data in zip(bars, results.values()):
        time = data['time']
        label = f'{time:.6f}' if time is not None else 'N/A'
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), label, ha='center', va='bottom')

    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('merge_sort_performance.png')
    plt.show()

# --- Display sorted array (truncated if long) ---
def print_full_array(arr, max_display=50):
    if len(arr) <= max_display:
        print(arr)
    else:
        half = max_display // 2
        print(f"[{', '.join(map(str, arr[:half]))}, ..., {', '.join(map(str, arr[-half:]))}]")
        print(f"(Showing first and last {half} elements of {len(arr)} total)")

# --- Main program ---
def main():
    # Compile sorting implementations
    subprocess.run(["gcc", "-o", "merge_sort", "merge_sort.c"])
    subprocess.run(["gcc", "-fopenmp", "-o", "merge_sort_openmp", "merge_sort_openmp.c"])
    subprocess.run(["mpicc", "-o", "merge_sort_mpi", "merge_sort_mpi.c"])
    subprocess.run(["mpicc", "-fopenmp", "-o", "hybrid_merge_sort", "hybrid_merge_sort.c"])

    # Get user input
    n, elements = get_user_input()
    input_file = save_input_to_file(n, elements)

    # Run all implementations and collect results
    results = {
        "Sequential": {},
        "OpenMP (4 threads)": {},
        "MPI (4 processes)": {},
        "Hybrid (2 MPI × 2 OMP)": {}
    }

    results["Sequential"]['sorted_array'], results["Sequential"]['time'] = run_sequential(input_file)
    results["OpenMP (4 threads)"]['sorted_array'], results["OpenMP (4 threads)"]['time'] = run_openmp(input_file, 4)
    results["MPI (4 processes)"]['sorted_array'], results["MPI (4 processes)"]['time'] = run_mpi(input_file, 4)
    results["Hybrid (2 MPI × 2 OMP)"]['sorted_array'], results["Hybrid (2 MPI × 2 OMP)"]['time'] = run_hybrid(input_file, 2, 2)

    # Verify sorting correctness
    if verify_sorted_arrays(results):
        print("\nAll implementations produced identical sorted arrays")
    else:
        print("\nWarning: Sorting implementations produced different results!")

    # Display final sorted array
    print("\nComplete sorted array from Sequential implementation:")
    print_full_array(results["Sequential"]['sorted_array'])

    # Display performance results
    print("\nPerformance Results:")
    for impl, data in results.items():
        if data['time'] is not None:
            print(f"{impl}: {data['time']:.6f} seconds")
        else:
            print(f"{impl}: Execution time not available")

    # Plot chart
    plot_results(results)

if __name__ == "__main__":
    main()
