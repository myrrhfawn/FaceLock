#!/bin/bash

# Перевіряємо, чи передано ім'я файлу main.py
if [ $# -eq 0 ]; then
    echo "Потрібно вказати ім'я файлу main.py"
    exit 1
fi

# Запускаємо pyinstaller з параметрами
pyinstaller --onefile --windowed "$1"

# ./build.sh main.py
