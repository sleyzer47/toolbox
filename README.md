# Pentest Toolbox

## Introduction

Welcome to the Pentest Toolbox, a project developed as part of my Master's program in Cybersecurity.

This tool is designed to automate professional penetration testing.

It consolidates various scan results into a well-structured PDF report, making it easier for security professionals to review and address vulnerabilities.

The application has been developed in **python and runs on Windows**, making it easy to access, for easier access. The application can be used without any knowledge of cybersecurity.

However, interpretation of the results may be complicated without such knowledge.

## Features

### 1. Nmap Scan
The tool integrates with Nmap to perform network scanning and gather information about open ports, services, and versions.
It also collects any associated CVEs (Common Vulnerabilities and Exposures) using the vulners script.

### 2. Web Scan
The tool can process results from web application scanners, specifically SQLMap and Nikto, providing detailed insights into potential vulnerabilities in web applications.

- **SQLMap**: SQLMap is an open-source penetration testing tool that automates the process of detecting and exploiting SQL injection flaws and taking over database servers. By integrating SQLMap, this toolbox can identify SQL injection vulnerabilities and help in securing web applications against such attacks.
  - **Information**: The SQLMap clone project from [GitHub - SQLMap](https://github.com/sqlmapproject/sqlmap).
  
- **Nikto**: Nikto is an open-source web server scanner which performs comprehensive tests against web servers for multiple items, including over 6700 potentially dangerous files/CGIs, checks for outdated versions, and version-specific problems. Integrating Nikto allows this toolbox to identify various vulnerabilities in web servers and applications.
  - **Information**: The Nikto clone project from [GitHub - Nikto](https://github.com/sullo/nikto).

### 3. SSH Brute Force
This feature captures and reports the results of SSH brute force attacks, including the ports tested, username lists, password lists, and the outcomes of the tests.

### 4. Network Testing
The toolbox will use Scapy to include various network tests to identify vulnerabilities and potential security issues within the network infrastructure. This functionality is separated into two types of scans:
- **SYN Flood Attack**: Using Scapy, the toolbox will send a large number of SYN packets to all ports that are up. However, **you'll need to use an external tool (like Wireshark) to see the impact on the target.**
- **Malformed Packet**:  The toolbox will send packets with different FLAGs (like URG, S, etc) with the aim of finding security holes or particular configurations on certain ports. 

### 5. Password Generation and Testing
The tool includes two features related to passwords:
- **Password Generation**: Generates secure passwords according to desired criteria (length, special characters, etc).
- **Password Strength Testing**: Assigns a score out of 5 to the password entered by the user. The score is defined according to criteria such as length, absence of numbers, etc.

### 6. Mapping
The tool offers local network mapping functions, using a scan of the hosts. It will list all hosts that are up, along with their hostname and MAC address where possible. Then draw a map to visually represent the network structure and identify critical points.

### 7. PDF Report Generation
All the data collected is compiled in a PDF report, including the results of every scan previously performed.


## Prerequisites

- **Python**: Ensure you have Python (version 3.10 or higher) installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **pip**: Ensure you have pip installed for managing Python packages.
- **Nmap**: Download and install Nmap from [nmap.org](https://nmap.org/download.html).
- **Perl**: Some tools may require Perl (for Nikto). You can download it from [perl.org](https://www.perl.org/get.html).

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/sleyzer47/toolbox.git

    cd toolbox/

2. **Install the required packages**:
    ```sh
    pip install -r requirements.txt

## Project Structure:

    toolbox/
    ├── main.py
    ├── report.pdf (if created)
    ├── requirements.txt
    ├── result.json
    ├── pages/
    │   ├── pdf.py
    │   ├── ssh.py
    │   ├── start.py
    │   ├── web.py
    │   ├── map.py
    │   ├── menu.py
    │   ├── network.py
    │   ├── nmap.py
    │   └── password.py
    ├── nikto/ (clone from GitHub)
    ├── sqlmap-dev/ (clone from GitHub)
    └── wordlists/
        ├── username/
        └── password/


## Usage

1. **Run the Application**: To start the application, execute the `main.py` script. 
    This script serves as the entry point for the toolbox.
   ```sh
   python main.py

2. **Navigate the Menu**: When you start the application, you'll be taken to a start page, then by clicking on the "Start" button, you'll access the menu. 
    This menu allows you to navigate to different functionalities of the toolbox. 

## How do the features work?

**Nmap Scan**:

- **Access the Nmap Page**: From the main menu, navigate to the "Nmap" page.
- **Enter Target Information**: Input the target IP address that you want to scan.
- **Run the Scan**: Start the Nmap scan. The results will be displayed in terminal and saved for inclusion in the PDF report.


**Web Scan**:

- **Access the Web Scan Page**: From the main menu, navigate to the "Web" page.
- **Enter Target Information**: Input the target URL or IP address.
- **Run the Scans**: Both SQLMap and Nikto scans will be executed.
    - **SQLMap**: Used to detect and exploit SQL injection vulnerabilities.
    - **Nikto**: Performs comprehensive tests against web servers, checking for potentially dangerous files, outdated versions, and version-specific problems.
- **View the Results**: The results from both scans will be saved for inclusion in the PDF report.


**Network Tests**:

- **Access the Network Page**: From the main menu, navigate to the "Network" page.
- **Enter Target Information**: Enter the gateway IP address of the target network or another network.
- **Run the Tests**: Both SYN Flood and Malformed Packet tests will be executed.
    - **SYN Flood**: Tests the target's resilience against SYN flood attacks.
    - **Malformed Packet**: Sends malformed packets to the target to test for vulnerabilities.
- **View the Results**: The results from both tests will be saved for inclusion in the PDF report.


**Mapping the Network**:

- **Access the Map Page**: From the main menu, navigate to the "Map" page.
- **Enter Target Information**: Input the network IP address **and the subnet mask**.
- **Generate Map**: Create a visual representation of the network structure. The map will help identify critical points and potential vulnerabilities.


**Generating and Testing Passwords**:

- **Access the Password Page**: From the main menu, navigate to the "Password" page.
    - **Generate Password**: Use the password generation function according to user-selectable criteria.
    - **Test Password Strength**: Enter a password to test its strength an the tool will provide a score.


**SSH Brute Force**:

- **Access the SSH Page**: From the main menu, navigate to the "SSH" page.
- **Enter Target Information**: Input the target IP address and port.
- **Enter Credentials Lists**: Provide the username and password lists to be used for the brute force attack.
- **Run the Attack**: Execute the brute force attack. The results will be displayed and saved for inclusion in the PDF report.


**Generating the PDF Report**:

- **Access the PDF Page**: From the main menu, navigate to the "PDF" page.
- **Generate Report**: Click on the button to generate the PDF report. The report will compile all collected data into a structured document including the results of all previously performed scans.
