"""
DT Anti Sanction
"""

import os
import json
import ctypes
import subprocess

# from colorama import Fore

VERSION: str = "1.4"

data: list = []
# interface_name: str = "Wi-Fi" # No longer a fixed global
# interface_name: str = "Ethernet" # No longer a fixed global


def check_user_is_admin() -> bool:
    """
    Check user is admin function.

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
    Load data function.
    """

    global data

    with open(file="data.json", mode="rt", encoding="utf-8") as file:
        data = json.load(fp=file)


def display_current_dns(interface_name: str) -> None:
    """
    Display current DNS function.

    Display the current DNS servers for a specified network interface.

    :param interface_name: Name of the network interface
    """
    try:
        command: str = f'netsh interface ip show dns name="{interface_name}"'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return

        print(result.stdout)

    except Exception as error:
        print(f"Error: {error}")


def reset_dns(interface_name: str) -> None:
    """
    Reset DNS function.

    Resets the DNS settings to obtain DNS servers automatically.

    :param interface_name: Name of the network interface
    """
    try:
        command: str = f'netsh interface ip set dns name="{interface_name}" dhcp'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"DNS settings for {interface_name} reset to automatic.")
            flush_dns() # Call flush_dns, which is also updated
        else:
            error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
            print(f"Error resetting DNS for {interface_name}: {error_message}")

    except Exception as error:
        print(f"Error during DNS reset operation: {error}")


def flush_dns() -> None:
    """
    Flush DNS function.

    """
    try:
        command: str = "ipconfig /flushdns"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("DNS Flushed.")
        else:
            error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
            print(f"Error flushing DNS: {error_message}")

    except Exception as error:
        print(f"Error during DNS flush operation: {error}")


def change_dns(
    interface_name: str,
    primary_dns: str,
    secondary_dns: str = None,
) -> None:
    """
    Change DNS function.

    Changes the DNS servers for a specified network interface.

    :param interface_name: Name of the network interface
    :param primary_dns: Primary DNS server address (e.g., "8.8.8.8")
    :param secondary_dns: Secondary DNS server address (optional, e.g., "8.8.4.4")
    """
    all_successful = True
    try:
        # Set Primary DNS
        command_primary: str = (
            f'netsh interface ip set dns name="{interface_name}" static {primary_dns}'
        )
        result_primary = subprocess.run(command_primary, shell=True, capture_output=True, text=True, check=False)
        if result_primary.returncode == 0:
            print(f"Primary DNS for {interface_name} set to {primary_dns}")
        else:
            all_successful = False
            error_message = result_primary.stderr.strip() if result_primary.stderr else result_primary.stdout.strip()
            print(f"Error setting primary DNS for {interface_name} to {primary_dns}: {error_message}")

        # Set Secondary DNS only if primary was successful and secondary_dns is provided
        if secondary_dns and all_successful:
            command_secondary: str = (
                f'netsh interface ip add dns name="{interface_name}" {secondary_dns} index=2'
            )
            result_secondary = subprocess.run(command_secondary, shell=True, capture_output=True, text=True, check=False)
            if result_secondary.returncode == 0:
                print(f"Secondary DNS for {interface_name} set to {secondary_dns}")
            else:
                all_successful = False
                error_message = result_secondary.stderr.strip() if result_secondary.stderr else result_secondary.stdout.strip()
                print(f"Error setting secondary DNS for {interface_name} to {secondary_dns}: {error_message}")

        if all_successful:
             flush_dns()

    except Exception as error:
        print(f"Error during DNS change operation: {error}")


