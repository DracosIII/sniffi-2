import pymysql
import hashlib
import os

# Paramètres de connexion à la base de données
host = "sniffi.cli6wkgcach0.us-east-1.rds.amazonaws.com"
port = 3306
user = "admin"
password = "5486201379"
database = "sniffi"
SESSION_FILE = "session.txt"

def get_connection():
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    hashed_password = hash_password(password)
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            connection.commit()
        print("Utilisateur inscrit avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'inscription : {e}")
    finally:
        connection.close()

def login_user(username, password):
    hashed_password = hash_password(password)
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                print(f"Connexion réussie pour {username}.")
                return user[0]  # Retourne l'ID utilisateur
            else:
                print("Nom d'utilisateur ou mot de passe incorrect.")
                return None
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        return None
    finally:
        connection.close()

def load_session():
    """Charge le nom d'utilisateur à partir du fichier de session."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            return file.read().strip()
    return None

def save_session(username):
    """Sauvegarde le nom d'utilisateur dans un fichier de session."""
    with open(SESSION_FILE, "w") as file:
        file.write(username)
        
def clear_session():
    """Efface les informations de session."""
    if os.path.exists("session.txt"):
        os.remove("session.txt")
        
def create_tables_for_user(user_id):
    """Crée les tables spécifiques à l'utilisateur."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Table des logs de périphériques
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `sniffi.{user_id}.logs` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_name VARCHAR(255),
                    mac_address VARCHAR(17),
                    ip_address VARCHAR(15),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table des paquets sniffés
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `sniffi.{user_id}.sproof` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    src_ip VARCHAR(15),
                    dst_ip VARCHAR(15),
                    protocol VARCHAR(10),
                    length INT,
                    timestamp DOUBLE
                )
            """)
            connection.commit()
    except Exception as e:
        print(f"Erreur lors de la création des tables pour l'utilisateur {user_id} : {e}")
    finally:
        connection.close()

def insert_device_log(user_id, device_name, mac_address, ip_address):
    """Insère un log de périphérique dans la table correspondante."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO `sniffi.{user_id}.logs` (device_name, mac_address, ip_address)
                VALUES (%s, %s, %s)
            """, (device_name, mac_address, ip_address))
            connection.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion du log de périphérique : {e}")
    finally:
        connection.close()

def insert_packet_data(user_id, src_ip, dst_ip, protocol, length, timestamp):
    """Insère un paquet sniffé dans la table correspondante."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO `sniffi.{user_id}.sproof` (src_ip, dst_ip, protocol, length, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (src_ip, dst_ip, protocol, length, timestamp))
            connection.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion du paquet : {e}")
    finally:
        connection.close()
