
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

int partition(int arr[], int low, int high) {
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

void parallelQuickSort(int arr[], int low, int high, int depth) {
    if (low < high) {
        int pi = partition(arr, low, high);

        if (depth <= 0) {
            parallelQuickSort(arr, low, pi - 1, 0);
            parallelQuickSort(arr, pi + 1, high, 0);
        } else {
            #pragma omp parallel sections
            {
                #pragma omp section
                parallelQuickSort(arr, low, pi - 1, depth - 1);

                #pragma omp section
                parallelQuickSort(arr, pi + 1, high, depth - 1);
            }
        }
    }
}

void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

int main() {
    int n;
    printf("Enter number of elements: ");
    scanf("%d", &n);

    int *arr = (int *)malloc(n * sizeof(int));
    if (arr == NULL) {
        printf("Memory allocation failed!\n");
        return 1;
    }

    printf("Enter %d integers:\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }

    double start = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp single
        parallelQuickSort(arr, 0, n - 1, 4);
    }
    double end = omp_get_wtime();

    printf("Sorted array:\n");
    printArray(arr, n);
    printf("Execution time: %f seconds\n", end - start);

    free(arr);
    return 0;
}
