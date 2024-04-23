import customtkinter as ctk
import subprocess
import ipaddress

class NmapPage(ctk.CTkFrame):
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

        button3 = ctk.CTkButton(button_frame, text="Nmap", fg_color="#0d68a1")
        button3.pack(fill="x", padx=10, pady=5)

        button4 = ctk.CTkButton(button_frame, text="OpenVAS", command=lambda: self.controller.show_frame("OpenVASPage"))
        button4.pack(fill="x", padx=10, pady=5)

        button5 = ctk.CTkButton(button_frame, text="Password", command=lambda: self.controller.show_frame("PasswordPage"))
        button5.pack(fill="x", padx=10, pady=5)

        button6 = ctk.CTkButton(button_frame, text="Auth", command=lambda: self.controller.show_frame("AuthPage"))
        button6.pack(fill="x", padx=10, pady=5)

        # Ajouter le bouton "Quitter" à la fin de la liste de boutons
        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)



        title = ctk.CTkLabel(canvas, text="Nmap Page", text_color="Black", font=(None, 20))
        title.pack(side="top", pady=10, anchor="n")

        label = ctk.CTkLabel(canvas, text="Welcome in nmap page!", text_color="Black", font=(None, 14))
        label.pack(side="top", pady=10, anchor="n")
        


        self.entry = ctk.CTkEntry(canvas, placeholder_text="Enter the target IP")
        self.entry.pack(padx=200, pady=5)

        options = ["-sS", "-A", "-sV"]
        self.nmap_option = ctk.IntVar(value=1)  # Par défaut, utiliser -sS
        for i, option in enumerate(options):
            radiobutton = ctk.CTkRadioButton(canvas, text=option, variable=self.nmap_option, value=i+1)
            radiobutton.pack(padx=200, pady=5)


        self.is_request_pending = False

        def generate_report():
            if self.is_request_pending:
                return
            
            ip = self.entry.get()
            nmap_option = options[self.nmap_option.get() - 1]

            try:
                ip_ok = ipaddress.ip_address(ip)
            except ValueError:
                self.show_error_message("Incorrect/unreachable IP!", canvas)
                return

            self.is_request_pending = True

            run_nmap_scan(ip, nmap_option)  # Appeler la fonction run_nmap_scan avec l'adresse IP et l'option Nmap

            self.after(3000, self.reset_request_state)

        generate_button = ctk.CTkButton(canvas, text="Generate Report", command=generate_report)
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