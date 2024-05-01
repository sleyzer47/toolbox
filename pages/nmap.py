import customtkinter as ctk
import subprocess
import ipaddress

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
            ("Nessus", lambda: self.controller.show_frame("NessusPage")),
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

        options = ["-sS", "-A", "-sV"]
        self.nmap_option = ctk.IntVar(value=1)
        for i, option in enumerate(options):
            radiobutton = ctk.CTkRadioButton(self.canvas, text=option, variable=self.nmap_option, value=i+1)
            radiobutton.pack(padx=200, pady=5)

        def generate_report():
            if self.is_request_pending:
                return
            
            ip = self.entry.get()
            nmap_option = options[self.nmap_option.get() - 1]

            try:
                ipaddress.ip_address(ip)
            except ValueError:
                self.show_error_message("Incorrect/unreachable IP!", self.canvas)
                return

            self.is_request_pending = True

            run_nmap_scan(ip, nmap_option)  # Appeler la fonction run_nmap_scan avec l'adresse IP et l'option Nmap

            self.after(3000, self.reset_request_state)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=generate_report)
        generate_button.pack(fill="x", padx=150, pady=5)


    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()

def run_nmap_scan(ip, option):
    command = f"nmap {option} {ip}"
    subprocess.run(command, shell=True)