#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <omp.h>
#include <time.h>

// Function to swap two elements
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// Partition function for Quick Sort
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}

// Hybrid Quick Sort with OpenMP
void hybrid_quick_sort(int arr[], int low, int high, int depth) {
    if (low < high) {
        int pi = partition(arr, low, high);

        if (depth <= 0) {
            // Sequential execution when depth reaches 0
            hybrid_quick_sort(arr, low, pi - 1, 0);
            hybrid_quick_sort(arr, pi + 1, high, 0);
        } else {
            #pragma omp parallel sections
            {
                #pragma omp section
                hybrid_quick_sort(arr, low, pi - 1, depth - 1);

                #pragma omp section
                hybrid_quick_sort(arr, pi + 1, high, depth - 1);
            }
        }
    }
}

int main(int argc, char* argv[]) {
    int rank, size, n, *data = NULL, *local_data;
    double start_time, end_time;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (rank == 0) {
        printf("Enter number of elements: ");
        scanf("%d", &n);

        data = (int*)malloc(n * sizeof(int));
        srand(time(NULL));
        for (int i = 0; i < n; i++) {
            data[i] = rand() % 1000000;
        }

        start_time = MPI_Wtime();
    }

    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    int local_n = n / size;
    local_data = (int*)malloc(local_n * sizeof(int));

    MPI_Scatter(data, local_n, MPI_INT, local_data, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    #pragma omp parallel
    {
        #pragma omp single
        hybrid_quick_sort(local_data, 0, local_n - 1, 4);
    }

    // Gather all sorted subarrays at root
    MPI_Gather(local_data, local_n, MPI_INT, data, local_n, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        // Final merge sort of the gathered sorted subarrays
        hybrid_quick_sort(data, 0, n - 1, 4);
        end_time = MPI_Wtime();

        printf("First 10 elements of sorted array:\n");
        for (int i = 0; i < 10 && i < n; i++) {
            printf("%d ", data[i]);
        }
        printf("\nLast 10 elements of sorted array:\n");
        for (int i = (n > 10 ? n - 10 : 0); i < n; i++) {
            printf("%d ", data[i]);
        }
        printf("\n");

        printf("Hybrid Quick Sort completed in %.6f seconds\n", end_time - start_time);
        free(data);
    }

    free(local_data);
    MPI_Finalize();
    return 0;
}