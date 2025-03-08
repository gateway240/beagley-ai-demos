#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/*
  We declare the functions from algorithms.c with 'extern'
  so that we can call them here. No separate header file needed.
*/
extern void   getMidElement(int *arr, int n);
extern void    binarySearch(int *arr, int n);
extern void        sumArray(int *arr, int n);
extern void       mergeSort(int *arr, int n);
extern void      bubbleSort(int *arr, int n);

/*
 * measureTime() - measures time (in ms) that 'func' takes on
 * an array of size n, calling func(arr,n) exactly once.
 */
static double measureTime(void (*func)(int*, int), int *arr, int n) {
    clock_t start = clock();
    func(arr, n);
    clock_t end = clock();

    // convert to milliseconds
    double elapsed_ms = 1000.0 * (double)(end - start) / CLOCKS_PER_SEC;
    return elapsed_ms;
}

/*
 * Generates an array of size n with random values in [0, n).
 * Caller must free the array.
 */
static int* generateArray(int n) {
    int *arr = (int *)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        arr[i] = rand() % n;
    }
    return arr;
}

/*
 * A universal test bench that:
 *   1. Starts with an initial array size (e.g. 1).
 *   2. Tenfolds the size each time (up to 7 times).
 *   3. Stops when a single run of the function exceeds 1 second (1000 ms).
 *   4. Prints the measured time in milliseconds at each step.
 */
static void runBench(const char* label, void (*func)(int*, int)) {
    printf("=== %s ===\n", label);

    int n = 1;  // starting size
    for (int i = 0; i <= 7; i++) {
        // Prepare data
        int* arr = generateArray(n);

        // If you want a sorted array for binarySearch, for instance:
        // mergeSort(arr, n);  // uncomment if needed

        double t = measureTime(func, arr, n);

        printf("n = %10d  -->  time = %10.3f ms\n", n, t);

        free(arr);

        if (t > 1000.0) {  // time is > 1 second
            printf("Time exceeded 1 second, stopping.\n\n");
            break;
        }
        n *= 10;  // double the size
    }
}

int main() {
    srand((unsigned int) time(NULL));

    runBench("O(1)     : getMidElement", getMidElement);
    runBench("O(log n) : binarySearch",    binarySearch);
    runBench("O(n)     : sumArray",        sumArray);
    runBench("O(n log n): mergeSort",      mergeSort);
    runBench("O(n^2)   : bubbleSort",      bubbleSort);

    return 0;
}
