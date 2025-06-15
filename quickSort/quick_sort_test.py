import subprocess
import matplotlib.pyplot as plt
import os
import random
import argparse

def generate_random_array(size, min_val=0, max_val=1000000):
    """Generate random array for testing"""
    return [random.randint(min_val, max_val) for _ in range(size)]

def save_input_to_file(n, elements, filename="input.txt"):
    """Save generated array to a file"""
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

def run_quick_sort(input_file, impl_type, threads=4, mpi_processes=2, omp_threads=2):
    """Run quick sort implementation"""
    if impl_type == "sequential":
        cmd = ["./quick_sort"]
        env = None
    elif impl_type == "openmp":
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = str(threads)
        cmd = ["./quick_sort_openmp"]
    elif impl_type == "mpi":
        env = None
        cmd = ["mpirun", "-n", str(threads), "./quick_sort_mpi"]
    elif impl_type == "hybrid":
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = str(omp_threads)
        cmd = ["mpirun", "-n", str(mpi_processes), "./hybrid_quick_sort"]
    
    with open(input_file, 'r') as f:
        proc = subprocess.Popen(cmd, stdin=f, stdout=subprocess.PIPE, text=True, env=env)
        output = proc.communicate()[0]
    return parse_output(output)

def compile_programs():
    """Compile all quick sort programs"""
    subprocess.run(["gcc", "-o", "quick_sort", "quick_sort.c"])
    subprocess.run(["gcc", "-fopenmp", "-o", "quick_sort_openmp", "quick_sort_openmp.c"])
    subprocess.run(["mpicc", "-o", "quick_sort_mpi", "quick_sort_mpi.c"])
    subprocess.run(["mpicc", "-fopenmp", "-o", "hybrid_quick_sort", "hybrid_quick_sort.c"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--omp_threads', type=int, default=4, help='OpenMP threads')
    parser.add_argument('--mpi_processes', type=int, default=4, help='MPI processes')
    parser.add_argument('--hybrid_mpi', type=int, default=2, help='MPI processes for hybrid')
    parser.add_argument('--hybrid_omp', type=int, default=2, help='OpenMP threads per MPI process for hybrid')
    parser.add_argument('--min_val', type=int, default=0, help='Minimum random value')
    parser.add_argument('--max_val', type=int, default=1000000, help='Maximum random value')
    args = parser.parse_args()

    # Compile all programs first
    compile_programs()
    
    # Get array size
    n = int(input("Enter number of elements for testing: "))
    
    # Generate random array
    elements = generate_random_array(n, args.min_val, args.max_val)
    print(f"\nGenerated random array of size {n} (values {args.min_val}-{args.max_val})")
    
    # Save to file
    input_file = save_input_to_file(n, elements)
    
    # Run implementations
    results = {
        'Sequential': {},
        f'OpenMP ({args.omp_threads} threads)': {},
        f'MPI ({args.mpi_processes} processes)': {},
        f'Hybrid ({args.hybrid_mpi} MPI × {args.hybrid_omp} OMP)': {}
    }
    
    # Run sequential
    sorted_array, time = run_quick_sort(input_file, "sequential")
    results['Sequential']['sorted_array'] = sorted_array
    results['Sequential']['time'] = time
    
    # Run OpenMP
    sorted_array, time = run_quick_sort(input_file, "openmp", args.omp_threads)
    results[f'OpenMP ({args.omp_threads} threads)']['sorted_array'] = sorted_array
    results[f'OpenMP ({args.omp_threads} threads)']['time'] = time
    
    # Run MPI
    sorted_array, time = run_quick_sort(input_file, "mpi", args.mpi_processes)
    results[f'MPI ({args.mpi_processes} processes)']['sorted_array'] = sorted_array
    results[f'MPI ({args.mpi_processes} processes)']['time'] = time
    
    # Run Hybrid
    sorted_array, time = run_quick_sort(input_file, "hybrid", mpi_processes=args.hybrid_mpi, omp_threads=args.hybrid_omp)
    results[f'Hybrid ({args.hybrid_mpi} MPI × {args.hybrid_omp} OMP)']['sorted_array'] = sorted_array
    results[f'Hybrid ({args.hybrid_mpi} MPI × {args.hybrid_omp} OMP)']['time'] = time
    
    # Print results
    print("\nPerformance Results:")
    for impl in results:
        print(f"{impl}: {results[impl]['time']:.6f} seconds")
    
    # Plot results
    plt.figure(figsize=(12, 6))
    colors = ['blue', 'green', 'red', 'purple']
    plt.bar(results.keys(), [results[impl]['time'] for impl in results], color=colors)
    plt.ylabel('Execution Time (seconds)')
    plt.title('Quick Sort Performance Comparison')
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('quick_sort_performance.png')
    plt.show()

if __name__ == "__main__":
    main()