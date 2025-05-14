import os
import time
import json
import base64
import hmac
import struct
import pyautogui
import subprocess
from datetime import datetime

import config

# Настройки
STEAM_PATH = config.STEAM_PATH
ACCOUNTS_DIR = config.ACCOUNTS_DIR
ACCOUNTS_FILE = config.ACCOUNTS_FILE  # Файл с логинами:паролями
DELAY = 5


def generate_2fa(shared_secret):
    """Генерация 5-значного Steam Guard кода с латинскими буквами и цифрами"""
    try:
        # Проверка shared_secret
        if not shared_secret:
            raise ValueError("shared_secret is empty")

        # Декодирование Base64
        try:
            key = base64.b64decode(shared_secret, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid Base64 in shared_secret: {e}")

        # Получение времени
        timestamp = int(time.time())
        print(f"[DEBUG] Timestamp: {timestamp} ({datetime.fromtimestamp(timestamp)})")

        # Формирование временного буфера (время / 30 секунд)
        time_buffer = struct.pack('>Q', timestamp // 30)

        # Вычисление HMAC-SHA1
        hmac_hash = hmac.new(key, time_buffer, 'sha1').digest()
        print(f"[DEBUG] HMAC hash: {hmac_hash.hex()}")

        # Получение офсета
        offset = hmac_hash[-1] & 0x0F
        print(f"[DEBUG] Offset: {offset}")

        # Извлечение 4 байт с учетом офсета
        code = struct.unpack('>I', hmac_hash[offset:offset + 4])[0] & 0x7FFFFFFF
        print(f"[DEBUG] Raw code: {code}")

        # Таблица символов Steam Guard (26 символов: 2-9, B-Y, без A, I, O, U, Z)
        steam_chars = '23456789BCDFGHJKMNPQRTVWXY'

        # Генерация 5-значного кода
        final_code = ''
        for _ in range(5):
            code, remainder = divmod(code, len(steam_chars))
            final_code += steam_chars[remainder]

        print(f"[DEBUG] Final 2FA code: {final_code}")
        return final_code

    except Exception as e:
        print(f"❌ Ошибка в generate_2fa: {e}")
        raise


def load_mafile(account_name):
    """Загрузка .mafile"""
    path = os.path.join(ACCOUNTS_DIR, f"{account_name}.mafile")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_accounts():
    """Загрузка логинов и паролей"""
    accounts = {}
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    login, password = line.strip().split(':', 1)
                    accounts[login] = password
    return accounts


def find_mafile_accounts():
    """Поиск всех .mafile файлов в ACCOUNTS_DIR"""
    print(f"[DEBUG] Поиск файлов в папке: {ACCOUNTS_DIR}")
    mafiles = []
    try:
        for f in os.listdir(ACCOUNTS_DIR):
            print(f"[DEBUG] Обнаружен файл: {f}")
            if f.lower().endswith('.mafile'):
                mafiles.append(f)
    except Exception as e:
        print(f"❌ Ошибка при доступе к папке {ACCOUNTS_DIR}: {e}")
        return []

    accounts = [os.path.splitext(f)[0] for f in mafiles]
    print(f"[DEBUG] Найдено .mafile файлов: {len(accounts)}")
    return accounts


def kill_process(name):
    """Закрытие процесса"""
    os.system(f"taskkill /f /im {name}.exe >nul 2>&1")
    time.sleep(2)


def login(account, password, shared_secret):
    """Процесс входа"""
    kill_process("steam")

    # Запуск Steam
    subprocess.Popen(STEAM_PATH)
    time.sleep(DELAY * 2)

    # Ввод данных
    pyautogui.typewrite(account)
    pyautogui.press('tab')
    pyautogui.typewrite(password)
    pyautogui.press('enter')
    time.sleep(DELAY)

    # Ввод 2FA
    code = generate_2fa(shared_secret)
    pyautogui.typewrite(code)
    pyautogui.press('enter')
    print(f"🔑 {account} | Код 2FA: {code}")
    time.sleep(DELAY * 2)


def main():
    # Напоминание о раскладке
    print("⚠️ Пожалуйста, переключите раскладку клавиатуры на английскую (US English)!")
    print(f"⏳ Даём 5 секунд для смены раскладки...")
    time.sleep(5)  # Пауза для смены раскладки пользователем

    # Создаем папки если их нет
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)

    # Загружаем пароли
    passwords = load_accounts()
    if not passwords:
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            f.write("логин1:пароль1\nлогин2:пароль2")
        print(f"📝 Создан файл {ACCOUNTS_FILE}. Заполните его!")
        return

    while True:
        # Поиск аккаунтов с .mafile
        mafile_accounts = find_mafile_accounts()
        if not mafile_accounts:
            print("❌ Не найдено ни одного .mafile файла в папке", ACCOUNTS_DIR)
            return

        print("\n📋 Найденные аккаунты:")
        for i, account in enumerate(mafile_accounts, 1):
            print(f"{i}. {account}")

        # Запрос выбора аккаунта
        try:
            choice = input("\nВведите номер аккаунта (или 'q' для выхода): ")
            if choice.lower() == 'q':
                break

            choice = int(choice)
            if choice < 1 or choice > len(mafile_accounts):
                print("❌ Неверный номер аккаунта!")
                continue

            account = mafile_accounts[choice - 1]
            print(f"\n🚀 Вход в аккаунт: {account}")

            # Проверка наличия пароля
            password = passwords.get(account)
            if not password:
                print(f"❌ Пароль для {account} не найден в {ACCOUNTS_FILE}!")
                continue

            # Загрузка mafile и вход
            try:
                mafile = load_mafile(account)
                login(account, password, mafile['shared_secret'])

                input("\n⏳ Нажмите Enter для выхода из аккаунта и возврата в меню...")
                kill_process("steam")
            except Exception as e:
                print(f"❌ Ошибка: {str(e)}")
                input("\n⏳ Нажмите Enter для возврата в меню...")
                kill_process("steam")

        except ValueError:
            print("❌ Введите корректный номер аккаунта!")
            continue


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()