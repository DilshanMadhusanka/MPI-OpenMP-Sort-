
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

void merge(int *arr, int l, int m, int r) {
    int n1 = m - l + 1;
    int n2 = r - m;

    int *L = (int *)malloc(n1 * sizeof(int));
    int *R = (int *)malloc(n2 * sizeof(int));

    for (int i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    int i = 0, j = 0, k = l;
    while (i < n1 && j < n2) {
        arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];
    }
    
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];

    free(L);
    free(R);
}

void mergeSort(int *arr, int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}

int main(int argc, char *argv[]) {
    int rank, size, n;
    int *data = NULL;     // Full data array 
    int *sub_data = NULL; // Subarray for each process
    int *sorted = NULL;   // Final sorted array 
    double start_time, end_time;

    MPI_Init(&argc, &argv);                   // Initialize MPI environment
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);     // Get current process rank
    MPI_Comm_size(MPI_COMM_WORLD, &size);     // Get total number of processes

    if (rank == 0) {
        printf("Enter number of elements: ");
        scanf("%d", &n);

        data = (int *)malloc(n * sizeof(int));
        if (data == NULL) {
            printf("Memory allocation failed!\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        printf("Enter %d integers:\n", n);
        for (int i = 0; i < n; i++) {
            scanf("%d", &data[i]);
        }

        start_time = MPI_Wtime();  
    }

    // Broadcast the size of the array to all processes
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    int local_n = n / size;

    // Allocate local subarray for each process
    sub_data = (int *)malloc(local_n * sizeof(int));
    if (sub_data == NULL) {
        printf("Rank %d: Memory allocation failed!\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    //Distributes equal chunks of the array from rank 0 to all ranks.
    MPI_Scatter(data, local_n, MPI_INT, sub_data, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    mergeSort(sub_data, 0, local_n - 1);

    if (rank == 0)
        sorted = (int *)malloc(n * sizeof(int));  

    //Collects sorted chunks from all ranks back to rank 0.
    MPI_Gather(sub_data, local_n, MPI_INT, sorted, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        mergeSort(sorted, 0, n - 1);

        end_time = MPI_Wtime();  

        printf("Sorted array:\n");

        for (int i = 0; i < n; i++)
        printf("%d ", sorted[i]);
        printf("\n");

        printf("MPI %.6f\n", end_time - start_time);

        free(data);
        free(sorted);
    }

    free(sub_data);
    MPI_Finalize();  
    return 0;
}


// mpicc merge_sort_mpi.c -o merge_sort_mpi


