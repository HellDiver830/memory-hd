import random
import ctypes
import ctypes.wintypes
import time
import subprocess
import json

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


PROCESS_ALL_ACCESS = 0x1F0FFF

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.wintypes.LPVOID),
        ("AllocationBase", ctypes.wintypes.LPVOID),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
    ]

def get_process_handle(pid):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    return handle

def read_memory(handle, address, size):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    buffer = ctypes.create_string_buffer(size)
    bytesRead = ctypes.c_size_t(0)
    
    if not kernel32.ReadProcessMemory(handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(bytesRead)):
        raise ctypes.WinError(ctypes.get_last_error())
    
    return buffer.raw

def get_memory_regions(handle):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    address = 0
    memory_regions = []

    while address < 0x7FFFFFFFFFFF:  # Максимальный адрес для 64-битных систем
        mbi = MEMORY_BASIC_INFORMATION()
        if kernel32.VirtualQueryEx(handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        if mbi.State == 0x1000 and (mbi.Protect & 0xF0) in (0x20, 0x40):  # MEM_COMMIT and readable/writable
            memory_regions.append((mbi.BaseAddress, mbi.RegionSize))
        address += mbi.RegionSize

    return memory_regions

def memory_snapshot(pid, interval=0.5, duration=30):  # Увеличим продолжительность для тестирования
    handle = get_process_handle(pid)
    snapshots = []
    
    try:
        memory_regions = get_memory_regions(handle)
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Проверяем, не завершился ли процесс
            if ctypes.windll.kernel32.WaitForSingleObject(handle, 0) == 0:
                print("Процесс завершился, остановка сбора данных.")
                break

            snapshot = {"timestamp": time.time(), "memory_data": []}
            for base_address, region_size in memory_regions:
                for offset in range(0, region_size, 16):  # Читаем по 16 байт
                    address = base_address + offset
                    try:
                        raw_data = read_memory(handle, address, 16)
                        hex_values = " ".join(f"{b:02x}" for b in raw_data)
                        dec_values = " ".join(str(b) for b in raw_data)
                        snapshot["memory_data"].append({
                            "address": hex(address),
                            "hex_values": hex_values,
                            "dec_values": dec_values
                        })
                    except Exception as e:
                        print(f"Ошибка чтения по адресу {hex(address)}: {e}")
                        continue
            snapshots.append(snapshot)
            time.sleep(interval)
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
    
    return snapshots

def save_snapshot(snapshots, classification, filename="memory_snapshot.json"):
    data = {
        "classification": classification,
        "memory_log": snapshots
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Снимок памяти с классификацией сохранен в {filename}")

def monitor_process(script_path, interval=0.5, duration=30, lineprog):  # Увеличим `duration` для проверки
    # Добавляем ожидание завершения процесса C++ перед завершением скрипта
    process = subprocess.Popen([script_path])
    time.sleep(1)  # Ждем, пока процесс загрузится

    # Собираем временные серии данных о всей памяти процесса
    snapshots = memory_snapshot(process.pid, interval, duration)
    
    # Запрашиваем классификацию у пользователя
    #classification = input("Введите классификацию: 1 - с утечкой, 2 - без утечек, 3 - периодическая утечка: ")
    classification = 2
    print("классификация:  2 - без утечек")
    save_snapshot(snapshots, classification, f"no_leak_{str(lineprog)}.json")

    # Завершаем C++ процесс
    process.terminate()
    process.wait()

# Пример использования

NumProg = 110 # сколько программ нужно сгенерировать, отсканировать и соханить снимки сырой памяти
starNum = 1
while starNum <= 110:
    save_cpp_code('C:/Users/Zeone/source/repos/testerScrapC/testerScrapC/testerScrapC.cpp', 'no_leak')
    time.sleep(5)
    monitor_process("C:/Users/Zeone/source/repos/testerScrapC/x64/Debug/testerScrapC.exe", interval=0.5, duration=30 , starNum)
    starNum+=1



