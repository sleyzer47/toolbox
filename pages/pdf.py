import customtkinter as ctk
import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tkinter import Label
from PIL import Image, ImageTk, ImageSequence
import threading

class PDFPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_request_pending = False
        self.loading_label = None
        self.loading_frames = []
        self.setup_ui()

    def setup_ui(self):
        # Set up the main canvas
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

        # Add a title label
        ctk.CTkLabel(self.canvas, text="PDF Generation Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")
        generate_button = ctk.CTkButton(self.canvas, text="Generate Report", command=self.generate_pdf)
        generate_button.pack(fill="x", padx=150, pady=5)

        self.setup_loading_animation()

    def setup_loading_animation(self):
        # Set up the loading animation
        self.loading_image = Image.open("asset/loading.gif")
        self.loading_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(self.loading_image)]
        self.loading_label = Label(self.canvas, bg="#f0f0f0")
        self.loading_label.pack_forget()  # Hide it initially

    def start_loading_animation(self):
        # Start the loading animation
        self.loading_label.pack(side="top", pady=10)
        self.animate_loading(0)

    def stop_loading_animation(self):
        # Stop the loading animation
        self.loading_label.pack_forget()

    def animate_loading(self, frame_index):
        # Animate the loading gif
        if not self.is_request_pending:
            return  # Stop animation if no request is pending
        
        frame_image = self.loading_frames[frame_index]
        self.loading_label.config(image=frame_image)
        self.loading_label.image = frame_image
        next_frame_index = (frame_index + 1) % len(self.loading_frames)
        self.loading_label.after(100, self.animate_loading, next_frame_index)

    def generate_pdf(self):
        # Generate the PDF report
        json_path = os.path.join(os.getcwd(), 'result.json')
        
        # Check if JSON file is empty
        with open(json_path, 'r') as file:
            data = json.load(file)
            if not data:
                self.show_error_message("No data available to generate PDF!", self.canvas)
                return
        
        self.is_request_pending = True
        self.start_loading_animation()
        threading.Thread(target=self.perform_pdf_generation, args=(json_path,)).start()

    def perform_pdf_generation(self, json_path):
        # Perform the actual PDF generation
        try:
            pdf_path = os.path.join(os.getcwd(), 'report.pdf')
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            custom_styles = {
                'Title': ParagraphStyle(name='Title', fontSize=24, leading=30, alignment=1, spaceAfter=20),
                'Subtitle': ParagraphStyle(name='Subtitle', fontSize=18, leading=22, alignment=1, spaceAfter=20),
                'NormalCenter': ParagraphStyle(name='NormalCenter', fontSize=12, leading=15, alignment=1, spaceAfter=20),
                'NormalRight': ParagraphStyle(name='NormalRight', fontSize=12, leading=15, alignment=2, spaceAfter=20),
                'BoldCenter': ParagraphStyle(name='BoldCenter', fontSize=12, leading=15, alignment=1, spaceAfter=20, fontName='Helvetica-Bold')
            }
            story = []

            # First page
            cover_title = "Pentest Toolbox Report"
            cover_subtitle = "This report is generated by the Toolbox"
            cover_date = "Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            summary = (
                "This report contains the results of a comprehensive penetration test conducted "
                "to identify and address security vulnerabilities within the target."
                "The findings and recommendations aim to enhance the security posture of the organization."
            )

            story.append(Spacer(1, 100))
            story.append(Paragraph(cover_title, custom_styles['Title']))
            story.append(Paragraph(cover_subtitle, custom_styles['Subtitle']))
            story.append(Spacer(1, 30))
            story.append(Paragraph(cover_date, custom_styles['BoldCenter']))
            story.append(Spacer(1, 50))
            story.append(Paragraph("Executive Summary", custom_styles['Subtitle']))
            story.append(Paragraph(summary, styles['Normal']))

            with open(json_path, 'r') as file:
                data = json.load(file)

            for ip, sections in data.items():
                story.append(PageBreak())  # Add page break before each new target
                story.append(Paragraph(f"Results for {ip}", styles['Heading2']))

                # NMAP part
                if "nmap" in sections:
                    nmap_entries = sections["nmap"]
                    story.append(Paragraph("Nmap Results:", styles['Heading3']))
                    column_widths = [60, 120, 120, 150]  # Adjust based on your content
                    table_data = [["Port", "Service", "Version", "CVEs"]]
                    for entry in nmap_entries:
                        cves = "\n".join(entry.get("CVE", []))
                        table_data.append([
                            Paragraph(entry.get("port", ""), styles['BodyText']),
                            Paragraph(entry.get("service", ""), styles['BodyText']),
                            Paragraph(entry.get("version", ""), styles['BodyText']),
                            Paragraph(cves, styles['BodyText'])
                        ])
                    tbl = Table(table_data, colWidths=column_widths)
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 2, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(tbl)
                    story.append(Spacer(1, 12))

                # Web Scans part
                if "web_scans" in sections:
                    web_scans_entries = sections["web_scans"]
                    story.append(Paragraph("Web Scans Results:", styles['Heading3']))
                    column_widths = [60, 120, 180, 150]  # Adjust based on your content
                    table_data = [["Port", "Service", "SQLMap", "Nikto"]]
                    for entry in web_scans_entries:
                        sqlmap_output = entry.get("sqlmap_results", {}).get("output", "")
                        nikto_cves = "\n".join(entry.get("nikto_results", {}).get("CVE", []))
                        table_data.append([
                            Paragraph(str(entry.get("port", "")), styles['BodyText']),
                            Paragraph(entry.get("service", ""), styles['BodyText']),
                            Paragraph(sqlmap_output, styles['BodyText']),
                            Paragraph(nikto_cves, styles['BodyText'])
                        ])
                    tbl = Table(table_data, colWidths=column_widths)
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 2, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(tbl)
                    story.append(Spacer(1, 12))

                # SSH Brute Force part
                if "ssh_brute_force" in sections:
                    ssh_brute_force_entries = sections["ssh_brute_force"]
                    story.append(Paragraph("SSH Brute Force Results:", styles['Heading3']))
                    column_widths = [60, 180, 180, 150]  # Adjust based on your content
                    table_data = [["Port", "Username List", "Password List", "Result"]]
                    table_data.append([
                        Paragraph(str(ssh_brute_force_entries.get("port", "")), styles['BodyText']),
                        Paragraph(ssh_brute_force_entries.get("username_list", ""), styles['BodyText']),
                        Paragraph(ssh_brute_force_entries.get("password_list", ""), styles['BodyText']),
                        Paragraph(ssh_brute_force_entries.get("result", ""), styles['BodyText'])
                    ])
                    tbl = Table(table_data, colWidths=column_widths)
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 2, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(tbl)
                    story.append(Spacer(1, 12))

                # SYN Flood part
                if "syn_flood_results" in sections:
                    syn_flood_entries = sections["syn_flood_results"]
                    story.append(Paragraph("SYN Flood Results:", styles['Heading3']))
                    column_widths = [120, 180]  # Adjust based on your content
                    table_data = [["Port", "Result"]]
                    for port, result in syn_flood_entries.items():
                        table_data.append([
                            Paragraph(port, styles['BodyText']),
                            Paragraph(result, styles['BodyText'])
                        ])
                    tbl = Table(table_data, colWidths=column_widths)
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 2, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(tbl)
                    story.append(Spacer(1, 12))

                # Malformed Packet Results part
                if "malformed_packet_results" in sections:
                    malformed_packet_entries = sections["malformed_packet_results"]
                    story.append(Paragraph("Malformed Packet Results:", styles['Heading3']))
                    column_widths = [120, 300]  # Adjust based on your content
                    table_data = [["Port", "Results"]]
                    for port, results in malformed_packet_entries.items():
                        result_text = "\n".join([f"{flag}: {response}" for flag, response in results.items()])
                        table_data.append([
                            Paragraph(port, styles['BodyText']),
                            Paragraph(result_text, styles['BodyText'])
                        ])
                    tbl = Table(table_data, colWidths=column_widths)
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 2, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(tbl)
                    story.append(Spacer(1, 12))

                # Other part
                for section_name, entries in sections.items():
                    if section_name not in ["nmap", "web_scans", "ssh_brute_force", "syn_flood_results", "malformed_packet_results"]:
                        story.append(Paragraph(section_name.replace('_', ' ').title() + ':', styles['Heading3']))
                        if isinstance(entries, dict):
                            for key, value in entries.items():
                                text = f"{key}: {value}"
                                story.append(Paragraph(text, styles['BodyText']))
                        elif isinstance(entries, list):
                            for item in entries:
                                if isinstance(item, dict):
                                    for key, value in item.items():
                                        text = f"{key}: {value}"
                                        story.append(Paragraph(text, styles['BodyText']))
                                else:
                                    text = str(item)
                                    story.append(Paragraph(text, styles['BodyText']))

                        story.append(Spacer(1, 12))

            doc.build(story)
            print("PDF generated successfully!")

            # Clear the JSON file
            with open(json_path, 'w') as file:
                json.dump({}, file)
        finally:
            self.is_request_pending = False
            self.stop_loading_animation()

    def show_error_message(self, message, canvas):
        # Show an error message on the canvas
        label_error = ctk.CTkLabel(canvas, text=message, text_color="Red", font=(None, 11))
        label_error.pack(side="top", pady=10, anchor="n")
        self.after(3000, lambda: label_error.destroy())

    def reset_request_state(self):
        # Reset the request state
        self.is_request_pending = False

    def quit_app(self):
        # Quit the application
        self.is_request_pending = False
        self.controller.quit()
