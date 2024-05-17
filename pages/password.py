import customtkinter as ctk
import string
import random
import pyperclip

class PasswordPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_request_pending = False
        self.current_canvas = None
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
        ctk.CTkLabel(self.canvas, text="Password Page", text_color="Black", font=(None, 20)).pack(side="top", pady=10, anchor="n")

        # Add buttons for password generation and testing
        self.generate_password_button = ctk.CTkButton(self.canvas, text="Generate Password", command=self.show_generate_password)
        self.generate_password_button.pack(pady=5)

        self.test_password_button = ctk.CTkButton(self.canvas, text="Test Password", command=self.show_test_password)
        self.test_password_button.pack(pady=5)

        # Show the password generation UI by default
        self.show_generate_password()

    def clear_canvas(self):
        # Clear the current canvas
        if self.current_canvas:
            self.current_canvas.destroy()
        self.current_canvas = ctk.CTkCanvas(self.canvas, highlightthickness=0)
        self.current_canvas.pack(fill="both", expand=True)

    def show_generate_password(self):
        # Show the password generation UI
        self.clear_canvas()
        self.length_entry = ctk.CTkEntry(self.current_canvas, placeholder_text="Enter password length")
        self.length_entry.pack(padx=200, pady=5)

        self.include_uppercase = ctk.CTkCheckBox(self.current_canvas, text="Include Uppercase")
        self.include_uppercase.pack(padx=10, pady=5)

        self.include_numbers = ctk.CTkCheckBox(self.current_canvas, text="Include Numbers")
        self.include_numbers.pack(padx=10, pady=5)

        self.include_special = ctk.CTkCheckBox(self.current_canvas, text="Include Special Characters")
        self.include_special.pack(padx=10, pady=5)

        generate_button = ctk.CTkButton(self.current_canvas, text="Generate Password", command=self.generate_password)
        generate_button.pack(fill="x", padx=150, pady=5)

        self.result_label = ctk.CTkLabel(self.current_canvas, text="", font=(None, 12), text_color="Blue")
        self.result_label.pack(side="top", pady=10, anchor="n")

    def show_test_password(self):
        # Show the password testing UI
        self.clear_canvas()
        ctk.CTkLabel(self.current_canvas, text="Enter the password", font=(None, 16)).pack(pady=10)
        self.password_entry = ctk.CTkEntry(self.current_canvas, placeholder_text="Enter password to test")
        self.password_entry.pack(pady=10)

        test_button = ctk.CTkButton(self.current_canvas, text="Test Strength", command=self.test_password)
        test_button.pack(pady=20)

        self.test_result_label = ctk.CTkLabel(self.current_canvas, text="", font=(None, 12))
        self.test_result_label.pack(pady=10)

    def generate_password(self):
        # Generate a random password
        if self.is_request_pending:
            return
        try:
            length = int(self.length_entry.get())
            if length < 4 or length > 100:
                self.show_error_message("Password length must be between 4 and 100", self.current_canvas)
                return
        except ValueError:
            self.show_error_message("Enter a number!", self.current_canvas)
            return

        include_upper = self.include_uppercase.get()
        include_numbers = self.include_numbers.get()
        include_special = self.include_special.get()

        characters = string.ascii_lowercase
        if include_upper:
            characters += string.ascii_uppercase
        if include_numbers:
            characters += string.digits
        if include_special:
            characters += string.punctuation

        password = ''.join(random.choice(characters) for i in range(length))
        self.result_label.configure(text=password + "\nPassword copied to clipboard!")
        self.copy_to_clipboard(password)

        self.is_request_pending = True
        self.after(300, self.reset_request_state)

    def update_label_color(self, score):
        # Update the label color based on password strength
        if score == 1:
            color = "#D81717"  # red
        elif score == 2:
            color = "#Ec8b0f"  # orange
        elif score == 3:
            color = "#E2bb38"  # yellow
        elif score == 4:
            color = "#90d615"  # light green
        else:
            color = "#008000"  # dark green
        self.test_result_label.configure(text_color=color, font=("Helvetica", 12, "bold"))

    def test_password(self):
        # Test the strength of the entered password
        if self.is_request_pending:
            return
        password = self.password_entry.get()
        score = 5

        if not any(c.isupper() for c in password):
            score -= 1
        if not any(c.isdigit() for c in password):
            score -= 1
        if not any(c in string.punctuation for c in password):
            score -= 1
        if len(password) < 8:
            score -= 1
        if not any(c.islower() for c in password):
            score -= 1

        self.update_label_color(score)
        result_text = f"Password Strength Score: {score}/5"
        self.test_result_label.configure(text=result_text)

        self.is_request_pending = True
        self.after(300, self.reset_request_state)

    def copy_to_clipboard(self, password):
        # Copy the generated password to the clipboard
        try:
            pyperclip.copy(password)
        except Exception as e:
            print("Failed to copy password to clipboard:", str(e))

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
        self.controller.quit()
