import customtkinter as ctk
import matplotlib.pyplot as plt
import networkx as nx
import subprocess
import re

class MapPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
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

        ctk.CTkLabel(self.canvas, text="Map Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in Map page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")
        
        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP range")
        self.entry.pack(padx=200, pady=5)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Map", command=self.run_scans)
        generate_button.pack(fill="x", padx=150, pady=5)

    def run_scans(self):
        self.network_range = self.entry.get()
        self.network_scan(self.network_range)

    def network_scan(self, network_range):
        # Scan pour identifier tous les hôtes actifs et récupérer les informations basiques
        command = f"nmap -sn {self.network_range} --system-dns"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        devices = self.parse_basic_info(result.stdout)

        self.visualize_network(devices)

    def parse_hosts(self, nmap_output):
        return re.findall(r"for (\S+) \(", nmap_output)

    def parse_basic_info(self, nmap_output):
        devices = {}
        lines = nmap_output.splitlines()
        current_ip = None
        for line in lines:
            if 'Nmap scan report for' in line:
                parts = line.split()
                current_ip = parts[-1].strip('()')  # Supprimer les parenthèses si elles existent
                # Vérifier si un nom de domaine existe avant l'IP
                hostname = parts[4] if '(' in parts[-1] and len(parts) > 5 else 'No hostname'
                # Si pas de parenthèses et la taille des parties est correcte, le nom de domaine est utilisé comme IP
                if '(' not in parts[-1] and len(parts) == 5:
                    hostname = parts[-1]

                devices[current_ip] = {
                    'ip': current_ip,
                    'hostname': hostname if hostname != current_ip else 'No hostname',
                    'mac': 'Unknown MAC',
                    'vendor': 'Unknown'
                }
            elif 'MAC Address' in line:
                parts = line.split(' ', 3)
                if current_ip and len(parts) > 2:
                    devices[current_ip]['mac'] = parts[2]
                    devices[current_ip]['vendor'] = parts[3].strip('()') if len(parts) > 3 else 'Unknown'

        return devices

    def visualize_network(self, devices):
        G = nx.Graph()
        print("Devices to add to graph:", devices)
        if not devices:
            print("No devices found.")
            return

        central_node_label = ""
        G.add_node(central_node_label, label="Targeted network")

        for ip, info in devices.items():
            label = f"IP: {ip}\n"
            if info['hostname'] and info['hostname'] != 'No hostname':
                label += f"Hostname: {info['hostname']}\n"
            if info['mac'] and info['mac'] != 'Unknown MAC':
                label += f"MAC: {info['mac']}\n"
            G.add_node(ip, label=label)
            G.add_edge(ip, central_node_label, weight=0.1)

        pos = nx.spring_layout(G, k=0.5)  # `k` adjusts the distance between nodes
        nx.draw(G, pos, labels=nx.get_node_attributes(G, 'label'), with_labels=True, node_color='skyblue', edge_color='red', node_size=2500, font_size=9)
        plt.show()

    def quit_app(self):
        self.controller.quit()
