import customtkinter as ctk
from PIL import Image
import webbrowser

class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a canvas as the main container
        self.canvas = ctk.CTkCanvas(self, bg="#041b29", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Load and display the logo image
        logo_image = Image.open("asset/logo.png")
        logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(250, 250))
        logo_label = ctk.CTkLabel(self.canvas, image=logo, text="")
        logo_label.pack(side=ctk.TOP, pady=(20, 20))

        # Display a welcome label
        label = ctk.CTkLabel(self.canvas, text="Welcome in the Toolbox!", text_color="white")
        label.pack(pady=10, padx=10)

        # Add a button to navigate to the menu
        menu_button = ctk.CTkButton(self.canvas, text="Start", command=self.go_to_menu)
        menu_button.pack(pady=5)

        # Add a button to open the README in the web browser
        readme_button = ctk.CTkButton(self.canvas, text="ReadME", command=self.open_readme)
        readme_button.pack(pady=5)

        # Add a button to quit the application
        quit_button = ctk.CTkButton(self.canvas, text="Quit", command=self.quit_app)
        quit_button.pack(pady=5)

    # Method to navigate to the menu page
    def go_to_menu(self):
        self.controller.show_frame("MenuPage")

    # Method to open the README in the web browser
    def open_readme(self):
        webbrowser.open("https://github.com/sleyzer47/toolbox#pentest-toolbox")

    # Method to quit the application
    def quit_app(self):
        self.controller.quit()
