
#include <iostream>
using namespace std;

void noMemoryLeak() {
    int value9 = 78;
    double var98 = 23.78419;
    double temp43 = 13.655542;
    double data56 = 21.382137;
    char item33 = 'Z';
    for (int i = 0; i < 10; ++i) {
        int* no_leak = new int[100]; // Выделение памяти
        delete[] no_leak; // Память корректно освобождается
        cout << "Iteration " << i << ": Memory allocated and freed." << endl;
    }
}

int main() {
    noMemoryLeak();
    return 0;
}
