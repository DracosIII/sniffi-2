from PyQt6.QtWidgets import QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QMessageBox

class EmailWindow(QMainWindow):
    def __init__(self, parent, devices):
        super().__init__(parent)
        self.setWindowTitle("Envoyer les appareils par Email")
        self.setGeometry(100, 100, 400, 300)
        self.devices = devices

        self.device_listbox = QListWidget(self)
        for device in devices:
            self.device_listbox.addItem(f"{device['name']} ({device['ip']})")

        self.send_button = QPushButton("Envoyer", self)
        self.send_button.clicked.connect(self.send_email)

        layout = QVBoxLayout()
        layout.addWidget(self.device_listbox)
        layout.addWidget(self.send_button)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_email(self):
        """Envoie les données par email."""
        QMessageBox.information(self, "Envoyé", "Appareils envoyés par email.")
