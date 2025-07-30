import random

def generate_variable():
    """Генерирует случайную переменную с уникальными значениями и именами."""
    types = ["int", "float", "double", "char", "bool"]
    names = ["var", "data", "item", "value", "temp"]
    var_type = random.choice(types)
    var_name = random.choice(names) + str(random.randint(1, 100))
    value = generate_random_value(var_type)
    return f"{var_type} {var_name} = {value};"

def generate_random_value(var_type):
    """Генерирует случайное значение для переменной."""
    if var_type == "int":
        return random.randint(1, 100)
    elif var_type == "float":
        return round(random.uniform(1.0, 100.0), 2)
    elif var_type == "double":
        return round(random.uniform(1.0, 100.0), 6)
    elif var_type == "char":
        return f"'{chr(random.randint(65, 90))}'"  # Символы от 'A' до 'Z'
    elif var_type == "bool":
        return random.choice(["true", "false"])
    return "0"

def generate_cpp_code(leak_type="no_leak"):
    """
    Генерирует C++ код с разнообразными данными и поведением:
    - "leak": утечка памяти.
    - "periodic_leak": периодическая утечка.
    - "no_leak": без утечек.
    """
    variables = "\n    ".join([generate_variable() for _ in range(random.randint(3, 7))])

    if leak_type == "leak":
        code = f"""
#include <iostream>
#include <vector>
using namespace std;

void memoryLeak() {{
    {variables}
    for (int i = 0; i < 10; ++i) {{
        int* leak = new int[100]; // Выделение памяти, но без освобождения
        cout << "Iteration " << i << ": Memory allocated but not freed." << endl;
    }}
}}

int main() {{
    memoryLeak();
    return 0;
}}
"""
    elif leak_type == "periodic_leak":
        code = f"""
#include <iostream>
#include <vector>
using namespace std;

void periodicMemoryLeak() {{
    {variables}
    for (int i = 0; i < 10; ++i) {{
        int* leak = new int[100]; // Выделение памяти
        if (i % 2 == 0) {{
            delete[] leak; // Освобождение только для чётных итераций
        }}
        cout << "Iteration " << i << ": Memory conditionally freed." << endl;
    }}
}}

int main() {{
    periodicMemoryLeak();
    return 0;
}}
"""
    else:  # "no_leak"
        code = f"""
#include <iostream>
using namespace std;

void noMemoryLeak() {{
    {variables}
    for (int i = 0; i < 10; ++i) {{
        int* no_leak = new int[100]; // Выделение памяти
        delete[] no_leak; // Память корректно освобождается
        cout << "Iteration " << i << ": Memory allocated and freed." << endl;
    }}
}}

int main() {{
    noMemoryLeak();
    return 0;
}}
"""
    return code

def save_cpp_code(file_path, leak_type):
    """Сохраняет сгенерированный C++ код в указанный файл."""
    code = generate_cpp_code(leak_type)
    with open(file_path, "w") as file:
        file.write(code)
    print(f"Сгенерированный код ({leak_type}) сохранён в {file_path}.")
save_cpp_code('lol.cpp', 'no_leak')
# Автоматическая генерация нескольких программ
#def generate_multiple_cpp_files(output_folder, num_files=10):
#    """Создаёт несколько C++ файлов с разными типами утечек."""
#    leak_types = ["leak", "periodic_leak", "no_leak"]
#    for i in range(num_files):
#        leak_type = random.choice(leak_types)
#        file_name = f"{output_folder}/example_{i + 1}_{leak_type}.cpp"
#        save_cpp_code(file_name, leak_type)

# Пример использования
#generate_multiple_cpp_files("cpp_scripts", num_files=1)
