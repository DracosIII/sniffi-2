from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QMessageBox, QDialog
from PyQt6.QtCore import Qt, QThread
from formulaire_inscription  import LoginWindow
from DB_AWS import load_session, save_session, clear_session
import pymysql
from network_scan import NetworkScanner
from spoofing import start_spoofing
import sys

SESSION_FILE = "session.txt"

def get_connection():
    """Crée une connexion à la base de données avec gestion d'erreurs."""
    try:
        return pymysql.connect(
            host="sniffi.cli6wkgcach0.us-east-1.rds.amazonaws.com",
            user="admin",
            password="5486201379",
            database="sniffi",
            connect_timeout=10  # Timeout de connexion
        )
    except pymysql.err.OperationalError as e:
        print(f"Erreur de connexion à la base de données : {e}")
        QMessageBox.critical(None, "Erreur", f"Connexion à la base de données échouée : {e}")
        return None
    
class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test PyQt")
        self.setGeometry(100, 100, 300, 200)
        label = QLabel("Application PyQt fonctionne !", self)
        label.move(50, 50)

class ARPSpooferApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("ARP Spoofer")
        self.setGeometry(100, 100, 600, 700)
        self.username = username
        self.devices = []

        # Affichage du nom d'utilisateur
        self.username_label = QLabel(f"Connecté en tant que : {username}", self)
        self.username_label.setGeometry(20, 20, 400, 30)

        # Bouton pour déconnexion
        self.logout_button = QPushButton("Se Déconnecter", self)
        self.logout_button.setGeometry(20, 60, 200, 40)
        self.logout_button.clicked.connect(self.logout)

        # Table pour afficher les appareils détectés
        self.devices_table = QTableWidget(self)
        self.devices_table.setColumnCount(3)
        self.devices_table.setHorizontalHeaderLabels(["Nom de l'appareil", "Adresse IP", "Adresse MAC"])
        self.devices_table.setGeometry(20, 120, 560, 300)

        # Bouton pour lancer un scan réseau
        self.scan_button = QPushButton("Scanner le Réseau", self)
        self.scan_button.setGeometry(20, 450, 200, 40)
        self.scan_button.clicked.connect(self.scan_network)

        # Bouton pour démarrer le spoofing
        self.spoof_button = QPushButton("Démarrer le Spoofing", self)
        self.spoof_button.setGeometry(240, 450, 200, 40)
        self.spoof_button.clicked.connect(self.start_spoofing)

        # Statut
        self.status_label = QLabel("Statut : Prêt", self)
        self.status_label.setGeometry(20, 500, 400, 30)

        # Créer une instance du scanner réseau
        self.network_scanner = NetworkScanner()

        # Connecter le signal de détection de l'appareil à la méthode de mise à jour
        self.network_scanner.device_detected_signal.connect(self.update_device_table)

        # Lancer le scan réseau en arrière-plan
        self.scan_thread = QThread()
        self.network_scanner.moveToThread(self.scan_thread)  # Déplacer l'objet scanner vers le thread
        self.scan_thread.started.connect(self.network_scanner.continuous_scan)
        self.scan_thread.start()


    def logout(self):
        clear_session()
        QMessageBox.information(self, "Déconnexion", "Vous avez été déconnecté.")
        self.close()

    def scan_network(self):
        # Cette méthode est maintenant gérée par un autre thread
        pass

    def start_spoofing(self):
        if not self.devices:
            QMessageBox.warning(self, "Pas de périphériques", "Aucun appareil détecté pour le spoofing.")
            return
        try:
            start_spoofing(self.devices)
            self.status_label.setText("Spoofing en cours...")
            QMessageBox.information(self, "Spoofing", "Spoofing réseau démarré.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors du spoofing : {e}")

    print("Avant update_device_table")
    def update_device_table(self, device):
        print("update_device_table appelée")
        # Mettre à jour le tableau avec les nouvelles données
        row_position = self.devices_table.rowCount()
        self.devices_table.insertRow(row_position)
        self.devices_table.setItem(row_position, 0, QTableWidgetItem(device["name"]))
        self.devices_table.setItem(row_position, 1, QTableWidgetItem(device["ip"]))
        self.devices_table.setItem(row_position, 2, QTableWidgetItem(device["mac"]))
        
   
if __name__ == "__main__":
    app = QApplication([])

    # Charger la session utilisateur
    username = load_session()
    if username:
        print(f"Connexion réussie pour {username}.")
        window = ARPSpooferApp(username)
        
        # Message de debug avant d'afficher la fenêtre
        print("Initialisation de la fenêtre...")
        
        window.show()
    else:
        # Lancer la fenêtre de connexion
        login_window = LoginWindow()
        if login_window.exec() == QDialog.DialogCode.Accepted:
            username = login_window.username_entry.text()

            # Vérifier si le nom d'utilisateur est vide
            if not username.strip():
                QMessageBox.critical(None, "Erreur", "Le nom d'utilisateur ne peut pas être vide.")
                exit(1)

            # Sauvegarder la session utilisateur
            save_session(username)

            print(f"Utilisateur {username} connecté.")
            window = ARPSpooferApp(username)
            
            # Message de debug avant d'afficher la fenêtre
            print("Initialisation de la fenêtre...")
            
            window.show()
        else:
            print("Connexion annulée par l'utilisateur.")
            exit(0)

    app.exec()
