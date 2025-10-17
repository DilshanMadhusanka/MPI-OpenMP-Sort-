# Parallel Sorting Algorithms (MPI + OpenMP)

A high-performance implementation of Merge Sort and Quick Sort using hybrid parallel programming (MPI for distributed memory and OpenMP for shared memory).

## Features

- **Multi-paradigm parallelism**: Combines MPI (distributed) + OpenMP (shared memory)
- **Algorithm comparisons**:
  - Sequential vs. OpenMP vs. MPI vs. Hybrid
- **Performance metrics**: Execution time analysis
- **Cross-platform**: Linux/Unix compatible

## Installation

### Prerequisites
- GCC (v9.0+)
- OpenMPI (v4.0+)
- OpenMP (included with GCC)
- Python 3 (for visualization)

### Compile All Implementations

#### Merge Sort versions
```bash
gcc -o merge_sort merge_sort.c
gcc -fopenmp -o merge_sort_openmp merge_sort_openmp.c 
mpicc -o merge_sort_mpi merge_sort_mpi.c
mpicc -fopenmp -o hybrid_merge_sort hybrid_merge_sort.c

```
#### Quick Sort versions
```bash
gcc -o quick_sort quick_sort.c
gcc -fopenmp -o quick_sort_openmp quick_sort_openmp.c
mpicc -o quick_sort_mpi quick_sort_mpi.c
mpicc -fopenmp -o hybrid_quick_sort hybrid_quick_sort.c
```

## Usage

#### Run Individual Implementations

#### Sequential
- ./merge_sort < input.txt

#### OpenMP (4 threads)
- export OMP_NUM_THREADS=4
- ./merge_sort_openmp < input.txt

#### MPI (4 processes)
- mpirun -np 4 ./merge_sort_mpi < input.txt

#### Hybrid (2 MPI processes × 2 OpenMP threads)
- export OMP_NUM_THREADS=2
- mpirun -np 2 ./hybrid_merge_sort < input.txt

## Project Structure
```bash
├── mergeSort/
│   ├── merge_sort.c             # Sequential
│   ├── merge_sort_openmp.c      # OpenMP
│   ├── merge_sort_mpi.c         # MPI
│   └── hybrid_merge_sort.c      # Hybrid
├── quickSort/
│   └── [same structure as mergeSort]
├── sort_comparison.py           # Performance analysis
└── input.txt                    # Sample input

```

### Key Sections Explained:
1. **Visualization**: The Python script generates comparative performance plots
2. **Hybrid Configuration**: Shows how to control MPI/OpenMP parallelism
3. **Portability**: Works on any Linux cluster with MPI/OpenMP support
4. **Extensibility**: Easy to add new algorithms (e.g., Radix Sort)



