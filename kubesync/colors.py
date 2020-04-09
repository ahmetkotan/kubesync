RESET = "\033[0m"
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"


def print_green(message) -> None:
    print(f"{GREEN}[+] {message}{RESET}")


def print_red(message) -> None:
    print(f"{RED}[-] {message}{RESET}")


def print_yellow(message) -> None:
    print(f"{YELLOW}[*] {message}{RESET}")
