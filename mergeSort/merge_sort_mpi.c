/*
 * File: merge_sort_mpi.c
 * Description: Parallel Merge Sort using MPI with user input and execution time
 */
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
    int rank, size, n, *data = NULL;
    int *sub_data, *sorted = NULL;
    double start_time, end_time;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

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

        start_time = MPI_Wtime();  // Start timing at rank 0
    }

    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    int local_n = n / size;
    sub_data = (int *)malloc(local_n * sizeof(int));
    if (sub_data == NULL) {
        printf("Rank %d: Memory allocation failed!\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    MPI_Scatter(data, local_n, MPI_INT, sub_data, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    mergeSort(sub_data, 0, local_n - 1);

    if (rank == 0)
        sorted = (int *)malloc(n * sizeof(int));

    MPI_Gather(sub_data, local_n, MPI_INT, sorted, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        mergeSort(sorted, 0, n - 1); // Final sort
        end_time = MPI_Wtime();     // End timing

        printf("Sorted array:\n");
        for (int i = 0; i < n; i++)
            printf("%d ", sorted[i]);
        printf("\n");

       //printf("Execution time: %.6f seconds\n", end_time - start_time);
        printf("MPI %.6f\n", end_time - start_time);
        free(data);
        free(sorted);
    }

    free(sub_data);
    MPI_Finalize();
    return 0;
}
