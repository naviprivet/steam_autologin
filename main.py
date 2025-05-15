import json
import os
import subprocess
import time
import pyautogui
from colorama import init, Fore, Style
from generate_2fa import generate_2fa
from config import STEAM_PATH, ACCOUNTS_DIR, ACCOUNTS_FILE, DELAY

# Инициализация colorama
init(autoreset=True)

def load_mafile(account_name):
    """Загрузка .mafile"""
    path = os.path.join(ACCOUNTS_DIR, f"{account_name}.mafile")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка при загрузке {path}: {e}{Style.RESET_ALL}")
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
            print(f"{Fore.BLUE}[DEBUG] Загружено аккаунтов из {ACCOUNTS_FILE}: {len(accounts)}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка при загрузке {ACCOUNTS_FILE}: {e}{Style.RESET_ALL}")
    return accounts

def find_mafile_accounts():
    """Поиск всех .mafile файлов в ACCOUNTS_DIR"""
    print(f"{Fore.BLUE}[DEBUG] Поиск файлов в папке: {ACCOUNTS_DIR}{Style.RESET_ALL}")
    mafiles = []
    try:
        for f in os.listdir(ACCOUNTS_DIR):
            print(f"{Fore.BLUE}[DEBUG] Обнаружен файл: {f}{Style.RESET_ALL}")
            if f.lower().endswith('.mafile'):
                mafiles.append(f)
    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка при доступе к папке {ACCOUNTS_DIR}: {e}{Style.RESET_ALL}")
        return []

    accounts = [os.path.splitext(f)[0] for f in mafiles]
    print(f"{Fore.BLUE}[DEBUG] Найдено .mafile файлов: {len(accounts)}{Style.RESET_ALL}")
    return accounts

def kill_process(name):
    """Закрытие процесса"""
    print(f"{Fore.GREEN}[INFO] Закрываем процесс: {name}.exe{Style.RESET_ALL}")
    os.system(f"taskkill /f /im {name}.exe >nul 2>&1")
    time.sleep(2)

def clear_steam_auth_data():
    """Очистка данных авторизации Steam"""
    print(f"{Fore.GREEN}[INFO] Очищаем данные авторизации Steam...{Style.RESET_ALL}")
    kill_process("steam")
    loginusers_path = os.path.join(os.path.dirname(STEAM_PATH), "config", "loginusers.vdf")
    try:
        if os.path.exists(loginusers_path):
            os.remove(loginusers_path)
            print(f"{Fore.GREEN}[INFO] Удален файл: {loginusers_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[INFO] Файл {loginusers_path} не найден{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Ошибка при удалении loginusers.vdf: {e}{Style.RESET_ALL}")
    cache_path = os.path.join(os.path.dirname(STEAM_PATH), "appcache")
    try:
        if os.path.exists(cache_path):
            for item in os.listdir(cache_path):
                item_path = os.path.join(cache_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"{Fore.GREEN}[INFO] Удален файл кэша: {item_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Ошибка при очистке кэша: {e}{Style.RESET_ALL}")

def login(account, password, shared_secret):
    """Процесс входа"""
    clear_steam_auth_data()
    kill_process("steam")

    print(f"{Fore.GREEN}[INFO] Запускаем Steam...{Style.RESET_ALL}")
    subprocess.Popen(STEAM_PATH)
    print(f"{Fore.GREEN}[INFO] Ожидаем {DELAY * 2} секунд для загрузки окна логина...{Style.RESET_ALL}")
    time.sleep(DELAY * 2)

    print(f"{Fore.GREEN}[INFO] Вводим логин: {account}{Style.RESET_ALL}")
    pyautogui.typewrite(account)
    pyautogui.press('tab')
    print(f"{Fore.GREEN}[INFO] Вводим пароль{Style.RESET_ALL}")
    pyautogui.typewrite(password)
    pyautogui.press('enter')
    time.sleep(DELAY)

    print(f"{Fore.GREEN}[INFO] Вводим 2FA-код...{Style.RESET_ALL}")
    code = generate_2fa(shared_secret)
    pyautogui.typewrite(code)
    pyautogui.press('enter')
    print(f"{Fore.CYAN}🔑 {account} | Код 2FA: {code}{Style.RESET_ALL}")
    time.sleep(DELAY * 2)

def main():
    print(f"{Fore.YELLOW}⚠️ Пожалуйста, переключите раскладку клавиатуры на английскую (US English)!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⏳ Даём 5 секунд для смены раскладки...{Style.RESET_ALL}")
    time.sleep(5)

    os.makedirs(ACCOUNTS_DIR, exist_ok=True)

    passwords = load_accounts()
    if not passwords:
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            f.write("логин1:пароль1\nлогин2:пароль2")
        print(f"{Fore.RED}📝 Создан файл {ACCOUNTS_FILE}. Заполните его!{Style.RESET_ALL}")
        return

    while True:
        mafile_accounts = find_mafile_accounts()
        if not mafile_accounts:
            print(f"{Fore.RED}❌ Не найдено ни одного .mafile файла в папке {ACCOUNTS_DIR}{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}\n📋 Найденные аккаунты:{Style.RESET_ALL}")
        for i, account in enumerate(mafile_accounts, 1):
            print(f"{Fore.YELLOW}{i}. {account}{Style.RESET_ALL}")

        try:
            choice = input(f"\nВведите номер аккаунта (или 'q' для выхода): ")
            if choice.lower() == 'q':
                print(f"{Fore.GREEN}[INFO] Выход из программы{Style.RESET_ALL}")
                break

            choice = int(choice)
            if choice < 1 or choice > len(mafile_accounts):
                print(f"{Fore.RED}❌ Неверный номер аккаунта!{Style.RESET_ALL}")
                continue

            account = mafile_accounts[choice - 1]
            print(f"{Fore.GREEN}\n🚀 Вход в аккаунт: {account}{Style.RESET_ALL}")

            password = passwords.get(account)
            if not password:
                print(f"{Fore.RED}❌ Пароль для {account} не найден в {ACCOUNTS_FILE}!{Style.RESET_ALL}")
                continue

            try:
                mafile = load_mafile(account)
                login(account, password, mafile['shared_secret'])

                input(f"{Fore.YELLOW}\n⏳ Нажмите Enter для выхода из аккаунта и возврата в меню...{Style.RESET_ALL}")
                kill_process("steam")
            except Exception as e:
                print(f"{Fore.RED}❌ Ошибка: {str(e)}{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}\n⏳ Нажмите Enter для возврата в меню...{Style.RESET_ALL}")
                kill_process("steam")

        except ValueError:
            print(f"{Fore.RED}❌ Введите корректный номер аккаунта!{Style.RESET_ALL}")
            continue

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()