import customtkinter as ctk
from scapy.all import sr1, IP, TCP
import ipaddress
import subprocess
import re
import json
import os
import threading
from tkinter import Label
from PIL import Image, ImageTk, ImageSequence

class NetworkPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_request_pending = False
        self.ports_and_services = {}
        self.loading_label = None
        self.loading_frames = []
        self.setup_ui()

    def setup_ui(self):
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame for the buttons
        button_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=button_frame, anchor="nw")
        button_frame.pack(fill="y", side="left")

        # Define navigation buttons
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

        # Add navigation buttons to the button frame
        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)

        # Add a quit button
        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        # Add labels and entry widget
        ctk.CTkLabel(self.canvas, text="Network Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="This feature is aimed at gateways, firewalls, etc.", text_color="Black", font=(None, 14)).pack(side="top", pady=5, anchor="n")
        ctk.CTkLabel(self.canvas, text="Enter the good target IP", text_color="Black", font=(None, 14)).pack(side="top", pady=5, anchor="n")

        self.entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        # Add a button to generate the report
        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.run_scans)
        generate_button.pack(fill="x", padx=150, pady=5)

        # Set up loading animation
        self.setup_loading_animation()

    def setup_loading_animation(self):
        # Load the loading animation GIF
        self.loading_image = Image.open("asset/loading.gif")
        self.loading_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(self.loading_image)]
        self.loading_label = Label(self.canvas, bg="#f0f0f0")
        self.loading_label.pack_forget()  # Hide it initially

    def start_loading_animation(self):
        # Show and start the loading animation
        self.loading_label.pack(side="top", pady=10)
        self.animate_loading(0)

    def stop_loading_animation(self):
        # Stop and hide the loading animation
        self.loading_label.pack_forget()

    def animate_loading(self, frame_index):
        # Animate the loading GIF
        if not self.is_request_pending:
            return  # Stop animation if no request is pending
        
        frame_image = self.loading_frames[frame_index]
        self.loading_label.config(image=frame_image)
        self.loading_label.image = frame_image
        next_frame_index = (frame_index + 1) % len(self.loading_frames)
        self.loading_label.after(100, self.animate_loading, next_frame_index)

    def run_scans(self):
        # Start the scanning process
        if self.is_request_pending:
            return
        ip = self.entry.get()
        try:
            ipaddress.ip_address(ip)
            self.is_request_pending = True
            self.start_loading_animation()
            threading.Thread(target=self.perform_scans, args=(ip,)).start()
        except ValueError:
            self.show_error_message("Incorrect/unreachable IP!", self.canvas)
            self.stop_loading_animation()

    def perform_scans(self, ip):
        # Perform all scans
        try:
            self.scan_with_nmap(ip)
            self.syn_flood_test(ip)
            self.malformed_packet_test(ip)
        finally:
            self.is_request_pending = False
            self.after(0, self.stop_loading_animation)

    def scan_with_nmap(self, ip):
        # Run an Nmap scan and store the results
        command = ["nmap", "-sV", ip]
        result = subprocess.run(command, capture_output=True, text=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if "/tcp" in line and "open" in line:
                match = re.search(r"(\d+)/tcp\s+open\s+([\w\s]+)", line)
                if match:
                    port = int(match.group(1))
                    service = match.group(2).strip()
                    self.ports_and_services[port] = service

    def syn_flood_test(self, ip):
        # Perform SYN flood test and update the JSON file
        syn_flood_results = [port for port in self.ports_and_services.keys()]
        self.update_json(ip, syn_flood_results=syn_flood_results)

    def malformed_packet_test(self, ip):
        # Perform malformed packet test and update the JSON file
        malformed_packet_results = {}
        flags_to_test = ['FPU', 'U', 'R', 'P']
        for port in self.ports_and_services.keys():
            results = {}
            for flag in flags_to_test:
                packet = IP(dst=ip)/TCP(dport=port, flags=flag)
                response = sr1(packet, timeout=1, verbose=0)
                response_status = "Response" if response else "No response"
                results[flag] = response_status
            malformed_packet_results[port] = results
        self.update_json(ip, malformed_packet_results=malformed_packet_results)

    def update_json(self, ip, syn_flood_results=None, malformed_packet_results=None):
        # Update the JSON file with the results
        json_path = os.path.join(os.getcwd(), 'result.json')
        if os.path.exists(json_path):
            with open(json_path, 'r+') as file:
                data = json.load(file)
                if not data.get(ip):
                    data[ip] = {}

                if syn_flood_results:
                    data[ip]["syn_flood_results"] = {f"Port: {port}": "Test completed" for port in syn_flood_results}
                if malformed_packet_results:
                    data[ip]["malformed_packet_results"] = {
                        f"Port: {port}": {f"Flag: {flag}": response for flag, response in results.items()}
                        for port, results in malformed_packet_results.items()
                    }

                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
        else:
            initial_data = {}
            if syn_flood_results:
                initial_data["syn_flood"] = {f"Port: {port}": "Test completed" for port in syn_flood_results}
            if malformed_packet_results:
                initial_data["malformed_packet"] = {
                    f"Port: {port}": {f"Flag: {flag}": response for flag, response in results.items()}
                    for port, results in malformed_packet_results.items()
                }
            with open(json_path, 'w') as file:
                json.dump({ip: initial_data}, file, indent=4)

    def show_error_message(self, message, canvas):
        # Show an error message on the canvas
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        # Reset the request state
        self.is_request_pending = False

    def quit_app(self):
        # Quit the application
        self.is_request_pending = False
        self.controller.quit()
