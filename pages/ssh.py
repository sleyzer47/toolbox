import customtkinter as ctk
import ipaddress
import subprocess
import re
import os
import paramiko
import threading
import time
import json


class SSHPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.username_list_button = None
        self.password_list_button = None
        self.connect_button = None
        self.setup_ui()

        self.is_request_pending = False
        self.selected_username_list = None
        self.selected_password_list = None
        self.ssh_port = None
        self.success_flag = threading.Event()
        self.threads = []

    def setup_ui(self):
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        button_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=button_frame, anchor="nw")
        button_frame.pack(fill="y", side="left")

        buttons = [
            ("Menu", lambda: self.controller.show_frame("MenuPage")),
            ("Network", lambda: self.controller.show_frame("NetworkPage")),
            ("Web", lambda: self.controller.show_frame("WebPage")),
            ("Nmap", lambda: self.controller.show_frame("NmapPage")),
            ("Map", lambda: self.controller.show_frame("MapPage")),
            ("Password", lambda: self.controller.show_frame("PasswordPage")),
            ("SSH", lambda: self.controller.show_frame("SSHPage")),
            ("PDF", lambda: self.controller.show_frame("PDFPage"))
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)

        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.canvas, text="SSH Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in SSH page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")
        
        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.run_scans)
        generate_button.pack(fill="x", padx=150, pady=5)

    def run_scans(self):
        ip = self.entry.get()
        try:
            ipaddress.ip_address(ip)
            self.ports_and_services = self.scan_with_nmap(ip)
            self.handle_services()
        except ValueError:
            self.show_error_message("Incorrect/unreachable IP!", self.canvas)

    def scan_with_nmap(self, ip):
        command = ["nmap", "-sV", ip]
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        
        ports_services = {}
        for line in output.split("\n"):
            match = re.search(r"(\d+)/tcp\s+open\s+([\w\s]+)", line)
            if match:
                port = int(match.group(1))
                service = match.group(2).strip()
                ports_services[port] = service
        return ports_services

    def handle_services(self):
        ssh_found = False
        for port, service in self.ports_and_services.items():
            if "ssh" in service.lower():
                self.ssh_port = port
                ssh_found = True
                break
        if ssh_found:
            self.show_ssh_buttons()
        else:
            self.show_error_message("No SSH service found on this target!", self.canvas)

    def show_ssh_buttons(self):
        if not self.username_list_button:
            self.username_list_button = ctk.CTkButton(self.canvas, text="Select Username List", command=lambda: self.select_list("username"))
            self.username_list_button.pack(padx=10, pady=5)
        
        if not self.password_list_button:
            self.password_list_button = ctk.CTkButton(self.canvas, text="Select Password List", command=lambda: self.select_list("password"))
            self.password_list_button.pack(padx=10, pady=5)
        
        if not self.connect_button:
            self.connect_button = ctk.CTkButton(self.canvas, text="Initiate SSH Connection", command=self.initiate_connection)
            self.connect_button.pack(padx=10, pady=5)

    def initiate_connection(self):
        if self.selected_username_list and self.selected_password_list and self.ssh_port:
            if self.is_request_pending:
                print("request blocked in initiate connection")
                return
            self.is_request_pending = True
            print("Initiating SSH connection...")
            threading.Thread(target=self.test_ssh_connection, args=(self.entry.get(), self.ssh_port)).start()
        else:
            self.show_error_message("Please ensure both lists are selected and SSH service is found.", self.canvas)

    def select_list(self, list_type):
        folder = f"wordlist/{list_type}/"
        self.show_selection_window(folder, f"Select {list_type.capitalize()} List")

    def show_selection_window(self, path, title):
        popup = ctk.CTkToplevel(self)
        popup.geometry("400x300")
        popup.title(title)

        # Make the popup stay on top
        popup.transient(self)
        popup.grab_set()
        
        frame = ctk.CTkFrame(popup)
        frame.pack(pady=20, padx=20, expand=True)

        var = ctk.StringVar(value="")
        for file in sorted(os.listdir(path)):
            radio_button = ctk.CTkRadioButton(frame, text=file, variable=var, value=file)
            radio_button.pack(anchor="w", padx=20, pady=5)

        confirm_button = ctk.CTkButton(popup, text="Confirm", command=lambda: self.set_list_choice(var.get(), path, popup))
        confirm_button.pack(pady=20)

    def set_list_choice(self, choice, path, popup):
        if "username" in path:
            self.selected_username_list = choice
        elif "password" in path:
            self.selected_password_list = choice
        print(f"Selected {choice} from {path}")
        popup.destroy()

    def test_ssh_connection(self, ip, port):
        print(f"Attempting to connect to SSH on {ip}:{port}")
        if not (self.selected_username_list and self.selected_password_list):
            print("Username or password list not selected.")
            return

        username_path = os.path.join("wordlist/username/", self.selected_username_list)
        password_path = os.path.join("wordlist/password/", self.selected_password_list)

        with open(username_path, 'r') as file:
            usernames = file.read().splitlines()

        with open(password_path, 'r') as file:
            passwords = file.read().splitlines()

        threads = []
        semaphore = threading.Semaphore(5)

        for username in usernames:
            for password in passwords:
                if self.success_flag.is_set():
                    break
                thread = threading.Thread(target=self.try_login, args=(ip, port, username, password, semaphore))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()


        if self.success_flag.is_set():
            result_details = f"SSH connection successful with {self.successful_credentials}"
            print("Successful authentication detected, stopping all other attempts.")
        else:
            result_details = "No successful SSH connection found."
            print(result_details)
        self.update_json(ip, result_details)

        self.is_request_pending = False
        self.success_flag.clear()

    def try_login(self, ip, port, username, password, semaphore):
        if self.success_flag.is_set():
            return

        with semaphore:
            if self.success_flag.is_set():
                return

            local_client = paramiko.SSHClient()
            local_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                local_client.connect(ip, port=port, username=username, password=password, timeout=10)
                print(f"SSH connection successful on port {port} with {username}/{password}")
                self.success_flag.set()
                self.successful_credentials = f"{username}/{password}"
                return
            except paramiko.AuthenticationException:
                print(f"Failed to connect via SSH on port {port} with {username}/{password}")
            except paramiko.SSHException as e:
                print(f"SSH Error on port {port}: {e}")
            finally:
                local_client.close()



    def update_json(self, ip, result_details):
        json_path = os.path.join(os.getcwd(), 'result.json')
        data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r') as file:
                data = json.load(file)

        data[ip] = data.get(ip, {})
        data[ip]['ssh_brute_force'] = {
            "username_list": self.selected_username_list,
            "password_list": self.selected_password_list,
            "port": self.ssh_port,
            "result": result_details
        }

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)

    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
