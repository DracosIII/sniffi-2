import scapy.all as scapy
import netifaces as ni
import socket
import time
from PyQt6.QtCore import pyqtSignal, QObject

class NetworkScanner(QObject):
    # Déclaration du signal pour notifier la détection d'un appareil
    device_detected_signal = pyqtSignal(dict)

    def get_local_network(self):
        try:
            interface = ni.gateways()['default'][ni.AF_INET][1]
            ip_info = ni.ifaddresses(interface)[ni.AF_INET][0]
            ip_address = ip_info['addr']
            netmask = ip_info['netmask']
            network = f"{ip_address}/{sum(bin(int(x)).count('1') for x in netmask.split('.'))}"
            return network
        except Exception as e:
            print(f"Erreur lors de la détection du réseau : {e}")
            return None

    def get_device_name(self, ip):
        try:
            host = socket.gethostbyaddr(ip)
            return host[0]
        except socket.herror:
            return "Inconnu"

    def scan_network(self):
        devices = []
        network = self.get_local_network()
        if not network:
            return devices

        try:
            arp_request = scapy.ARP(pdst=network)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request

            answered_list = scapy.srp(arp_request_broadcast, timeout=5, verbose=False)[0]

            for sent, received in answered_list:
                device = {
                    "ip": received.psrc,
                    "mac": received.hwsrc,
                    "name": self.get_device_name(received.psrc)
                }
                self.device_detected_signal.emit(device)  # Émettre un signal avec l'appareil détecté
                devices.append(device)

        except Exception as e:
            print(f"Erreur pendant le scan réseau : {e}")

        return devices

    # Fonction pour scanner en continu
    def continuous_scan(self):
        while True:
            self.scan_network()
            time.sleep(5)  # Scanner toutes les 5 secondes

