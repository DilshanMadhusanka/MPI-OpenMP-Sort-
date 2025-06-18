
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

void merge(int arr[], int l, int m, int r) {
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;

    int *L = (int *)malloc(n1 * sizeof(int));
    int *R = (int *)malloc(n2 * sizeof(int));

    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    i = 0;
    j = 0;
    k = l;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }

    while (i < n1) {
        arr[k++] = L[i++];
    }

    while (j < n2) {
        arr[k++] = R[j++];
    }

    free(L);
    free(R);
}

void parallelMergeSort(int arr[], int l, int r, int depth) {
    if (l < r) {
        int m = l + (r - l) / 2;

        if (depth <= 0) {
            parallelMergeSort(arr, l, m, 0);
            parallelMergeSort(arr, m + 1, r, 0);
        } else {
            #pragma omp parallel sections
            {
                #pragma omp section
                parallelMergeSort(arr, l, m, depth - 1);

                #pragma omp section
                parallelMergeSort(arr, m + 1, r, depth - 1);
            }
        }
        merge(arr, l, m, r);
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
        //ensures that only one thread begins the recursive sorting call
        #pragma omp single
        parallelMergeSort(arr, 0, n - 1, 4);  
    }
    double end = omp_get_wtime();

    printf("Sorted array:\n");
    printArray(arr, n);
    printf("OPENMP %.6f\n", end - start);
    free(arr);
    return 0;
}


//gcc -fopenmp merge_sort_openmp.c -o merge_sort_openmp