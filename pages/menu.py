import customtkinter as ctk
from tkinter import Text, END, Scrollbar, RIGHT, Y

class MenuPage(ctk.CTkFrame):
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
            ("SSH", lambda: self.controller.show_frame("SSHPage")),
            ("PDF", lambda: self.controller.show_frame("PDFPage"))
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)

        quit_button = ctk.CTkButton(button_frame, text="Quitter", command=self.quit_app, fg_color="#d05e5e")
        quit_button.pack(fill="x", padx=10, pady=5)

        text_widget = Text(self.canvas, wrap="word", font=("Arial", 12), bg="#f0f0f0", fg="black", bd=0, highlightthickness=0)
        text_widget.insert(END, self.load_intro_text("asset/menu.txt"))
        text_widget.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        text_widget.config(state="disabled")  # Make the text read-only

        # Adding a Scrollbar
        scrollbar = Scrollbar(self.canvas, command=text_widget.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.config(yscrollcommand=scrollbar.set)

    def load_intro_text(self, filepath):
        """Load introduction text from a file."""
        try:
            with open(filepath, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "Introduction text file not found."

    def quit_app(self):
        self.controller.quit()
