import customtkinter as ctk
from PIL import Image

class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.canvas = ctk.CTkCanvas(self, bg="#041b29", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        logo_image = Image.open("asset/logo.png")
        logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(250, 250))
        logo_label = ctk.CTkLabel(self.canvas, image=logo, text="")
        logo_label.pack(side=ctk.TOP, pady=(20, 20))

        label = ctk.CTkLabel(self.canvas, text="Start Page", text_color="white")
        label.pack(pady=10, padx=10)

        menu_button = ctk.CTkButton(self.canvas, text="Go to Menu", command=self.go_to_menu)
        menu_button.pack(pady=5)

        quit_button = ctk.CTkButton(self.canvas, text="Quit", command=self.quit_app)
        quit_button.pack(pady=5)

    def go_to_menu(self):
        self.controller.show_frame("MenuPage")

    def quit_app(self):
        self.controller.quit()
