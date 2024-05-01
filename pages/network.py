import customtkinter as ctk
from scapy.all import sr1, IP, TCP, send
import ipaddress
import subprocess
import re

class NetworkPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_request_pending = False
        self.setup_ui()

    def setup_ui(self):
        self.canvas = ctk.CTkCanvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        button_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=button_frame, anchor="nw")
        button_frame.pack(fill="y", side="left")

        buttons = [
            ("Menu", lambda: self.controller.show_frame("MenuPage")),
            ("Network", lambda: self.controller.show_frame("NetworkPage")),
            ("Web", lambda: self.controller.show_frame("WebPage")),
            ("Nmap", lambda: self.controller.show_frame("NmapPage")),
            ("Nessus", lambda: self.controller.show_frame("NessusPage")),
            ("Password", lambda: self.controller.show_frame("PasswordPage")),
            ("SSH", lambda: self.controller.show_frame("SSHPage"))
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)

        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.canvas, text="Network Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in network page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")

        
        # Créer une zone de texte
        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        def run_scans():
            if self.is_request_pending:
                return
            ip = self.entry.get()

            try:
                ip_ok = ipaddress.ip_address(ip)
                self.ports_and_services = self.scan_with_nmap(ip)
                results_text = "\n".join(f"Port {port}: {service}" for port, service in self.ports_and_services.items())
                print(results_text)
                self.syn_flood_test(ip)
                self.malformed_packet_test(ip)

            except ValueError:
                self.show_error_message("Incorrect/unreachable IP!", self.canvas)
                return

            self.is_request_pending = True
            self.after(3000, self.reset_request_state)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=run_scans)
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

    def syn_flood_test(self, ip):
        print("Starting SYN flood test...")
        for port in self.ports_and_services.keys(): # Ports à tester
            for _ in range(0, 100): # Nombre de paquets SYN à envoyer
                send(IP(dst=ip)/TCP(dport=port, flags="S"), verbose=0)
        print("SYN flood test completed.")

    def malformed_packet_test(self, ip):
        print("Running malformed packet tests...")
        flags_to_test = ['FPU', 'U', 'R', 'P']  # Flags malformés
        for port in self.ports_and_services.keys():
            for flag in flags_to_test:
                packet = IP(dst=ip) / TCP(dport=port, flags=flag)  # Unusual flag
                response = sr1(packet, timeout=1, verbose=0)
                if response:
                    print(f"Port {port} Flags {flag}: Response: {response.summary()}")
                else:
                    print(f"Port {port} Flags {flag}: No response")
        print("Malformed packet test finished")
        
    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
