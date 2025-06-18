
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int partition(int *arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }

    int temp = arr[i + 1];
    arr[i + 1] = arr[high];
    arr[high] = temp;

    return i + 1;
}

void quickSort(int *arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

int main(int argc, char *argv[]) {
    int rank, size, n;
    int *data = NULL, *local_data, *sorted = NULL;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    double start_time, end_time;

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

        start_time = MPI_Wtime();  // Start timing on master process
    }

    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    int local_n = n / size;
    local_data = (int *)malloc(local_n * sizeof(int));
    if (local_data == NULL) {
        printf("Rank %d: Memory allocation failed!\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    //Distributes equal chunks of the array from rank 0 to all ranks.
    MPI_Scatter(data, local_n, MPI_INT, local_data, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    quickSort(local_data, 0, local_n - 1);

    if (rank == 0)
        sorted = (int *)malloc(n * sizeof(int));

    //Collects sorted chunks from all ranks back to rank 0.
    MPI_Gather(local_data, local_n, MPI_INT, sorted, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        quickSort(sorted, 0, n - 1);  // Final merge sort
        end_time = MPI_Wtime();      // Stop timing

        printf("Sorted array:\n");
        for (int i = 0; i < n; i++)
        printf("%d ", sorted[i]);
        printf("\n");

        printf("Execution time: %.6f seconds\n", end_time - start_time);

        free(data);
        free(sorted);
    }

    free(local_data);
    MPI_Finalize();
    return 0;
}
