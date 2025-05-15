import json
import os
import subprocess
import time

import pyautogui

import config
import generate_2fa
from generate_2fa import generate_2fa

# Настройки
STEAM_PATH = config.STEAM_PATH
ACCOUNTS_DIR = config.ACCOUNTS_DIR
ACCOUNTS_FILE = config.ACCOUNTS_FILE  # Файл с логинами:паролями
DELAY = config.DELAY


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


def clear_steam_auth_data():
    """Очистка данных авторизации Steam"""
    print("[INFO] Очищаем данные авторизации Steam...")
    kill_process("steam")  # Закрываем Steam
    # Удаляем loginusers.vdf
    loginusers_path = os.path.join(os.path.dirname(STEAM_PATH), "config", "loginusers.vdf")
    try:
        if os.path.exists(loginusers_path):
            os.remove(loginusers_path)
            print(f"[INFO] Удален файл: {loginusers_path}")
        else:
            print(f"[INFO] Файл {loginusers_path} не найден")
    except Exception as e:
        print(f"[ERROR] Ошибка при удалении loginusers.vdf: {e}")
    # Удаляем кэш Steam
    cache_path = os.path.join(os.path.dirname(STEAM_PATH), "appcache")
    try:
        if os.path.exists(cache_path):
            for item in os.listdir(cache_path):
                item_path = os.path.join(cache_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"[INFO] Удален файл кэша: {item_path}")
    except Exception as e:
        print(f"[ERROR] Ошибка при очистке кэша: {e}")


def login(account, password, shared_secret):
    """Процесс входа"""
    clear_steam_auth_data()
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
