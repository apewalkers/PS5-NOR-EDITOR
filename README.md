# Dony's PS5 NOR Editor

Welcome to Dony's PS5 NOR Editor! This application provides a convenient way to manage and customize your PlayStation 5 console's NOR flash memory dumps. Whether you're working with your original NOR dump or need to integrate console-specific data into a verified base, this tool streamlines the process.

---

## Overview

The PS5 NOR Editor is designed to help users safely manipulate their console's NOR data. It offers two primary workflows: directly editing your original NOR dump or extracting unique console data to merge into a pre-verified working NOR image. This ensures you can generate a clean, customized, and functional NOR image for your specific console.

---

## Features

* **Browse & Select:** Easily select your original PS5 NOR dump file.
* **Settings Adjustment:** Prepare your NOR dump by adjusting necessary settings within the application.
* **Verified Base Option:** Utilize pre-tested, verified working NOR dumps as a base for new configurations.
* **Data Harvesting:** Extract console-specific unique data from your input files.
* **Intelligent Merging:** Seamlessly merge harvested data into a verified NOR dump to create a new, clean, and customized NOR image.

---

## How to Use

There are two main approaches to using Dony's PS5 NOR Editor:

### Option 1: Using Your Original NOR Dump

This method is for users who have successfully dumped their console's original NOR.

1.  **Select Original File:** Click the "**Browse Original File**" button.
2.  **Choose Your Dump:** Navigate to and select your PS5 console's original NOR dump file. This file contains your console's unique data.
3.  **Adjust Settings:** Once loaded, you can adjust any necessary settings within the editor.
4.  **Proceed:** Follow the application's prompts to save or apply your changes.

### Option 2: Using a Verified Working NOR Dump (Alternative)

If you do not have your original NOR dump, or prefer to start with a known good base, you can use this alternative method.

1.  **Select Base File:** Click "**Browse Original File**" and select a verified working NOR dump from the `\Data\NOR Files\` directory provided with the application. These dumps have been tested and are known to be compatible across various consoles.
2.  **Harvest Your Data:** Use the "**Harvest**" function within the application. This feature will extract your console-specific data from your input files (e.g., from a partial dump or another source).
3.  **Merge & Generate:** The harvested data will then be merged into the verified NOR dump you selected. This process generates a new, clean, and fully working NOR image that is customized for your specific console.

---

## Installation

The easiest way to use Dony's PS5 NOR Editor is via the **provided executable**, which has been bundled with PyInstaller and contains all necessary dependencies. Just download and run it!

Alternatively, if you prefer to run the application from source for transparency or development, the source `.PY` file is included in the repository. To run from source:

1.  **Ensure Python is installed:** Make sure you have Python 3.x installed on your system.
2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/apewalkers/Dony-PS5-NOR-Editor.git](https://github.com/apewalkers/Dony-PS5-NOR-Editor.git)
    cd Dony-PS5-NOR-Editor
    ```
    *(Note: Replace `Dony-PS5-NOR-Editor` with your actual repository name if it's different)*

3.  **Install dependencies:**
    ```bash
    pip install Pillow
    ```
    *(`tkinter` is usually included with Python installations)*

4.  **Run the application from source:**
    ```bash
    python your_main_script_name.py
    ```
    *(Note: Replace `your_main_script_name.py` with the actual name of your Python script that contains the `tkinter` application, e.g., `main.py` or `app.py`)*

---

## Support

If you find this tool helpful and would like to support its development, you can do so via PayPal:

* **PayPal:** [https://www.paypal.me/dannyjohn08](https://www.paypal.me/dannyjohn08)

You can also contribute to the project on GitHub:

* **GitHub:** [https://github.com/apewalkers/](https://github.com/apewalkers/)

Thank you for your support!
