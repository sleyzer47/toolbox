import customtkinter as ctk
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from textwrap import wrap

class PDFPage(ctk.CTkFrame):
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

        ctk.CTkLabel(self.canvas, text="PDF Generation Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        ctk.CTkLabel(self.canvas, text="Click to generate a PDF report from the results!", text_color="Black", font=(None, 14)).pack(side="top", pady=10, anchor="n")

        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.generate_pdf)
        generate_button.pack(fill="x", padx=150, pady=5)

    def wrap_text(self, text, width):
        """
        Wrap text to fit into a specific width
        """
        return wrap(text, width)

    def generate_pdf(self):
        json_path = os.path.join(os.getcwd(), 'result.json')
        with open(json_path, 'r') as file:
            data = json.load(file)

        pdf_path = os.path.join(os.getcwd(), 'report.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # Ajout de la page de garde
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, "Pentest Toolbox")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawCentredString(width / 2, height - 130, f"Generated on: {current_datetime}")
        c.showPage()

        # Génération des résultats de scan
        max_line_length = 80
        line_height = 14
        margin = 30

        for ip, sections in data.items():
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin, height - margin, f"Results for {ip}")
            y_position = height - margin - 30

            for section_name, entries in sections.items():
                if y_position < 100:  # Ensure there is space to start new section
                    c.showPage()
                    y_position = height - margin

                c.setFont("Helvetica-Bold", 14)
                c.drawString(margin, y_position, section_name.replace('_', ' ').title() + ':')
                y_position -= 20

                c.setFont("Helvetica", 12)
                if isinstance(entries, dict):
                    for key, value in entries.items():
                        wrapped_text = self.wrap_text(f"{key}: {value}", max_line_length)
                        for line in wrapped_text:
                            if y_position < margin + line_height:
                                c.showPage()
                                y_position = height - margin
                            c.drawString(margin + 10, y_position, line)
                            y_position -= line_height
                    y_position -= 10
                elif isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, dict):
                            for key, value in entry.items():
                                if isinstance(value, list):
                                    value = ', '.join(value)
                                wrapped_text = self.wrap_text(f"{key}: {value}", max_line_length)
                                for line in wrapped_text:
                                    if y_position < margin + line_height:
                                        c.showPage()
                                        y_position = height - margin
                                    c.drawString(margin + 10, y_position, line)
                                    y_position -= line_height
                            y_position -= 10  # Extra space between entries
                        else:
                            wrapped_text = self.wrap_text(str(entry), max_line_length)
                            for line in wrapped_text:
                                if y_position < margin + line_height:
                                    c.showPage()
                                    y_position = height - margin
                                c.drawString(margin + 10, y_position, line)
                                y_position -= line_height
                            y_position -= 10

                y_position -= 10  # Extra space before a new section

            c.showPage()  # Start a new page after each IP section

        c.save()
        print("PDF generated successfully!")
            # Clear the JSON file
        with open(json_path, 'w') as file:
            json.dump({}, file)  # Reset the file to empty or initial structure

    def show_message(self, message, canvas):
        label = ctk.CTkLabel(canvas, text=message, text_color="Green", font=(None, 11))
        label.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label.destroy())

    def reset_request_state(self):
        self.is_request_pending = False

    def quit_app(self):
        self.controller.quit()
