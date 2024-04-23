import customtkinter as ctk

class PasswordPage(ctk.CTkFrame):
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

        button5 = ctk.CTkButton(button_frame, text="Password", fg_color="#0d68a1")
        button5.pack(fill="x", padx=10, pady=5)

        button6 = ctk.CTkButton(button_frame, text="Auth", command=lambda: self.controller.show_frame("AuthPage"))
        button6.pack(fill="x", padx=10, pady=5)

        # Ajouter le bouton "Quitter" à la fin de la liste de boutons
        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        title = ctk.CTkLabel(canvas, text="Password Page", text_color="Black", font=(None, 20))
        title.pack(side="top", pady=10, anchor="n")

        label = ctk.CTkLabel(canvas, text="Welcome in password page!", text_color="Black", font=(None, 14))
        label.pack(side="top", pady=10, anchor="n")
        

    def quit_app(self):
        self.controller.quit()
