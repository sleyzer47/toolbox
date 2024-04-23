import customtkinter as ctk
import ipaddress
import subprocess
import re
import os
import paramiko
import threading


class AuthPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

        self.selected_username_list = None
        self.selected_password_list = None
        self.ssh_port = None

    def setup_ui(self):
        self.canvas = ctk.CTkCanvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        button_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=button_frame, anchor="nw")
        button_frame.pack(fill="y", side="left")

        buttons = [
            ("Menu", lambda: self.controller.show_frame("MenuPage")),
            ("Host", lambda: self.controller.show_frame("HostPage")),
            ("Web", lambda: self.controller.show_frame("WebPage")),
            ("Nmap", lambda: self.controller.show_frame("NmapPage")),
            ("OpenVAS", lambda: self.controller.show_frame("OpenVASPage")),
            ("Password", lambda: self.controller.show_frame("PasswordPage")),
            ("Auth", lambda: self.controller.show_frame("AuthPage"))
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)

        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.canvas, text="Auth Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in authentication page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")
        
        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.run_scans)
        generate_button.pack(fill="x", padx=150, pady=5)

        self.is_request_pending = False

    def run_scans(self):
        ip = self.entry.get()
        try:
            ipaddress.ip_address(ip)  # Validate IP
            self.ports_and_services = self.scan_with_nmap(ip)
            self.handle_services(ip)
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

    def handle_services(self, ip):
        ssh_found = False
        for port, service in self.ports_and_services.items():
            if "ssh" in service.lower():
                self.ssh_port = port
                print(self.ssh_port)
                ssh_found = True
                break
        if ssh_found:
            self.show_ssh_buttons()
        else:
            self.show_error_message("No SSH service found on this target!", self.canvas)

    def show_ssh_buttons(self):
        self.username_list_button = ctk.CTkButton(self.canvas, text="Select Username List", command=lambda: self.select_list("username"))
        self.username_list_button.pack(padx=10, pady=5)
        self.password_list_button = ctk.CTkButton(self.canvas, text="Select Password List", command=lambda: self.select_list("password"))
        self.password_list_button.pack(padx=10, pady=5)
        self.connect_button = ctk.CTkButton(self.canvas, text="Initiate SSH Connection", command=self.initiate_connection)
        self.connect_button.pack(padx=10, pady=5)

    def initiate_connection(self):
        print(self.ssh_port)
        if self.selected_username_list and self.selected_password_list and self.ssh_port:
            print("Initiating SSH connection...")
            self.test_ssh_connection(self.entry.get(), self.ssh_port)
        else:
            self.show_error_message("Please ensure both lists are selected and SSH service is found.", self.canvas)


    def select_list(self, list_type):
        folder = f"wordlist/{list_type}/"
        self.show_selection_window(folder, f"Select {list_type.capitalize()} List")

    def show_selection_window(self, path, title):
        popup = ctk.CTkToplevel(self)
        popup.geometry("400x300")
        popup.title(title)
        
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

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for username in usernames:
            for password in passwords:
                try:
                    client.connect(ip, port=port, username=username, password=password, timeout=10)
                    print(f"SSH connection successful on port {port} with {username}/{password}")
                    client.close()
                    return
                except paramiko.AuthenticationException:
                    print(f"Failed to connect via SSH on port {port} with {username}/{password}")
                except paramiko.SSHException as e:
                    print(f"SSH Error on port {port}: {e}")
                    break
                finally:
                    client.close()

        print("SSH test completed for all username/password combinations on port {port}.")


    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()






















#### OLD SSH.PY
import customtkinter as ctk
import ipaddress
import subprocess
import re
import os
import paramiko

class AuthPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Créer un canevas avec une taille spécifique
        canvas = ctk.CTkCanvas(self)
        canvas.pack(side="left", fill="both", expand=True)  # Remplir toute la page

        # Créer un cadre à l'intérieur du canevas pour organiser les boutons
        button_frame = ctk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=button_frame, anchor="nw")
        button_frame.pack(fill="y", side="left")

        button0 = ctk.CTkButton(button_frame, text="Menu", command=lambda: self.controller.show_frame("MenuPage"))
        button0.pack(fill="x", padx=10, pady=5)

        button1 = ctk.CTkButton(button_frame, text="Host", command=lambda: self.controller.show_frame("HostPage"))
        button1.pack(fill="x", padx=10, pady=5)

        button2 = ctk.CTkButton(button_frame, text="Web", command=lambda: self.controller.show_frame("WebPage"))
        button2.pack(fill="x", padx=10, pady=5)

        button3 = ctk.CTkButton(button_frame, text="Nmap", command=lambda: self.controller.show_frame("NmapPage"))
        button3.pack(fill="x", padx=10, pady=5)

        button4 = ctk.CTkButton(button_frame, text="OpenVAS", command=lambda: self.controller.show_frame("OpenVASPage"))
        button4.pack(fill="x", padx=10, pady=5)

        button5 = ctk.CTkButton(button_frame, text="Password", command=lambda: self.controller.show_frame("PasswordPage"))
        button5.pack(fill="x", padx=10, pady=5)

        button6 = ctk.CTkButton(button_frame, text="Auth", fg_color="#0d68a1")
        button6.pack(fill="x", padx=10, pady=5)

        # Ajouter le bouton "Quitter" à la fin de la liste de boutons
        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        title = ctk.CTkLabel(canvas, text="Auth Page", text_color="Black", font=(None, 20))
        title.pack(side="top", pady=10, anchor="n")

        label = ctk.CTkLabel(canvas, text="Welcome in authentification page!", text_color="Black", font=(None, 14))
        label.pack(side="top", pady=10, anchor="n")

        self.entry = ctk.CTkEntry(canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        ####ajout des radio buttons pour choisir les wordlist
        self.username_list_button = None
        self.password_list_button = None

        self.selected_username_list = None  # Initialisation à None
        self.selected_password_list = None  # Initialisation à None

        self.is_request_pending = False

        def run_scans():
            if self.is_request_pending:
                return
            ip = self.entry.get()

            try:
                ipaddress.ip_address(ip)
                self.ports_and_services = self.scan_with_nmap(ip)
                results_text = "\n".join(f"Port {port}: {service}" for port, service in self.ports_and_services.items())
                print(results_text)
                # Nouveau code pour détecter SSH et lancer le test SSH
                ssh_found = False
                for port, service in self.ports_and_services.items():
                    if "ssh" in service.lower():  # Vérifier si le service contient 'ssh'
                        self.ssh_port = port
                        self.test_ssh_connection(ip, port)  # Appeler la méthode de test SSH
                        ssh_found = True


                        # Ajouter des boutons pour sélectionner les listes d'utilisateurs et de mots de passe
                        self.username_list_button = ctk.CTkButton(canvas, text="Select Username List", command=self.select_username_list)
                        self.username_list_button.pack(fill="x", padx=10, pady=5)

                        self.password_list_button = ctk.CTkButton(canvas, text="Select Password List", command=self.select_password_list)
                        self.password_list_button.pack(fill="x", padx=10, pady=5)

                if not ssh_found:
                    self.show_error_message("No SSH on this target!", canvas)
                #self.show_error_message("No SSH on this target!", canvas)

            except ValueError:
                self.show_error_message("Incorrect/unreachable IP!", canvas)
                return

            self.is_request_pending = True
            self.after(3000, self.reset_request_state)

        generate_button = ctk.CTkButton(canvas, text="Generate Report", command=run_scans)
        generate_button.pack(fill="x", padx=150, pady=5)

    def scan_with_nmap(self, ip):
        print("Nmap started:")
        try:
            # Lancement de Nmap avec les options pour récupérer les services
            command = ["nmap", "-sV", ip]
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout

            # Parsing du résultat pour construire le dictionnaire
            self.ports_and_services = {}
            lines = output.split("\n")
            for line in lines:
                if "/tcp" in line and "open" in line:
                    match = re.search(r"(\d+)/tcp\s+open\s+([\w\s]+)", line)
                    if match:
                        port = int(match.group(1))
                        service = match.group(2).strip()
                        self.ports_and_services[port] = service
            return self.ports_and_services
        except Exception as e:
            print(f"Failed to run Nmap: {e}")
            return {}

    def test_ssh_connection (self, ip, port):
        print("SSH Found")
        if self.selected_username_list and self.selected_password_list:
            username_path = os.path.join("wordlist/username/", self.selected_username_list)
            password_path = os.path.join("wordlist/password/", self.selected_password_list)

            with open(username_path, 'r') as file:
                usernames = file.read().splitlines()

            with open(password_path, 'r') as file:
                passwords = file.read().splitlines()

            # Créer une instance de SSHClient
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Essayer toutes les combinaisons de noms d'utilisateur et de mots de passe
            for username in usernames:
                for password in passwords:
                    try:
                        client.connect(ip, port=port, username=username, password=password, timeout=10)
                        print(f"SSH connection successful on port {port} with {username}/{password}")
                        client.close()
                        return  # Arrêter après la première connexion réussie
                    except paramiko.AuthenticationException:
                        print(f"Failed to connect via SSH on port {port} with {username}/{password}")
                    except paramiko.SSHException as e:
                        print(f"SSH Error on port {port}: {e}")
                        break
                    finally:
                        client.close()

            print("SSH test completed for all username/password combinations on port {port}.")


    
    def select_username_list(self):
        self.show_selection_window("wordlist/username/", "Select Username List")

    def select_password_list(self):
        self.show_selection_window("wordlist/password/", "Select Password List")


    def show_selection_window(self, relative_path, title):
        base_path = os.path.dirname(__file__)  # Obtenez le dossier où le script est exécuté
        path = os.path.abspath(os.path.join(base_path, '..', relative_path))  # Remontez d'un niveau puis accédez à 'wordlist'
        print(f"Looking for files in: {path}")  # Déboguez pour voir le chemin complet

        popup = ctk.CTkToplevel(self)
        popup.geometry("400x300")
        popup.title(title)
        
        frame = ctk.CTkFrame(popup)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        var = ctk.StringVar(value="")
        for file in sorted(os.listdir(path)):
            radio_button = ctk.CTkRadioButton(frame, text=file, variable=var, value=file)
            radio_button.pack(anchor="w", padx=20, pady=5)

        confirm_button = ctk.CTkButton(popup, text="Confirm", command=lambda: self.set_list_choice(var.get(), path))
        confirm_button.pack(pady=20)

    def set_list_choice(self, choice, path):
        if "/username/" in path:
            self.selected_username_list = choice
        elif "/password/" in path:
            self.selected_password_list = choice
        print(f"Selected {choice} from {path}")
        # Vérifiez que les deux listes et le port sont sélectionnés
        if self.selected_username_list and self.selected_password_list and hasattr(self, 'ssh_port'):
            self.test_ssh_connection(self.entry.get(), self.ssh_port)

        

    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