def display_interfaces() -> list[str]:
    """
    Display available network interfaces and return them as a list.
    """
    print("Available network interfaces:\\n")
    interfaces_found: list[str] = []

    try:
        command: str = "netsh interface show interface"
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True  # Consistent with other 'netsh' calls in the script
            # No check=True, will handle result.returncode manually
        )

        if result.returncode != 0:
            error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
            print(f"Error listing interfaces: {error_message}")
            return []

        lines = result.stdout.strip().splitlines()
        
        header_found = False
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or "---" in line_stripped: # Skip empty lines and the separator line
                if "Interface Name" in line_stripped and "---" not in line_stripped :
                     header_found = True # Handles cases where header might be only thing on a line then separator
                continue

            if not header_found:
                if "Interface Name" in line_stripped: # Found the header line
                    header_found = True
                continue # Skip lines until header is processed

            # At this point, header_found is True, and we are past the header or on a data line.
            # Parse the actual interface data lines.
            parts = line_stripped.split(None, 3) # Split by whitespace, max 3 splits (gives 4 parts)
            if len(parts) == 4:
                interface_name = parts[3].strip() # The 4th part is the interface name
                if interface_name: 
                    interfaces_found.append(interface_name)

        if not interfaces_found:
            print("No network interfaces found or could not parse them.")
            return []

        # Displaying the found interfaces, matching author's menu style for DNS list
        for i, name in enumerate(interfaces_found):
            if (i + 1) < 10:
                 print(f"{i + 1}.  {name}")
            else:
                 print(f"{i + 1}. {name}")
        print() # Extra newline after menu

    except FileNotFoundError:
        print(f"Error: 'netsh' command not found. Is it in your system's PATH?")
    except Exception as e:
        print(f"An unexpected error occurred while listing interfaces: {e}")
    
    return interfaces_found


def handle_dns_management() -> None:
    """
    Handles the DNS list management menu and operations.
    """
    # Note: Assumes 'data' list is already loaded in main()
    os.system(command="cls") # Clear screen for the sub-menu

    while True: # Loop for the management menu
        print("--- DNS Management Menu ---\n")
        print("1. View all DNS entries")
        print("2. Add a new DNS entry")
        print("3. Edit an existing DNS entry")
        print("4. Delete a DNS entry")
        print("5. Back to main menu")
        print() # Newline before input prompt

        try:
            choice_str = input("Select a management option [1-5]: ")
            print() # Newline after input

            if not choice_str.isdigit():
                print("Invalid input! Please enter a number.")
                print() # Newline for spacing
                continue

            choice = int(choice_str)

            if choice == 1: # View all DNS entries
                print("--- All DNS Entries ---\n")
                if not data: # Check if data list is empty
                    print("No DNS entries found in data.json.")
                else:
                    for i, entry in enumerate(data): # Iterate through the global 'data' list
                        secondary = entry.get("secondary_dns", "Not set")
                        url = entry.get("url", "Not set")
                        # Consistent formatting with main menu numbering if possible, though maybe not necessary for this view
                        # Let's just list them clearly
                        print(f"Entry {i + 1}:")
                        print(f"  Name: {entry.get('dns_name', 'N/A')}") # Use .get for robustness
                        print(f"  Primary: {entry.get('primary_dns', 'N/A')}")
                        print(f"  Secondary: {secondary}")
                        print(f"  URL: {url}")
                        print() # Space between entries
                
                # Pause before returning to management menu
                input("Press Enter to continue...") 
                os.system(command="cls") # Clear after viewing

            elif choice == 2: # Add a new DNS entry
                print("--- Add New DNS Entry ---\n") # Keep header print
                add_dns_entry() # Call the new function
                # No input("Press Enter...") here, add_dns_entry handles flow
                os.system(command="cls") # Clear after adding and return to management menu

            elif choice == 3: # Edit an existing DNS entry
                print("--- Edit DNS Entry ---\n") # Keep header print
                edit_dns_entry() # Call the edit function
                input("Press Enter to continue...") # Pause after edit
                os.system(command="cls") # Clear and return to management menu

            elif choice == 4: # Delete a DNS entry
                print("--- Delete DNS Entry ---\n") # Keep header print
                delete_dns_entry() # Call the delete function
                input("Press Enter to continue...") # Pause after delete
                os.system(command="cls") # Clear and return to management menu

            elif choice == 5: # Back to main menu
                print("Returning to main menu.\n")
                return # Exit the management menu loop

            else:
                print("Invalid selection. Please choose a number between 1 and 5.")
                print()

        except ValueError: # Catches int() conversion error
            print("Invalid input. Please enter a numerical choice.")
            print()
        except KeyboardInterrupt:
            print("\\nOperation cancelled. Returning to management menu.")
            print() # Newline after message
            os.system(command="cls") # Clear and show menu again after Ctrl+C
            continue # Continue the management menu loop


