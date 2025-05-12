# 📄 DT Anti Sanction

Simplify Windows DNS Management to Bypass Restrictions.

### Version 1.4

Welcome to the **DT Anti Sanction** repository! This project implements a command-line utility for Windows to quickly change network DNS settings, likely intended to help users bypass internet restrictions.

Key components of the project include:
- **DNS Operations:** Functions to set, reset, and display DNS configurations using Windows system commands.
- **Interface Selection:** Logic to detect and allow the user to choose a specific network adapter to modify.
- **Data Management:** Functions to load, add, edit, and delete DNS server entries stored in a JSON file.

This tool provides a user-friendly alternative to manually navigating complex Windows network settings.

---

## ✨ Overview

This project is a self-contained Python script designed to streamline the process of changing DNS server settings on a Windows operating system. By interacting with system commands (`netsh`, `ipconfig`) via Python's `subprocess` module, it automates tasks that would otherwise require manual steps through the Windows network control panel.

The primary goal is to offer a quick way to switch between different DNS providers, potentially to overcome regional or network-level content restrictions.

Key features include:

*   **Dynamic Interface Selection:** Upon launch, the script identifies available network adapters and prompts the user to select which one they wish to configure.
*   **Predefined DNS List:** Loads a list of popular DNS server configurations from a `data.json` file, presenting them as easy-to-select options.
*   **DNS Management Menu:** Provides a dedicated sub-menu to view, add, edit, or delete entries within the `data.json` list.
*   **One-Click Actions:** Offers direct options to apply a selected DNS configuration, reset the chosen interface to obtain DNS automatically via DHCP, or display the interface's current DNS settings.

The project is written in Python and relies on standard Windows command-line utilities.

---

## 🗂️ File Structure

The project has a simple and flat file structure:

```
.
├── .git/              # Git version control directory
├── .gitignore         # Specifies intentionally untracked files
├── app.py             # The main executable Python script containing all program logic
├── data.json          # Stores the list of predefined and user-managed DNS server entries
├── DT_Anti_Sanction.webp # Project image used in the README
└── README.md          # Project overview, features, requirements, and instructions
```

---

## 🚀 Features

Detailed breakdown of the project's capabilities:

*   **Dynamic Network Interface Selection:** The script identifies active network interfaces on the Windows system (e.g., Wi-Fi, Ethernet, VPN adapters) using `netsh interface show interface`, displays them as a numbered list, and allows the user to choose which interface the DNS operations should apply to. If only one interface is found, it is automatically selected.

*   **Predefined and Customizable DNS List:** DNS server options (including names, primary and secondary IPs, and associated URLs) are loaded from the `data.json` file. This list is presented as the primary menu for quick selection.

*   **Integrated DNS Management Menu:** Selecting the 'Manage DNS List' option from the main menu leads to a sub-menu with the following functionalities:
    1.  **View all DNS entries:** Displays the details (Name, Primary, Secondary, URL) of all entries currently loaded from `data.json`.
    2.  **Add a new DNS entry:** Prompts the user for the Name, Primary IP, optional Secondary IP, and optional URL for a new DNS server, then adds it to the list and saves to `data.json`.
    3.  **Edit an existing DNS entry:** Allows the user to select an entry by number and modify its Name, Primary IP, optional Secondary IP, and optional URL. Changes are saved to `data.json`.
    4.  **Delete a DNS entry:** Presents the list of entries for deletion, asks for confirmation, removes the selected entry, and saves to `data.json`.

*   **DNS Configuration Operations:** Utilizes `netsh interface ip` commands via `subprocess` to manage DNS settings:
    *   **Set Static DNS:** Applies the Primary and (if provided) Secondary DNS IP addresses from a selected entry to the chosen network interface.
    *   **Reset DNS:** Configures the chosen network interface to automatically obtain DNS server addresses via DHCP.
    *   **Display Current DNS:** Shows the DNS servers currently configured for the selected network interface.

