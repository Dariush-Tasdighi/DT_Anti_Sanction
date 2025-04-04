"""
DT Anti Sanction
"""

import os
import json
import ctypes
import subprocess

# from colorama import Fore

data: list = []
interface_name: str = "Wi-Fi"
# interface_name: str = "Ethernet"


def check_user_is_admin() -> bool:
    """
    Check User Is Admin Function

    Checks if the current user is an administrator.

    :return: True if the user is an administrator, False otherwise.
    """

    is_user_admin: bool = False

    try:
        is_user_admin = os.getuid() == 0

    except AttributeError:
        is_user_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return is_user_admin


def load_data() -> None:
    """
    Load Data Function
    """

    global data

    with open(file="data.json", mode="rt", encoding="utf-8") as file:
        data = json.load(fp=file)


def display_menu() -> None:
    """
    Display Menu Function
    """

    print("Welcome to DT Anti Sanction - Version 1.2")
    # print(f"{Fore.BLUE}Welcome to DT Anti Sanction - Version 1.0{Fore.RESET}")

    if check_user_is_admin() == False:
        print("You must run this program as an administrator!")
        # print(f"{Fore.YELLOW}You must run this program as an administrator!{Fore.RESET}")
        print()
        quit()

    print()

    for index in range(len(data)):
        if data[index]["need_space"]:
            print()

        if index < 9:
            print(f"{index + 1}.  {data[index]["dns_name"]}")
        else:
            print(f"{index + 1}. {data[index]["dns_name"]}")

    print()
    print(f"{len(data) + 1}. Reset")
    print(f"{len(data) + 2}. Display Current DNS")
    print()


def display_current_dns(interface_name: str) -> None:
    """
    Display Current DNS Function

    Display the current DNS servers for a specified network interface.

    :param interface_name: Name of the network interface
    """

    try:
        command: str = f'netsh interface ip show dns name="{interface_name}"'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            # print(f"{Fore.RED}Error: {result.stderr}{Fore.RESET}")
            return

        print(result.stdout)

    except Exception as ex:
        print(f"Error: {ex}")
        # print(f"{Fore.RED}Error: {ex}{Fore.RESET}")


def reset_dns(interface_name: str) -> None:
    """
    Reset DNS Function

    Resets the DNS settings to obtain DNS servers automatically.

    :param interface_name: Name of the network interface
    """

    try:
        command: str = f'netsh interface ip set dns name="{interface_name}" dhcp'
        os.system(command=command)
        print(f"DNS settings for {interface_name} reset to automatic.")
        flush_dns()

    except Exception as ex:
        print(f"Error: {ex}")
        # print(f"{Fore.RED}Error: {ex}{Fore.RESET}")


def flush_dns() -> None:
    """
    Flush DNS Function
    """

    try:
        command: str = "ipconfig /flushdns"
        os.system(command=command)
        print("DNS Flushed.")

    except Exception as ex:
        print(f"Error: {ex}")
        # print(f"{Fore.RED}Error: {ex}{Fore.RESET}")


def change_dns(
    interface_name: str, primary_dns: str, secondary_dns: str = None
) -> None:
    """
    Change DNS Function

    Changes the DNS servers for a specified network interface.

    :param interface_name: Name of the network interface
    :param primary_dns: Primary DNS server address (e.g., "8.8.8.8")
    :param secondary_dns: Secondary DNS server address (optional, e.g., "8.8.4.4")
    """

    try:
        command: str = (
            f'netsh interface ip set dns name="{interface_name}" static {primary_dns}'
        )
        os.system(command=command)
        print(f"Primary DNS for {interface_name} set to {primary_dns}")

        if secondary_dns:
            command: str = (
                f'netsh interface ip add dns name="{interface_name}" {secondary_dns} index=2'
            )
            os.system(command=command)
            print(f"Secondary DNS for {interface_name} set to {secondary_dns}")

        flush_dns()

    except Exception as ex:
        print(f"Error: {ex}")
        # print(f"{Fore.RED}Error: {ex}{Fore.RESET}")


def display_interfaces() -> None:
    """
    Display Interfaces Function
    """
    # netsh interface show interface


def main() -> None:
    """
    Main Function
    """

    os.system(command="cls")

    load_data()
    display_menu()

    try:
        choice: str = input(f"Select an option [1..{len(data) + 2}]: ")
        print()

        if not choice.isdigit():
            print("Invalid input! Please enter just a number...")
            print()
            quit()

        choice: int = int(choice)

        if choice < 1 or choice > len(data) + 2:
            print(
                f"Invalid input! Please enter a number between 1 and {len(data) + 2}..."
            )
            print()
            quit()

        if choice == len(data) + 1:
            reset_dns(interface_name=interface_name)
            display_current_dns(interface_name=interface_name)

        elif choice == len(data) + 2:
            display_current_dns(interface_name=interface_name)

        else:
            dns_name: str = data[choice - 1]["dns_name"]
            primary_dns: str = data[choice - 1]["primary_dns"]
            secondary_dns: str = data[choice - 1]["secondary_dns"]
            print(f"{dns_name} - primary: {primary_dns} - Secondary: {secondary_dns}")

            change_dns(
                primary_dns=primary_dns,
                secondary_dns=secondary_dns,
                interface_name=interface_name,
            )

            display_current_dns(interface_name=interface_name)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
