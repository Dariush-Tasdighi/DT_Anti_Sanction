"""
DT Anti Sanction
"""

import os
import json
import ctypes
import subprocess
from typing import (
    Final,
    Optional,
)

VERSION: Final[str] = "1.4"
INTERFACE_NAME: Final[str] = "Wi-Fi"  # "Ethernet"


def check_user_is_admin() -> bool:
    """
    Check user is admin function.

    Checks if the current user is an administrator.

    :return: True if the user is an administrator, False otherwise.
    """

    is_user_admin: bool = False

    # Check if the operating system is Unix-like
    if os.name == "posix":
        try:
            is_user_admin = os.getuid() == 0

        except AttributeError:
            pass
    else:
        is_user_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return is_user_admin


def load_data() -> None:
    """
    Load data function.
    """

    global data

    with open(file="data.json", mode="rt", encoding="utf-8") as file:
        data = json.load(fp=file)


def display_menu() -> None:
    """
    Display menu function.
    """

    print(f"Welcome to DT Anti Sanction - Version {VERSION}")

    if check_user_is_admin() == False:
        error_message: str = "You must run this program as an administrator"
        raise Exception(error_message)

    print()

    for index in range(len(data)):
        if data[index]["need_space"]:
            print()

        print(f"{(index + 1):>2}. {data[index]["dns_name"]}")

    print()
    print(f"{len(data) + 1}. Reset")
    print(f"{len(data) + 2}. Display Current DNS")
    print()
    print(f"{len(data) + 3}. Exit")
    print()


def display_current_dns(interface_name: str) -> None:
    """
    Display current DNS function.

    Display the current DNS servers for a specified network interface.

    :param interface_name: Name of the network interface
    """

    try:
        command: str = f'netsh interface ip show dns name="{interface_name}"'

        result = subprocess.run(
            text=True,
            check=True,
            shell=True,
            args=command,
            capture_output=True,
        )

        if result.returncode != 0:
            print(f"[-] {result.stderr}!")
            return

        print(result.stdout.strip())

    except Exception as exception:
        print(f"[-] {exception}!")


def reset_dns(interface_name: str) -> None:
    """
    Reset DNS function.

    Resets the DNS settings to obtain DNS servers automatically.

    :param interface_name: Name of the network interface
    """

    try:
        command: str = f'netsh interface ip set dns name="{interface_name}" dhcp'

        subprocess.run(
            text=True,
            check=True,
            shell=True,
            args=command,
            capture_output=False,
        )

        print(f"DNS settings for {interface_name} reset to automatic.")
        flush_dns()

    except Exception as exception:
        print(f"[-] Error: {exception}!")


def flush_dns() -> None:
    """
    Flush DNS function.
    """

    try:
        command: str = "ipconfig /flushdns"

        subprocess.run(
            text=True,
            check=True,
            shell=True,
            args=command,
            capture_output=False,
        )

        print("DNS Flushed.")

    except Exception as exception:
        print(f"[-] Error: {exception}!")


def change_dns(
    interface_name: str,
    primary_dns: str,
    secondary_dns: Optional[str] = None,
) -> None:
    """
    Change DNS function.

    Changes the DNS servers for a specified network interface.

    :param interface_name: Name of the network interface
    :param primary_dns: Primary DNS server address (e.g., "8.8.8.8")
    :param secondary_dns: Secondary DNS server address (optional, e.g., "8.8.4.4")
    """

    try:
        command: str = (
            f'netsh interface ip set dns name="{interface_name}" static {primary_dns}'
        )

        subprocess.run(
            text=True,
            check=True,
            shell=True,
            args=command,
            capture_output=False,
        )

        print(f"Primary DNS for {interface_name} set to {primary_dns}")

        if secondary_dns:
            command: str = (
                f'netsh interface ip add dns name="{interface_name}" {secondary_dns} index=2'
            )

            subprocess.run(
                text=True,
                check=True,
                shell=True,
                args=command,
                capture_output=False,
            )

            print(f"Secondary DNS for {interface_name} set to {secondary_dns}")

        flush_dns()

    except Exception as exception:
        print(f"[-] Error: {exception}!")


def display_interfaces() -> None:
    """
    Display interfaces.
    """

    # netsh interface show interface


def main() -> None:
    """
    The main of program
    """

    if os.name == "nt":
        subprocess.run(args=["cls"], shell=True)
    else:
        subprocess.run(args=["clear"], shell=True)

    load_data()
    display_menu()

    prompt: str = f"Select an option [1..{len(data) + 2}]: "
    choice: str = input(prompt)
    print()

    if not choice.isdigit():
        error_message: str = "Invalid input! Please enter just a number"
        raise ValueError(error_message)

    choice_int: int = int(choice)
    max_choice: int = len(data) + 3

    if choice_int < 1 or choice_int > max_choice:
        error_message: str = (
            f"Invalid input! Please enter a number between 1 and {max_choice}"
        )
        raise ValueError(error_message)

    if choice_int == len(data) + 1:
        reset_dns(interface_name=INTERFACE_NAME)
        display_current_dns(interface_name=INTERFACE_NAME)

    elif choice_int == len(data) + 2:
        display_current_dns(interface_name=INTERFACE_NAME)

    elif choice_int == len(data) + 3:
        print("Goodbye!")

    else:
        dns_name: str = data[choice_int - 1]["dns_name"]
        primary_dns: str = data[choice_int - 1]["primary_dns"]
        secondary_dns: str = data[choice_int - 1]["secondary_dns"]
        print(f"{dns_name} - primary: {primary_dns} - Secondary: {secondary_dns}")

        change_dns(
            primary_dns=primary_dns,
            secondary_dns=secondary_dns,
            interface_name=INTERFACE_NAME,
        )

        display_current_dns(interface_name=INTERFACE_NAME)


if __name__ == "__main__":
    try:
        data: list = []

        main()

    except KeyboardInterrupt:
        print()

    except Exception as exception:
        print(f"[-] {exception}!")

    finally:
        print()
