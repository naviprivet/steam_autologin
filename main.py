import os
import threading
import tkinter as tk
from tkinter import ttk

import pyautogui
from ttkbootstrap import Window

from config import ACCOUNTS_DIR, ACCOUNTS_FILE
from helpers import load_mafile, load_accounts, find_mafile_accounts, kill_process, login


def create_gui():
    # Создаём окно с тёмной темой
    root = Window(title="Steam Account Login", themename="darkly")
    root.geometry("450x400")
    root.resizable(False, False)
    root.attributes('-alpha', 0.98)  # Лёгкая полупрозрачность для Apple-стиля

    # Создаём папку для .mafile
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)

    # Загружаем пароли
    passwords = load_accounts()
    if not passwords:
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            f.write("логин1:пароль1\nлогин2:пароль2")
        ttk.Label(root, text=f"Создан файл {ACCOUNTS_FILE}. Заполните его!", bootstyle="danger").pack(pady=10)
        root.after(3000, root.destroy)  # Закрываем через 3 секунды
        return

    # Загружаем аккаунты
    mafile_accounts = find_mafile_accounts()
    if not mafile_accounts:
        ttk.Label(root, text=f"Не найдено .mafile файлов в {ACCOUNTS_DIR}", bootstyle="danger").pack(pady=10)
        root.after(3000, root.destroy)
        return

    # Контейнер для элементов
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill="both")

    # Заголовок
    ttk.Label(frame, text="Steam Account Login", font=("Helvetica", 18, "bold"), style="light.TLabel").pack(
        pady=(0, 20))

    # Выбор аккаунта
    ttk.Label(frame, text="Выберите аккаунт:", font=("Helvetica", 12)).pack(anchor="w")
    account_var = tk.StringVar()
    account_combobox = ttk.Combobox(frame, textvariable=account_var, values=mafile_accounts, state="readonly",
                                    font=("Helvetica", 11))
    account_combobox.pack(fill="x", pady=(5, 15))
    if mafile_accounts:
        account_combobox.set(mafile_accounts[0])

    # Статус
    status_label = ttk.Label(frame, text="Ожидание выбора аккаунта...", font=("Helvetica", 10), wraplength=400,
                             style="default.TLabel")
    status_label.pack(pady=(0, 20))

    # Кнопки
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill="x")

    def start_login():
        account = account_var.get()
        if not account:
            status_label.config(text="Выберите аккаунт!", bootstyle="danger")
            return
        password = passwords.get(account)
        if not password:
            status_label.config(text=f"Пароль для {account} не найден в {ACCOUNTS_FILE}!", bootstyle="danger")
            return
        try:
            mafile = load_mafile(account)
            status_label.config(text=f"Вход в аккаунт: {account}...", bootstyle="success")
            threading.Thread(target=login, args=(account, password, mafile['shared_secret'], status_label, root),
                             daemon=True).start()
        except Exception as e:
            status_label.config(text=f"Ошибка: {str(e)}", bootstyle="danger")
            print(f"{Fore.RED}❌ Ошибка: {str(e)}")

    ttk.Button(button_frame, text="Войти", command=start_login, style="primary.Outline.TButton").pack(side="left",
                                                                                                      padx=5)

    def logout():
        kill_process("steam")
        status_label.config(text="Ожидание выбора аккаунта...", style="default.TLabel")

    ttk.Button(button_frame, text="Выйти из аккаунта", command=logout, style="secondary.Outline.TButton").pack(
        side="left", padx=5)

    def refresh_accounts():
        nonlocal mafile_accounts
        mafile_accounts = find_mafile_accounts()
        account_combobox['values'] = mafile_accounts
        if mafile_accounts:
            account_combobox.set(mafile_accounts[0])
        else:
            status_label.config(text="Не найдено .mafile файлов!", bootstyle="danger")
            account_combobox.set("")

    ttk.Button(button_frame, text="Обновить", command=refresh_accounts, style="info.Outline.TButton").pack(side="left",
                                                                                                           padx=5)

    # Кнопка выхода
    ttk.Button(frame, text="Закрыть", command=lambda: [kill_process("steam"), root.destroy()],
               style="danger.Outline.TButton").pack(pady=(20, 0))

    # Анимация статуса (мигание при ожидании)
    def blink_status():
        if "Ожидаем" in status_label.cget("text") or "Запускаем" in status_label.cget("text"):
            current_color = status_label.cget("foreground")
            new_color = "#00ff00" if current_color != "#00ff00" else "#80ff80"
            status_label.config(foreground=new_color)
        root.after(500, blink_status)

    root.after(500, blink_status)

    # Напоминание о раскладке
    ttk.Label(frame, text="Убедитесь, что раскладка клавиатуры — английская (US English)", font=("Helvetica", 9),
              style="warning.TLabel").pack(pady=(20, 0))

    root.mainloop()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    create_gui()
