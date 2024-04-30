import customtkinter as ctk
from pages.start import StartPage
from pages.menu import MenuPage
from pages.web import WebPage
from pages.network import NetworkPage
from pages.nmap import NmapPage
from pages.nessus import NessusPage
from pages.password import PasswordPage
from pages.ssh import SSHPage

class CustomTkinterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ToolBox")
        self.geometry("800x600")

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {
            "StartPage": StartPage,
            "MenuPage": MenuPage,
            "NetworkPage": NetworkPage,
            "WebPage": WebPage,
            "NmapPage": NmapPage,
            "NessusPage": NessusPage,
            "PasswordPage": PasswordPage,
            "AuthPage": SSHPage            
        }

        self.current_frame = None
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        if page_name in self.frames:
            # Détruire le cadre actuel s'il existe
            if self.current_frame:
                self.current_frame.destroy()
            # Créer et afficher le nouveau cadre
            FrameClass = self.frames[page_name]
            self.current_frame = FrameClass(parent=self.container, controller=self)
            self.current_frame.pack(fill="both", expand=True)
        else:
            print(f"Error: Page '{page_name}' not found")


app = CustomTkinterApp()
app.mainloop()
