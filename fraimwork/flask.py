from flask import Flask

app = Flask(__name__)  # Crée une instance de l'application Flask

@app.route("/")  # Définir la route pour la page d'accueil
def home():
    return "Bienvenue sur mon application Flask !"

if __name__ == "__main__":
    app.run(debug=True)  # Lancer le serveur en mode debug
