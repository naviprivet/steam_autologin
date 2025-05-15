import json
import os
import subprocess
import time

import pyautogui
from colorama import Fore

from config import ACCOUNTS_DIR, ACCOUNTS_FILE, DELAY, STEAM_PATH
from generate_2fa import generate_2fa


def load_mafile(account_name):
    """Загрузка .mafile"""
    path = os.path.join(ACCOUNTS_DIR, f"{account_name}.mafile")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка при загрузке {path}: {e}")
        raise


def load_accounts():
    """Загрузка логинов и паролей"""
    accounts = {}
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        login, password = line.strip().split(':', 1)
                        accounts[login] = password
            print(f"{Fore.BLUE}[DEBUG] Загружено аккаунтов из {ACCOUNTS_FILE}: {len(accounts)}")
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка при загрузке {ACCOUNTS_FILE}: {e}")
    return accounts


def find_mafile_accounts():
    """Поиск всех .mafile файлов в ACCOUNTS_DIR"""
    print(f"{Fore.BLUE}[DEBUG] Поиск файлов в папке: {ACCOUNTS_DIR}")
    mafiles = []
    try:
        for f in os.listdir(ACCOUNTS_DIR):
            print(f"{Fore.BLUE}[DEBUG] Обнаружен файл: {f}")
            if f.lower().endswith('.mafile'):
                mafiles.append(f)
    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка при доступе к папке {ACCOUNTS_DIR}: {e}")
        return []

    accounts = [os.path.splitext(f)[0] for f in mafiles]
    print(f"{Fore.BLUE}[DEBUG] Найдено .mafile файлов: {len(accounts)}")
    return accounts


def kill_process(name):
    """Закрытие процесса"""
    print(f"{Fore.GREEN}[INFO] Закрываем процесс: {name}.exe")
    os.system(f"taskkill /f /im {name}.exe >nul 2>&1")
    time.sleep(2)


def clear_steam_auth_data():
    """Очистка данных авторизации Steam"""
    print(f"{Fore.GREEN}[INFO] Очищаем данные авторизации Steam...")
    kill_process("steam")
    loginusers_path = os.path.join(os.path.dirname(STEAM_PATH), "config", "loginusers.vdf")
    try:
        if os.path.exists(loginusers_path):
            os.remove(loginusers_path)
            print(f"{Fore.GREEN}[INFO] Удален файл: {loginusers_path}")
        else:
            print(f"{Fore.GREEN}[INFO] Файл {loginusers_path} не найден")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Ошибка при удалении loginusers.vdf: {e}")
    cache_path = os.path.join(os.path.dirname(STEAM_PATH), "appcache")
    try:
        if os.path.exists(cache_path):
            for item in os.listdir(cache_path):
                item_path = os.path.join(cache_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"{Fore.GREEN}[INFO] Удален файл кэша: {item_path}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Ошибка при очистке кэша: {e}")


def login(account, password, shared_secret, status_label, root):
    """Процесс входа"""
    try:
        clear_steam_auth_data()
        kill_process("steam")

        status_label.config(text="Запускаем Steam...", bootstyle="success")
        print(f"{Fore.GREEN}[INFO] Запускаем Steam...")
        subprocess.Popen(STEAM_PATH)
        print(f"{Fore.GREEN}[INFO] Ожидаем {DELAY * 2} секунд для загрузки окна логина...")
        time.sleep(DELAY * 2)

        status_label.config(text=f"Вводим логин: {account}", bootstyle="success")
        print(f"{Fore.GREEN}[INFO] Вводим логин: {account}")
        pyautogui.typewrite(account)
        pyautogui.press('tab')
        status_label.config(text="Вводим пароль...", bootstyle="success")
        print(f"{Fore.GREEN}[INFO] Вводим пароль")
        pyautogui.typewrite(password)
        pyautogui.press('enter')
        time.sleep(DELAY)

        status_label.config(text="Вводим 2FA-код...", bootstyle="success")
        print(f"{Fore.GREEN}[INFO] Вводим 2FA-код...")
        code = generate_2fa(shared_secret)
        pyautogui.typewrite(code)
        pyautogui.press('enter')
        status_label.config(text=f"Код 2FA введён: {code}", bootstyle="info")
        print(f"{Fore.CYAN}🔑 {account} | Код 2FA: {code}")
        time.sleep(DELAY * 2)

        status_label.config(text="Вход выполнен. Нажмите 'Выйти из аккаунта'.", bootstyle="success")
    except Exception as e:
        error_msg = f"Ошибка: {str(e)}"
        status_label.config(text=error_msg, bootstyle="danger")
        print(f"{Fore.RED}❌ {error_msg}")
        kill_process("steam")
