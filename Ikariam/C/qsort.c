void swap(float* array, int i, int j) {
    float temp = array[i];
    array[i] = array[j];
    array[j] = temp;
}

// Funkcja dzieląca tablicę na dwie części i zwracająca indeks punktu podziału
int partition(float* array, int low, int high) {
    float pivot = array[high];  // Wybieramy ostatni element jako pivot
    int i = low - 1;             // Indeks mniejszej wartości

    for (int j = low; j <= high - 1; j++) {
        // Jeśli aktualny element jest mniejszy lub równy pivotowi, zamieniamy go z elementem mniejszym
        if (array[j] <= pivot) {
            i++;
            swap(array, i, j);
        }
    }

    swap(array, i + 1, high);  // Zamieniamy pivot z elementem większym
    return i + 1;              // Zwracamy indeks punktu podziału
}

// Implementacja algorytmu QuickSort dla tablicy float
void qqsort(float* array, int low, int high) {
    if (low < high) {
        int pivot = partition(array, low, high);  // Podział tablicy

        // Rekurencyjnie sortujemy elementy przed i po punkcie podziału
        qqsort(array, low, pivot - 1);
        qqsort(array, pivot + 1, high);
    }
}