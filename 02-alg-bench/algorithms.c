#include <stdlib.h>  // for malloc, free, rand

/* 
 * O(1) function:
 * Returns the first element (constant time).
 * Refactored to a void function for uniform signature.
 */
void getMidElement(int *arr, int n) {
    if (n > 0) {
        // Use volatile to ensure the compiler doesn't optimize this away.
        volatile int x = arr[n/2];
    }
}

/* 
 * O(log n) function:
 * Binary search for a "target" in a sorted array.
 * We'll pick a mid-element as "target" for demonstration,
 * but the function just runs a typical binary search loop.
 */
void binarySearch(int *arr, int n) {
    if (n == 0) return;

    // Let's pick the middle element as the target to search for:
    int target = arr[n / 2];

    int left = 0;
    int right = n - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            // store in volatile to avoid optimization
            volatile int foundIndex = mid;
            return;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
}

/*
 * O(n) function:
 * Sums all elements in the array (linear time).
 * We'll do the sum but discard it in a volatile variable.
 */
void sumArray(int *arr, int n) {
    long long total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    volatile long long sink = total;  // so it's not optimized away
}

/*
 * O(n log n) function:
 * Merge Sort. We define a single function that takes (arr, n).
 * Internally, it calls a static helper with left/right.
 */
static void merge(int *arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    int *L = (int *)malloc(n1 * sizeof(int));
    int *R = (int *)malloc(n2 * sizeof(int));

    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];

    int i = 0, j = 0, k = left;

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

static void mergeSortRecursive(int *arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSortRecursive(arr, left, mid);
        mergeSortRecursive(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

void mergeSort(int *arr, int n) {
    if (n <= 1) return;
    mergeSortRecursive(arr, 0, n - 1);
}

/*
 * O(n^2) function:
 * Bubble Sort on the array.
 */
void bubbleSort(int *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}