def save_data(data_list: list) -> None:
    """
    Saves the current data list back to data.json.
    
    :param data_list: The list of DNS entries to save.
    """
    try:
        # Use indent=4 for readability, matching original file style if possible.
        with open(file="data.json", mode="wt", encoding="utf-8") as file:
            json.dump(data_list, file, indent=4)
        # print("Data saved successfully.") # Optional success message - keep silent to match author style
    except Exception as e:
        print(f"Error saving data to data.json: {e}")
        # print(f"{Fore.RED}Error saving data...{Fore.RESET}") # Keep silent to match author style, just print error


def add_dns_entry() -> None:
    """
    Prompts user for details and adds a new DNS entry to the data list.
    """
    global data # Need to modify the global list

    print("Enter details for the new DNS entry:")
    
    # Get DNS Name
    while True:
        dns_name = input("  DNS Name (e.g., 'My New DNS'): ").strip()
        if dns_name:
            break
        else:
            print("    DNS Name cannot be empty. Please try again.")

    # Get Primary DNS
    while True:
        primary_dns = input("  Primary DNS IP Address (e.g., '1.1.1.1'): ").strip()
        if primary_dns:
            # Basic check if it looks like an IP address (contains at least one dot and numbers)
            # More robust validation could be added here if needed.
            if '.' in primary_dns and any(char.isdigit() for char in primary_dns):
                break
            else:
                 print("    Invalid format. Please enter a valid IP address.")
        else:
            print("    Primary DNS IP Address cannot be empty. Please try again.")

    # Get Secondary DNS (Optional)
    secondary_dns = input("  Secondary DNS IP Address (Optional): ").strip()

    # Get URL (Optional)
    url = input("  URL (Optional): ").strip()

    # Create the new entry dictionary
    new_entry = {
        "need_space": False, # Defaulting to False for new entries
        "dns_name": dns_name,
        "primary_dns": primary_dns,
    }
    if secondary_dns: # Only add secondary if provided and not empty
        new_entry["secondary_dns"] = secondary_dns
    if url: # Only add url if provided and not empty
        new_entry["url"] = url

    # Add the new entry to the global data list
    data.append(new_entry)

    # Save the updated data list back to data.json
    save_data(data) # Pass the updated data list

    print("\nNew DNS entry added successfully.") # Use \n for newline before message
    # No extra print() after this, consistent with save_data's silent success


