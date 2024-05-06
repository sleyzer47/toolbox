import customtkinter as ctk
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

class PDFPage(ctk.CTkFrame):
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

        ctk.CTkLabel(self.canvas, text="PDF Generation Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Click to generate a PDF report from the results!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")

        def generate_pdf():
            json_path = os.path.join(os.getcwd(), 'result.json')
            with open(json_path, 'r') as file:
                data = json.load(file)

            pdf_path = os.path.join(os.getcwd(), 'report.pdf')
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter

            # Ajout de la page de garde
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width/2, height - 100, "Pentest Toolbox")
            c.setFont("Helvetica", 12)
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.drawCentredString(width/2, height - 130, f"Generated on: {current_datetime}")
            c.showPage()  # Commencer une nouvelle page après la page de garde

            # Génération des résultats de scan
            for key, values in data.items():
                y_position = height - 30
                c.setFont("Helvetica-Bold", 18)
                c.drawString(30, y_position, key.upper() + " Scan Results:")
                c.setFont("Helvetica", 12)
                y_position -= 20
                for value in values:
                    for field, info in value.items():
                        if isinstance(info, list):
                            info = ', '.join(info)
                        c.drawString(40, y_position, f"{field}: {info}")
                        y_position -= 20
                    y_position -= 10  # Add extra space between entries
                c.showPage()  # Start a new page after each section

            c.save()
            self.show_message("PDF generated successfully!", self.canvas)

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=generate_pdf)
        generate_button.pack(fill="x", padx=150, pady=5)

    def show_message(self, message, canvas):
        label = ctk.CTkLabel(canvas, text=message, text_color="Green", font=(None, 11))
        label.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
