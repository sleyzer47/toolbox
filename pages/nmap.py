import customtkinter as ctk
import subprocess
import ipaddress
import re
import json

class NmapPage(ctk.CTkFrame):
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
            ("Map", lambda: self.controller.show_frame("MapPage")),
            ("Password", lambda: self.controller.show_frame("PasswordPage")),
            ("SSH", lambda: self.controller.show_frame("SSHPage"))
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)

        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.canvas, text="Nmap Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in nmap page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")

        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        def generate_report():
            if self.is_request_pending:
                return
            ip = self.entry.get()

            try:
                ipaddress.ip_address(ip)
                report = self.run_nmap_scan(ip)
                print(json.dumps(report, indent=4))
            except ValueError:
                self.show_error_message("Incorrect/unreachable IP!", self.canvas)
                return

            self.is_request_pending = True
            self.after(3000, self.reset_request_state)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=generate_report)
        generate_button.pack(fill="x", padx=150, pady=5)

    def run_nmap_scan(self, ip):
        try:
            command = f"nmap -sV --script=vulners {ip} -p 0-10000"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return self.parse_nmap_output(result.stdout)
        except Exception as e:
            print(f"Failed to run Nmap: {e}")
            return {}

    def parse_nmap_output(self, output):
        service_pattern = re.compile(r'(\d+)/tcp\s+open\s+(\S+)\s+(.*)')
        cve_pattern = re.compile(r'(CVE-\d{4}-\d{4,5})\s+(\d+\.\d+)')
        services = []
        current_service = {}

        for line in output.split('\n'):
            service_match = service_pattern.search(line)
            if service_match:
                if current_service:  # Save the previous service if exists
                    services.append(current_service)
                port, service, version = service_match.groups()
                current_service = {'service': service, 'port': port, 'version': version.strip(), 'CVE': []}
            elif current_service:  # Only search for CVEs if we are within a service block
                cve_match = cve_pattern.findall(line)
                for cve, cvss in cve_match:
                    if float(cvss) >= 7.0:
                        current_service['CVE'].append(cve)

        if current_service:  # Don't forget to add the last service if any
            services.append(current_service)

        return services

    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()