def edit_dns_entry() -> None:
    """
    Prompts user to select and edit an existing DNS entry.
    """
    global data # Need to modify the global list

    if not data:
        print("\nNo DNS entries available to edit.\n")
        return # Exit function, handle_dns_management will pause/cls

    print("--- Edit DNS Entry ---\n")
    print("Select the entry number you want to edit:\n")

    # Display the current entries with numbers
    for i, entry in enumerate(data):
        print(f"{i + 1}. {entry.get('dns_name', 'N/A')} ({entry.get('primary_dns', 'N/A')})")
    print() # Newline after the list

    # Get user choice for which entry to edit
    while True:
        try:
            choice_str = input(f"Enter entry number to edit [1-{len(data)}]: ").strip()
            print() # Newline after input

            if not choice_str.isdigit():
                print("  Invalid input. Please enter a number.")
                print() # Newline for spacing
                continue

            choice = int(choice_str)
            if 1 <= choice <= len(data):
                entry_index = choice - 1 # Convert to 0-indexed list index
                break
            else:
                print(f"  Invalid number. Please choose a number between 1 and {len(data)}.")
                print() # Newline for spacing
        except ValueError: # Should be caught by isdigit check, but good practice
             print("  Invalid input. Please enter a number.")
             print() # Newline for spacing

    # Get new values from user, allowing blank input to keep current value
    entry_to_edit = data[entry_index]
    print(f"\nEditing entry {choice}: {entry_to_edit.get('dns_name', 'N/A')}")
    print("Press Enter to keep the current value.")
    print() # Newline before prompts

    # Edit DNS Name
    current_name = entry_to_edit.get('dns_name', '')
    new_name = input(f"  DNS Name (Current: '{current_name}'): ").strip()
    if new_name: # Only update if user provided input and it's not empty
        entry_to_edit['dns_name'] = new_name
    elif not current_name: # If user entered blank AND current name is empty, maybe prompt again?
         # For simplicity, we allow empty name if they explicitly enter blank, 
         # but the add function requires a name. Let's enforce non-empty name on edit too if user provides input.
         # If user enters blank and current name is NOT empty, we keep current.
         # If user enters non-blank, we use it.
         pass # If new_name is empty, we check if current_name exists later.

    # Edit Primary DNS
    current_primary = entry_to_edit.get('primary_dns', '')
    while True: # Loop until valid primary DNS is entered or kept
        new_primary = input(f"  Primary DNS IP Address (Current: '{current_primary}'): ").strip()
        if new_primary: # User entered something
             # Basic check if it looks like an IP address (contains at least one dot and numbers)
             if '.' in new_primary and any(char.isdigit() for char in new_primary):
                 entry_to_edit['primary_dns'] = new_primary
                 break
             else:
                 print("    Invalid format. Please enter a valid IP address.")
        elif current_primary: # User pressed enter, keep current value if it exists
             break # Keep the existing primary_dns
        else: # User pressed enter, but there is no current primary (shouldn't happen if adding requires primary)
             print("    Primary DNS IP Address cannot be empty. Please provide a value.")
             print() # Newline for spacing

    # Edit Secondary DNS (Optional)
    current_secondary = entry_to_edit.get('secondary_dns', '')
    new_secondary = input(f"  Secondary DNS IP Address (Current: '{current_secondary}'): ").strip()
    # If user enters a value, update it. If they enter blank, remove secondary_dns.
    if new_secondary: # If user provided a value
        entry_to_edit['secondary_dns'] = new_secondary
    elif 'secondary_dns' in entry_to_edit: # User entered blank, and secondary exists
        del entry_to_edit['secondary_dns'] # Remove the key if set to empty by user

    # Edit URL (Optional)
    current_url = entry_to_edit.get('url', '')
    new_url = input(f"  URL (Current: '{current_url}'): ").strip()
     # If user enters a value, update it. If they enter blank, remove url.
    if new_url: # If user provided a value
        entry_to_edit['url'] = new_url
    elif 'url' in entry_to_edit: # User entered blank, and url exists
         del entry_to_edit['url'] # Remove the key if set to empty by user

    # Ensure DNS Name is not empty after edits, if it was changed
    if not entry_to_edit.get('dns_name'):
         # This case happens if user edited the name to be empty. 
         # It contradicts add_dns_entry. Let's print a warning or disallow.
         # For simplicity, if they made it empty, maybe set a default or quit?
         # Let's just print a warning for now.
         print("\nWarning: DNS Name is now empty. Consider editing it again.")

    # Save the updated data list
    save_data(data) # Pass the updated data list

    print("\nDNS entry updated successfully.\n") # Use \n for newline before/after message
    # No input() pause here, handle_dns_management will pause


