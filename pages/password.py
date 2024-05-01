import customtkinter as ctk
import string
import random

class PasswordPage(ctk.CTkFrame):
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

        ctk.CTkLabel(self.canvas, text="Password Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Welcome in password page!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")
        
        self.length_entry = ctk.CTkEntry(self.canvas, placeholder_text="Enter password length")
        self.length_entry.pack(padx=200, pady=5)

        self.include_uppercase = ctk.CTkCheckBox(self.canvas, text="Include Uppercase")
        self.include_uppercase.pack(padx=10, pady=5)

        self.include_digits = ctk.CTkCheckBox(self.canvas, text="Include Numbers")
        self.include_digits.pack(padx=10, pady=5)

        self.include_special = ctk.CTkCheckBox(self.canvas, text="Include Special Characters")
        self.include_special.pack(padx=10, pady=5)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.generate_password)
        generate_button.pack(fill="x", padx=150, pady=5)

        self.result_label = ctk.CTkLabel(self.canvas, text="", font=(None, 12), text_color="Blue")
        self.result_label.pack(side="top", pady=10, anchor="n")

    def generate_password(self):
        if self.is_request_pending:
            return
        length = int(self.length_entry.get())
        include_upper = self.include_uppercase.get()
        include_digits = self.include_digits.get()
        include_special = self.include_special.get()

        characters = string.ascii_lowercase
        if include_upper:
            characters += string.ascii_uppercase
        if include_digits:
            characters += string.digits
        if include_special:
            characters += string.punctuation

        password = ''.join(random.choice(characters) for i in range(length))
        self.result_label.configure(text=password)
        print(password)
        
        self.is_request_pending = True
        self.after(300, self.reset_request_state)

    def show_error_message(self, message, canvas):
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
