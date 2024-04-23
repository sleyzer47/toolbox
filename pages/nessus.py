import customtkinter as ctk
from nessrest.ness6rest import Scanner

class NessusPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        # Assurez-vous que les détails du serveur sont corrects et que le token est valide
        self.scanner = Scanner(url="https://localhost:8834", login="admin", password="admin", insecure=True)

    def setup_ui(self):
        self.ip_address_entry = ctk.CTkEntry(self, placeholder_text="Entrez l'adresse IP cible")
        self.ip_address_entry.pack(pady=20, padx=20)

        scan_button = ctk.CTkButton(self, text="Démarrer le scan Nessus", command=self.start_scan)
        scan_button.pack(pady=10)

        self.results_label = ctk.CTkLabel(self, text="Les résultats du scan apparaîtront ici", text_color="black")
        self.results_label.pack(pady=20)

    def start_scan(self):
        target_ip = self.ip_address_entry.get()
        if target_ip:
            # Faites correspondre les paramètres avec ceux acceptés par votre API
            try:
                response = self.scanner.scan_add(target_ip)
                if 'scan' in response:
                    scan_id = response['scan']['uuid']
                    self.scanner.scan_run(scan_id=scan_id)
                    self.results_label.configure(text=f"Scan lancé pour l'IP : {target_ip}")
                else:
                    self.results_label.configure(text="Erreur lors de la création du scan: " + str(response))
            except Exception as e:
                self.results_label.configure(text=f"Erreur lors de la communication avec Nessus: {e}")
        else:
            self.results_label.configure(text="Veuillez entrer une adresse IP valide.")

# Assurez-vous d'intégrer cette classe correctement avec le reste de votre application.
