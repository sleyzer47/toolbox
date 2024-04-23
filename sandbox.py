import customtkinter as ctk
import ipaddress
import time
from gvm.protocols.latest import Gmp
from gvm.connections import UnixSocketConnection
from reportlab.pdfgen import canvas
import os
import subprocess

class OpenVASPage(ctk.CTkFrame):
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

        button4 = ctk.CTkButton(button_frame, text="OpenVAS", fg_color="#0d68a1")
        button4.pack(fill="x", padx=10, pady=5)

        button5 = ctk.CTkButton(button_frame, text="Password", command=lambda: self.controller.show_frame("PasswordPage"))
        button5.pack(fill="x", padx=10, pady=5)

        button6 = ctk.CTkButton(button_frame, text="Auth", command=lambda: self.controller.show_frame("AuthPage"))
        button6.pack(fill="x", padx=10, pady=5)

        # Ajouter le bouton "Quitter" à la fin de la liste de boutons
        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        title = ctk.CTkLabel(canvas, text="OpenVAS Page", text_color="Black", font=(None, 20))
        title.pack(side="top", pady=10, anchor="n")

        label = ctk.CTkLabel(canvas, text="Welcome in OpenVAS page!", text_color="Black", font=(None, 14))
        label.pack(side="top", pady=10, anchor="n")

        self.entry = ctk.CTkEntry(canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        self.is_request_pending = False

        def generate_report():
            if self.is_request_pending:
                return

            ip = self.entry.get()

            try:
                ip_ok = ipaddress.ip_address(ip)
            except ValueError:
                self.show_error_message("Incorrect/unreachable IP!", canvas)
                return

            # Run the OpenVAS scan
            self.run_openvas_scan(ip)

            self.is_request_pending = True

            self.after(3000, self.reset_request_state)

        generate_button = ctk.CTkButton(canvas, text="Generate Report", command=generate_report)
        generate_button.pack(fill="x", padx=150, pady=5)

    def run_openvas_scan(self, target):
        # Define the command to run
        command = f"gvm-cli socket --xml '<create_target><name>My Target</name><hosts>{target}</hosts></create_target>'"

        # Run the command and get the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            print(f"Error running OpenVAS scan: {result.stderr}")
            return

        # Extract the target_id from the result
        target_id = self.parse_target_id(result.stdout)  # You'll need to implement this function

        # Now that we have a target, we can create and start a task
        command = f"gvm-cli socket --xml '<create_task><name>My Task</name><config id=\\\"daba56c8-73ec-11df-a475-002264764cea\\\"/><target id=\\\"{target_id}\\\"/></create_task>'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            print(f"Error creating OpenVAS task: {result.stderr}")
            return

        # Extract the task_id from the result
        task_id = self.parse_task_id(result.stdout)  # You'll need to implement this function

        # Start the task
        command = f"gvm-cli socket --xml '<start_task task_id={task_id}/>'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            print(f"Error starting OpenVAS task: {result.stderr}")
            return

    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, label_error.destroy)

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()