# memory-hd

Набор скриптов для генерации C++ программ с разными сценариями утечек памяти и мониторинга их работы.

## Описание

Репозиторий содержит инструменты для автоматизации экспериментов с утечками памяти:

1. **Генерация C++ кода** (`g.py`): создаёт исходники с разными типами поведения памяти — без утечек, с утечками и периодическими утечками.
2. **Пример шаблона** (`lol.cpp`): демонстрационный код для сценария без утечек.
3. **Мониторинг памяти** (`main.py`): запускает сгенерированный C++ исполняемый файл, читает области памяти процесса через WinAPI (CTypes), собирает снимки и сохраняет их с классификацией в JSON.

## Структура репозитория

```
hd/
├─ g.py        # Генерация C++ исходников с разными сценариями утечек
├─ lol.cpp       # Пример C++ кода без утечек памяти
└─ main.py       # Мониторинг запущенного C++ процесса и сохранение снимков памяти
```

## Требования

* Python 3.8 или выше
* Операционная система Windows (использует WinAPI через `ctypes`)
* Компилятор C++ с поддержкой C++17 (например, MSVC или MinGW)

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/HellDiver830/hd.git
   cd hd
   ```
2. (Опционально) Создайте виртуальное окружение и активируйте его:

   ```bash
   python -m venv venv
   venv\\Scripts\\activate # Windows
   ```

## Использование

### Генерация C++ исходников

```bash
python g.py
```

В результате будет перезаписан файл `lol.cpp` с кодом сценария `no_leak`.

### Компиляция C++ кода

Используйте предпочитаемый компилятор, например:

```bash
g++ lol.cpp -std=c++17 -o test.exe
```

Или для MSVC:

```batch
cl /std:c++17 lol.cpp /Fe:test.exe
```

### Мониторинг и сбор снимков

```bash
python main.py
```

По умолчанию скрипт сгенерирует и запустит `test.exe` (внутри `monitor_process` укажите путь к вашему исполняемому файлу), соберёт данные о чтении памяти каждые 0.5 секунды в течение 30 сек и сохранит JSON-файл:

```
no_leak_1.json
no_leak_2.json
...
```

Вы можете изменить параметры в `main.py`:

* `interval` — интервал между снимками (секунды)
* `duration` — длительность мониторинга (секунды)
* Путь к исполняемому файлу в вызове `monitor_process`

## Выходные данные

Каждый JSON содержит:

```json
{
  "classification": 2,            // 2 — без утечек
  "memory_log": [                // Список снимков
    {
      "timestamp": 169...,        // Метка времени
      "memory_data": [           // Сырые данные из областей памяти
        {
          "address": "0x...",
          "hex_values": "ff 00 ...",
          "dec_values": "255 0 ..."
        },
        ...
      ]
    },
    ...
  ]
}
```

## Лицензия

MIT License
