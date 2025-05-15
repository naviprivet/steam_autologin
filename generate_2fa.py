import base64
import hmac
import struct
import time
from datetime import datetime
from colorama import init, Fore

# Инициализация colorama
init(autoreset=True)

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
        print(f"{Fore.BLUE}[DEBUG] Timestamp: {timestamp} ({datetime.fromtimestamp(timestamp)})")

        # Формирование временного буфера (время / 30 секунд)
        time_buffer = struct.pack('>Q', timestamp // 30)

        # Вычисление HMAC-SHA1
        hmac_hash = hmac.new(key, time_buffer, 'sha1').digest()
        print(f"{Fore.BLUE}[DEBUG] HMAC hash: {hmac_hash.hex()}")

        # Получение офсета
        offset = hmac_hash[-1] & 0x0F
        print(f"{Fore.BLUE}[DEBUG] Offset: {offset}")

        code = struct.unpack('>I', hmac_hash[offset:offset+4])[0] & 0x7FFFFFFF
        print(f"{Fore.BLUE}[DEBUG] Raw code: {code}")

        # Таблица символов Steam Guard (26 символов: 2-9, B-Y, без A, I, O, U, Z)
        steam_chars = '23456789BCDFGHJKMNPQRTVWXY'

        # Генерация 5-значного кода
        final_code = ''
        for _ in range(5):
            code, remainder = divmod(code, len(steam_chars))
            final_code += steam_chars[remainder]

        print(f"{Fore.BLUE}[DEBUG] Final 2FA code: {final_code}")
        return final_code

    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка в generate_2fa: {e}")
        raise