def delete_dns_entry() -> None:
    """
    Prompts user to select and delete a DNS entry.
    """
    global data # Need to modify the global list

    if not data:
        print("\nNo DNS entries available to delete.\n")
        return # Exit function, handle_dns_management will pause/cls

    print("--- Delete DNS Entry ---\n")
    print("Select the entry number you want to delete:\n")

    # Display the current entries with numbers
    for i, entry in enumerate(data):
        print(f"{i + 1}. {entry.get('dns_name', 'N/A')} ({entry.get('primary_dns', 'N/A')})")
    print() # Newline after the list

    # Get user choice for which entry to delete
    while True:
        try:
            choice_str = input(f"Enter entry number to delete [1-{len(data)}]: ").strip()
            print() # Newline after input

            if not choice_str.isdigit():
                print("  Invalid input. Please enter a number.")
                print() # Newline for spacing
                continue

            choice = int(choice_str)
            if 1 <= choice <= len(data):
                entry_index = choice - 1 # Convert to 0-indexed list index
                break
            else:
                print(f"  Invalid number. Please choose a number between 1 and {len(data)}.")
                print() # Newline for spacing
        except ValueError: # Should be caught by isdigit check, but good practice
             print("  Invalid input. Please enter a number.")
             print() # Newline for spacing

    # Get confirmation
    entry_to_delete = data[entry_index]
    confirm_name = entry_to_delete.get('dns_name', 'this entry')
    confirm = input(f"Are you sure you want to delete '{confirm_name}'? (yes/no): ").strip().lower()
    print() # Newline after input

    if confirm == 'yes':
        try:
            del data[entry_index] # Remove the entry from the list
            save_data(data) # Save the updated list
            print(f"'{confirm_name}' deleted successfully.\n")
             # No input() pause here, handle_dns_management will pause/cls
        except Exception as e:
             print(f"Error deleting entry: {e}\n") # Print error message
    else:
        print("Deletion cancelled.\n")
         # No input() pause here, handle_dns_management will pause/cls


