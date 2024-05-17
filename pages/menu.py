import customtkinter as ctk
from tkinter import Text, END, Scrollbar, RIGHT, Y

class MenuPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    # Set up the main canvas
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

        # Add a text widget with scroll functionality
        text_frame = ctk.CTkFrame(self.canvas)
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        text_widget = Text(text_frame, wrap="word", font=("Arial", 12), bg="#f0f0f0", fg="black", bd=0, highlightthickness=0, yscrollcommand=scrollbar.set)
        text_widget.pack(side="top", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        self.insert_text(text_widget)

        # Make the text read-only
        text_widget.config(state="disabled")

    def insert_text(self, text_widget):
        # Load introduction text from file
        intro_text = self.load_intro_text("asset/menu.txt")

        # Define tags for styling
        text_widget.tag_configure("title", font=("Arial", 16, "bold"))
        text_widget.tag_configure("subtitle", font=("Arial", 14, "bold"))
        text_widget.tag_configure("bold", font=("Arial", 12, "bold"))

        # Insert styled text
        text_widget.insert(END, "Welcome to Pentest Toolbox!\n", "title")
        text_widget.insert(END, "\nPentest Toolbox is an integrated suite of tools designed to facilitate and speed up penetration testing for cybersecurity professionals. This application combines various features that cover multiple aspects of security audits, enabling users to scan, analyze, and assess the security of networks and computer systems.\n\n", "normal")
        
        text_widget.insert(END, "Objectives of Pentest Toolbox:\n", "subtitle")
        text_widget.insert(END, "Automate repetitive tasks: ", "bold")
        text_widget.insert(END, "Automate network scans, vulnerability tests, and more, thus freeing up time for more complex analyses.\n")
        text_widget.insert(END, "Centralize security tools: ", "bold")
        text_widget.insert(END, "Access a multitude of security features from a single interface, simplifying the penetration testing process.\n")
        text_widget.insert(END, "Detailed and actionable reports: ", "bold")
        text_widget.insert(END, "Generate detailed reports to document findings and facilitate decision-making based on concrete data.\n\n")
        
        text_widget.insert(END, "Features:\n", "subtitle")
        features = [
            ("Network scanning with Nmap: ", "Discover active devices on your network and their open ports."),
            ("Web vulnerability tests with Nikto and SQLmap: ", "Identify security flaws in web applications."),
            ("Secure password generation: ", "Create strong passwords to secure your access."),
            ("SSH brute force testing: ", "Test the resilience of your SSH servers against brute force attacks."),
            ("Network visualization: ", "Graphically visualize the structure of your network."),
            ("PDF report creation: ", "Compile your findings into formatted reports for clear documentation.")
        ]

        for title, description in features:
            text_widget.insert(END, title, "bold")
            text_widget.insert(END, description + "\n")

        text_widget.insert(END, "\nUse Pentest Toolbox to enhance your efficiency in penetration testing, reducing the time needed to gather information and increasing the accuracy of your security analyses.\n", "normal")

    def load_intro_text(self, filepath):
        """Load introduction text from a file."""
        try:
            with open(filepath, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "Introduction text file not found."

    def quit_app(self):
        self.controller.quit()
