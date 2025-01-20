from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from DB_AWS import register_user, login_user
from network_scan import NetworkScanner
from spoofing import start_spoofing

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.master = parent
        self.setWindowTitle("Connexion")
        self.setGeometry(100, 100, 400, 300)

        # Champs de connexion
        self.username_label = QLabel("Nom d'utilisateur", self)
        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Entrez votre nom d'utilisateur")

        self.password_label = QLabel("Mot de passe", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Entrez votre mot de passe")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Se Connecter", self)
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Créer un compte", self)
        self.register_button.clicked.connect(self.open_register_window)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        if login_user(username, password):
            QMessageBox.information(self, "Connexion réussie", "Vous êtes connecté avec succès.")
            if self.master:
                self.master.login_successful()  # Appel au parent pour changer l'état
            self.close()

            # Lancer le scan réseau et le spoofing ARP
            devices = NetworkScanner()
            start_spoofing(devices)  # Démarrer le spoofing et la capture des paquets
        else:
            QMessageBox.critical(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

    def open_register_window(self):
        """Ouvre la fenêtre d'inscription"""
        self.register_window = RegisterWindow(self.master)
        self.register_window.setGeometry(400, 300, 400, 300)
        self.register_window.exec()

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créer un compte")
        self.setGeometry(100, 100, 400, 300)

        # Champs pour l'inscription
        self.username_label = QLabel("Nom d'utilisateur", self)
        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Choisissez un nom d'utilisateur")

        self.email_label = QLabel("Email", self)
        self.email_entry = QLineEdit(self)
        self.email_entry.setPlaceholderText("Entrez votre email")

        self.password_label = QLabel("Mot de passe", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Choisissez un mot de passe")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton("S'inscrire", self)
        self.register_button.clicked.connect(self.register)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_entry.text()
        email = self.email_entry.text()
        password = self.password_entry.text()
        if username and email and password:
            if register_user(username, email, password):
                QMessageBox.information(self, "Inscription réussie", "Votre compte a été créé avec succès.")
                self.close()  # Ferme la fenêtre d'inscription après succès
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de créer le compte. Essayez à nouveau.")
        else:
            QMessageBox.critical(self, "Erreur", "Veuillez remplir tous les champs.")