def main() -> None:
    """
    Main function.
    """
    os.system(command="cls") # Clear screen at the start

    # --- Admin Check ---
    if not check_user_is_admin():
        print("You must run this program as an administrator!")
        print()
        quit()

    # --- Get Network Interface ---
    available_interfaces = display_interfaces() 
    
    if not available_interfaces:
        print("No network interfaces were found or an error occurred during detection. Exiting.")
        print()
        quit()

    selected_interface_name: str = ""
    if len(available_interfaces) == 1:
        selected_interface_name = available_interfaces[0]
        print(f"Automatically selected the only available interface: {selected_interface_name}\\\\n")
    else:
        while True:
            try:
                interface_choice_str = input(f"Select an interface to configure [1..{len(available_interfaces)}]: ")
                print() 

                if not interface_choice_str.isdigit():
                    print("Invalid input! Please enter a number.")
                    print() 
                    continue
                
                interface_choice = int(interface_choice_str)
                if 1 <= interface_choice <= len(available_interfaces):
                    selected_interface_name = available_interfaces[interface_choice - 1]
                    print(f"Configuring for interface: {selected_interface_name}\\\\n")
                    break
                else:
                    print(f"Invalid selection. Please choose a number between 1 and {len(available_interfaces)}.")
                    print() 
            except ValueError: 
                print("Invalid input. Please enter a numerical choice.")
                print() 

    # --- Load Data ---
    load_data() # Load DNS data from data.json

    # --- Main Application Loop ---
    # This loop will keep the program running until the user chooses to exit.
    while True:
        # Clear screen before displaying menu in each iteration
        os.system(command="cls")

        print(f"Welcome to DT Anti Sanction - Version {VERSION}") # Welcome message
        print() # Newline for spacing

        print(f"DNS options for interface '{selected_interface_name}':")
        for index_dns in range(len(data)): # Using index_dns to be distinct
            if data[index_dns]["need_space"]:
                print() # Print extra newline if specified in data.json

            # Consistent formatting for DNS options (space padding for single-digit numbers)
            if index_dns < 9:
                print(f"{index_dns + 1}.  {data[index_dns]['dns_name']}")
            else:
                print(f"{index_dns + 1}. {data[index_dns]['dns_name']}")
        print() # Newline after listing DNS servers

        # Display management and action options with updated numbering
        next_option_number = len(data) + 1
        print(f"{next_option_number}. Manage DNS List")
        next_option_number += 1
        print(f"{next_option_number}. Reset DNS for '{selected_interface_name}' to automatic")
        next_option_number += 1
        print(f"{next_option_number}. Display Current DNS for '{selected_interface_name}'")
        next_option_number += 1
        print(f"{next_option_number}. Exit") # New Exit option
        print() # Final newline before input prompt

        # --- Handle User Choice ---
        try:
            # Update the valid range to include the new Exit option
            max_choice = len(data) + 4 # +1 for Manage, +1 for Reset, +1 for Display, +1 for Exit
            choice_str: str = input(f"Select an option for '{selected_interface_name}' [1..{max_choice}]: ")
            print() # Newline after input, consistent with original style

            # Store the choice for later checking if we need to pause
            current_choice = choice_str # Store string input first

            if not current_choice.isdigit():
                print("Invalid input! Please enter just a number...")
                print() # Newline for spacing
                # Continue loop to show menu again
                input("Press Enter to continue...") # Pause to read message
                continue # Go back to the start of the while loop

            choice: int = int(current_choice) # Convert validated string to int

            if not (1 <= choice <= max_choice): # Check if choice is in valid range
                print(
                    f"Invalid input! Please enter a number between 1 and {max_choice}..."
                )
                print() # Newline for spacing
                # Continue loop to show menu again
                input("Press Enter to continue...") # Pause to read message
                continue # Go back to the start of the while loop

            # Perform action based on choice
            # Adjust the conditional checks based on new numbering
            if choice == len(data) + 2: # Reset DNS (Adjusted number)
                reset_dns(interface_name=selected_interface_name)
                print() # Add a newline for better readability before showing current DNS
                display_current_dns(interface_name=selected_interface_name)
            elif choice == len(data) + 3: # Display Current DNS (Adjusted number)
                display_current_dns(interface_name=selected_interface_name)
            elif choice == len(data) + 1: # Manage DNS List (Number remains the same relative to DNS options)
                handle_dns_management() # This function has its own loop/menu
                # After returning from handle_dns_management, the while loop continues,
                # redisplaying the main menu. No pause needed as handle_dns_management handles its own flow.
                continue # Skip the pause below and immediately redraw main menu
            elif choice == len(data) + 4: # Exit (New option)
                 print("Exiting program. Goodbye!")
                 print() # Final newline for clean exit
                 break # Exit the while loop, ending the main function and script

            else: # Original DNS selection cases (1 to len(data) - Change DNS)
                dns_entry = data[choice - 1] # User choice is 1-indexed
                dns_name: str = dns_entry["dns_name"]
                primary_dns: str = dns_entry["primary_dns"]
                secondary_dns: str | None = dns_entry.get("secondary_dns") # Use .get() for safety
                dns_url: str | None = dns_entry.get("url") # Get the URL, also safely

                print(f"Attempting to set DNS for '{selected_interface_name}' to: {dns_name}")
                print(f"Primary: {primary_dns}")
                if secondary_dns:
                    print(f"Secondary: {secondary_dns}")
                else:
                    print("Secondary: Not set")
                if dns_url:
                    print(f"URL: {dns_url}")
                print() # Newline before executing change

                change_dns(
                    interface_name=selected_interface_name,
                    primary_dns=primary_dns,
                    secondary_dns=secondary_dns,
                )
                print() # Add a newline for better readability before showing current DNS
                display_current_dns(interface_name=selected_interface_name)

            # Pause before showing the menu again (unless it was the management menu or Exit)
            # The management menu handles its own flow, and Exit breaks the loop.
            # Also pause after invalid input (handled by continue). So pause for set/reset/display.
            if choice != len(data) + 1 and choice != len(data) + 4:
                 input("Press Enter to return to the main menu...")

        except KeyboardInterrupt:
            print("\\nOperation cancelled by user. Exiting.") # More user-friendly message
            print() # Final newline for clean exit
            break # Exit the while loop

        except Exception as e: # Catch any other unexpected error in this block
            print(f"An unexpected error occurred in main operation: {e}")
            print() # Newline after error message
            # Pause to read the error message before redrawing menu
            input("Press Enter to continue...")
            continue # Go back to the start of the while loop


if __name__ == "__main__":
    main()
