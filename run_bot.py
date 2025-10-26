#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота с проверками
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Проверяет наличие необходимых файлов"""
    print("🔍 Проверка требований...")
    
    # Проверяем .env файл
    if not Path('.env').exists():
        print("❌ Файл .env не найден!")
        return False
    
    # Проверяем main.py
    if not Path('main.py').exists():
        print("❌ Файл main.py не найден!")
        return False
    
    # Проверяем папку data
    if not Path('data').exists():
        print("⚠️  Папка data не найдена, будет создана автоматически")
    
    print("✅ Все требования выполнены")
    return True

def stop_existing_bots():
    """Останавливает существующие экземпляры бота"""
    print("🛑 Остановка существующих экземпляров...")
    
    try:
        # Ищем процессы Python с main.py
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True, text=True, shell=True
        )
        
        if 'main.py' in result.stdout:
            print("Найдены запущенные экземпляры, останавливаем...")
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], shell=True)
            time.sleep(2)
        
        print("✅ Все экземпляры остановлены")
        
    except Exception as e:
        print(f"⚠️  Не удалось остановить процессы: {e}")

def start_bot():
    """Запускает бота"""
    print("🚀 Запуск бота...")
    
    try:
        # Запускаем бота
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Бот запущен с PID: {process.pid}")
        print("📱 Бот готов к работе!")
        print("💡 Для остановки нажмите Ctrl+C")
        
        # Ждем завершения
        try:
            stdout, stderr = process.communicate()
            if stdout:
                print("STDOUT:", stdout)
            if stderr:
                print("STDERR:", stderr)
        except KeyboardInterrupt:
            print("\n🛑 Остановка бота...")
            process.terminate()
            process.wait()
            print("✅ Бот остановлен")
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    print("🤖 TgProbot - Запуск")
    print("=" * 40)
    
    # Проверяем требования
    if not check_requirements():
        print("❌ Запуск невозможен")
        sys.exit(1)
    
    # Останавливаем существующие экземпляры
    stop_existing_bots()
    
    # Запускаем бота
    if not start_bot():
        print("❌ Не удалось запустить бота")
        sys.exit(1)

if __name__ == "__main__":
    main()
