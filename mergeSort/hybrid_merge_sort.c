#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <omp.h>
#include <time.h>

// Function to merge two sorted subarrays arr[l..m] and arr[m+1..r]
void merge(int arr[], int l, int m, int r) {
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;

    int *L = (int *)malloc(n1 * sizeof(int)); // Temporary array for left half
    int *R = (int *)malloc(n2 * sizeof(int)); // Temporary array for right half

    // Copy data to temporary arrays L[] and R[]
    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    i = 0; j = 0; k = l;

    // Merge the temporary arrays back into arr[l..r]
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }

    // Copy remaining elements of L[], if any
    while (i < n1) arr[k++] = L[i++];

    // Copy remaining elements of R[], if any
    while (j < n2) arr[k++] = R[j++];

    free(L);
    free(R);
}

// Recursive parallel merge sort with controlled OpenMP parallelism depth
void parallelMergeSort(int arr[], int l, int r, int depth) {
    if (l < r) {
        int m = l + (r - l) / 2;

        if (depth <= 0) {
            // Sequential recursive calls once max parallel depth is reached
            parallelMergeSort(arr, l, m, 0);
            parallelMergeSort(arr, m + 1, r, 0);
        } else {
            // Parallelize recursive calls using OpenMP sections
            #pragma omp parallel sections
            {
                #pragma omp section
                parallelMergeSort(arr, l, m, depth - 1);

                #pragma omp section
                parallelMergeSort(arr, m + 1, r, depth - 1);
            }
        }
        // Merge the sorted halves
        merge(arr, l, m, r);
    }
}

int main(int argc, char *argv[]) {
    int rank, size, n, *data = NULL;
    int *sub_data, *sorted = NULL;
    double start_time, end_time;

    // Initialize MPI environment
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);  // Get process rank
    MPI_Comm_size(MPI_COMM_WORLD, &size);  // Get total number of processes

    if (rank == 0) {
        // Only rank 0 reads input data
        printf("Enter number of elements: ");
        scanf("%d", &n);

        data = (int *)malloc(n * sizeof(int));
        printf("Enter %d integers:\n", n);
        for (int i = 0; i < n; i++) {
            scanf("%d", &data[i]);
        }

        start_time = MPI_Wtime();  // Start timing on rank 0
    }

    // Broadcast the number of elements to all processes
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    int local_n = n / size;  // Number of elements per process (assumes divisible)
    sub_data = (int *)malloc(local_n * sizeof(int));

    // Scatter chunks of the array to all processes
    MPI_Scatter(data, local_n, MPI_INT, sub_data, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    // Each process sorts its chunk in parallel using OpenMP
    #pragma omp parallel
    {
        #pragma omp single
        parallelMergeSort(sub_data, 0, local_n - 1, 4); // depth = 4 controls OpenMP recursion depth
    }

    if (rank == 0) {
        sorted = (int *)malloc(n * sizeof(int)); // Allocate array for gathered results
    }

    // Gather sorted subarrays back to root process
    MPI_Gather(sub_data, local_n, MPI_INT, sorted, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        // Final merge of the sorted chunks using OpenMP parallel merge sort
        #pragma omp parallel
        {
            #pragma omp single
            parallelMergeSort(sorted, 0, n - 1, 4);
        }

        end_time = MPI_Wtime();  // End timing on rank 0

        // Print first 10 elements for verification
        printf("Sorted array:\n");
        for (int i = 0; i < ((n < 10) ? n : 10); i++) {
            printf("%d ", sorted[i]);
        }
        if (n > 10) printf("... ");
        printf("\n");

        printf("HYBRID MERGE SORT TIME: %.6f seconds\n", end_time - start_time);

        free(data);
        free(sorted);
    }

    free(sub_data);

    // Finalize MPI environment
    MPI_Finalize();

    return 0;
}
