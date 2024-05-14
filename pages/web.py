import customtkinter as ctk
from scapy.all import sr1, IP, TCP, send
import ipaddress
import subprocess
import re
import json
import os
import time

class WebPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_request_pending = False
        
        self.setup_ui()

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

        ctk.CTkLabel(self.canvas, text="Web Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in Web page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")
        
        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.run_scans)
        generate_button.pack(fill="x", padx=150, pady=5)
       
    def run_scans(self):
        if self.is_request_pending:
            return
        ip = self.entry.get()

        try:
            ipaddress.ip_address(ip)
            self.ports_and_services = self.scan_with_nmap(ip)
            self.handle_services(ip)
        except ValueError:
            self.show_error_message("Incorrect/unreachable IP!", self.canvas)
            return

        self.is_request_pending = True
        self.after(3000, self.reset_request_state)

    def scan_with_nmap(self, ip):
        command = ["nmap", ip]
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
        web_ports = {}
        http_services = {'http', 'apache', 'nginx', 'http-alt', 'http-proxy', 'https', 'apache2', 'apache-ssl'}
        for port, service in self.ports_and_services.items():
            if any(http_service in service.lower() for http_service in http_services):
                web_ports[port] = service
        if web_ports:
            for port, service in web_ports.items():
                sqlmap_output = self.test_sql_injection(ip, port)
                nikto_output = self.run_nikto_scan(ip, port)
                self.collect_and_update_results(ip, port, service, sqlmap_output, nikto_output)
        else:
            print("No web server found!")
            self.show_error_message("No web server found on this target!", self.canvas)


    def parse_nikto_output(self, output):
        lines = output.split('\n')
        cve_patterns = re.compile(r'CVE-\d{4}-\d{4,7}')
        cve_lines = [cve_patterns.search(line).group(0) for line in lines if 'CVE' in line and cve_patterns.search(line)]
        return cve_lines
    
    def parse_sqlmap_output(self, output):
        critical_lines = []
        for line in output.split('\n'):
            if "[CRITICAL]" in line:
                part = line.split("[CRITICAL] ", 1)[-1]
                if part:
                    critical_lines.append(part)

        return ' '.join(critical_lines)

    def test_sql_injection(self, ip, port):
        print("Starting sqlmap on port: " + str(port))
        path_to_sqlmap = "./sqlmap-dev/sqlmap.py"
        url = f"http://{ip}:{port}"
        command = f"python {path_to_sqlmap} -u {url} --batch --level=5 --risk=3 --threads=10 --tamper=space2comment --random-agent -v 0"
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            detected = "injection not detected" not in result.stdout
            output = self.parse_sqlmap_output(result.stdout)
            return {"detected": detected, "start_time": start_time, "end_time": end_time, "output": output}
        except Exception as e:
            print(f"Error running sqlmap: {str(e)}")
            return {"detected": False, "start_time": start_time, "end_time": end_time, "output": str(e)}

    def run_nikto_scan(self, ip, port):
        print("Starting nikto on port: " + str(port))
        path_to_nikto = "./nikto/program/nikto.pl"
        command = ["perl", path_to_nikto, "-h", ip, "-p", str(port)]
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            result = subprocess.run(command, text=True, capture_output=True, timeout=300)
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            output = self.parse_nikto_output(result.stdout)
            return {"start_time": start_time, "end_time": end_time, "CVE": output}
        except subprocess.TimeoutExpired:
            return {"start_time": start_time, "end_time": end_time, "output": ["Nikto scan timed out after 3 minutes on port: " + str(port)]}
        except Exception as e:
            return {"start_time": start_time, "end_time": end_time, "output": [str(e)]}

    def update_json(self, ip, port_details):
        json_path = os.path.join(os.getcwd(), 'result.json')
        data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r') as file:
                data = json.load(file)

        if ip not in data:
            data[ip] = {}
        data[ip].setdefault("web_scans", [])
        data[ip]["web_scans"].append(port_details)

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)

    def collect_and_update_results(self, ip, port, service, sqlmap_output, nikto_output):
        port_details = {
            "port": port,
            "service": service,
            "sqlmap_results": sqlmap_output,
            "nikto_results": nikto_output
        }
        self.update_json(ip, port_details)

    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