*   **DNS Cache Flushing:** Automatically runs `ipconfig /flushdns` after setting or resetting DNS to ensure the changes take effect immediately.

*   **Administrator Requirement:** The script includes a check to ensure it is being run with elevated (administrator) privileges, which is necessary for modifying network configurations.

---

## 📋 Requirements

1.  **Software:**
    *   Python 3.11 or higher. The script likely works with earlier Python 3 versions >= 3.6 due to f-string usage.
    *   Windows Operating System.
    *   Administrator privileges to run the script.
2.  **Dependencies:** 
    *   No external Python packages are required. The script uses only modules from the Python standard library (`os`, `json`, `ctypes`, `subprocess`).
    *   Dependency management is not required as there are no external packages.
3.  **Environment Setup:**
    *   No specific environment variables or configuration files (beyond `data.json`) are required.

---

## 💻 Installation & Launch Instructions

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```
2.  **Install Dependencies**
    This project has no external Python dependencies, so no installation step is needed.

3.  **Launch the Application/Script**
    Open a Command Prompt or PowerShell window **as Administrator**, navigate to the project directory, and run the script:
    ```bash
    python app.py
    ```

---

## 📝 Usage Guide

1.  Run the script with administrator privileges (as shown in Installation & Launch).
2.  Upon launch, the script will list available network interfaces. Select the number corresponding to the interface you wish to configure (e.g., Wi-Fi, Ethernet).
3.  The main menu will appear, listing available DNS options (loaded from `data.json`), a 'Manage DNS List' option, 'Reset DNS', 'Display Current DNS', and 'Exit'.
4.  Select a number corresponding to your desired action.
    *   Selecting a DNS number (1 to `len(data)`) will attempt to apply that DNS configuration to the chosen interface.
    *   Selecting 'Manage DNS List' will enter the DNS management sub-menu.
    *   Selecting 'Reset DNS' will configure the interface to use DHCP for DNS.
    *   Selecting 'Display Current DNS' will show the current DNS settings for the interface.
    *   Selecting 'Exit' will close the program.
5.  Within the 'Manage DNS List' menu, follow the prompts to View, Add, Edit, or Delete DNS entries in `data.json`.
6.  After performing most actions, press Enter to return to the main menu.
7.  Select 'Exit' from the main menu to terminate the program.

---

## ⚙️ Technical Implementation Details

### Core Functionality
- Uses `subprocess` to execute Windows specific command-line tools (`netsh`, `ipconfig`) for network configuration.
- Parses command output to extract information (like current DNS or interface names).
- Employs `json` for loading and saving the DNS entry data to `data.json`.
- Includes a check using `ctypes` for verifying administrator privileges.

### Data Handling
- DNS entries are stored as a list of dictionaries in `data.json`.
- The script loads this data into a global Python list (`data`) at the start of `main`.
- Add, Edit, and Delete operations modify this list in memory and then write the entire updated list back to `data.json` using `json.dump` with indentation for readability.

### User Interaction
- Implements a text-based command-line interface with numbered menus and input prompts.
- Uses `os.system('cls')` to clear the console for cleaner menu navigation.
- Includes basic input validation (checking for numbers in menu selections).
- Catches `KeyboardInterrupt` for graceful exit on Ctrl+C.

---

## 📈 Current Status & Future Plans

### Current Status
- The project appears functional for its core purpose: dynamic interface selection, DNS application/reset/display, and comprehensive DNS list management via the console.
- Basic error handling is implemented for subprocess calls and user input.

### Future Enhancements
- Error handling could be made more specific and robust for various `netsh` and `ipconfig` failure cases.
- More advanced validation for IP addresses in add/edit functions.
- A graphical user interface (GUI) could make the tool more accessible to non-technical users.
- Packaging the script into a standalone executable for easier distribution (e.g., using PyInstaller).
- Implementing the ability to open the URL associated with a DNS entry in a web browser.
