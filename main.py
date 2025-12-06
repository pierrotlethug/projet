# Flask : Classe principale, initialise l'app
# render_template : Charge et compile les templates Jinja2
# session : Stockage côté serveur des données utilisateur
# request : Accès aux données de la requête HTTP
# url_for : Génération dynamique des URLs
# redirect : Redirection HTTP vers une autre route

# On importe mongodb, os, bcrypt (chiffrement des mdps)
import pymongo, os, bcrypt, random
# On import du framework flask :
# * la classe Flask
# * render_template fonction qui permet d'afficher un fichier HTML
from flask import Flask, render_template, session, request, url_for, redirect
# On crée une variable qui stocke une instance de la classe Flask
app = Flask(__name__)

# On crée une clef de chiffrement -> obligatoire pour utiliser session => elle signe et chiffre les cookies
# On crée une valeur au hasard de 24 bits
app.secret_key = os.urandom(24)

# Connexion database
mongo = pymongo.MongoClient("mongodb+srv://someoneuserdb:Pierre2811!@cluster0.eqv96ae.mongodb.net/?appName=Cluster0")


wrongUsernameMsgs = ["Nom d'utilisateur déjà choisi, veuillez changer", "Pas bon non plus, réessayez", "Toujours pas.", "Pff... Toujours pas.", "EH BIEN NON !", "Mais fais preuve d'originalité à la fin !", "Tu le fais exprès, c'est ça ?", "Tu n'en as pas marre ?", "Bon je te laisse", "Nom d'utilisateur déjà choisi, veuillez changer"]
wrongPWMsgs = ["Veuillez renseigner les mêmes mots de passe", "Veuillez renseigner les mêmes mots de passe, s'il vous plait ?", "VEUILLEZ RENSEIGNER LES MÊMES MOTS DE PASSE !", "Pardon, mais franchement, renseignez les mêmes mots de passe svp.", "Petite astuce : Ctrl+C, Ctrl+V", "Ça ne marche pas ?", "Bon, j'en ai marre", "Veuillez renseigner les mêmes mots de passe"]
# On crée un route de notre page d'accueil
@app.route('/')
def index():
    # # On récupère la collection annonces de notre base de données
    db_annonces = mongo.db.annonces
    annonces =  db_annonces.find({})
    if 'utilisateur' in session :
       return render_template("index.html", annonces = annonces, utilisateur = session["utilisateur"])
    else :
       return render_template("index.html", annonces = annonces)


# On crée le route pour l'inscription de l'utilisateur
@app.route('/register', methods = ['GET', 'POST'] )
def register():
    # On vérifie si la méthode est POST pour traiter le formulaire reçu
    if request.method == "POST": 
    # on récupère la table "utilisateurs" de notre base de données 
        db_users = mongo.db.utilisateurs
        # On vérifie que le nom d'utilisateur n'est pas existant
        if db_users.find_one({"nom":request.form['utilisateur']}):
           return render_template("register.html", erreur = random.choice(wrongUsernameMsgs))
        else :
            # On ajoute l'utilisateur à bdd après avoir chiffiré son mdp, si les mots de passe fournis sont égaux
            if request.form['mot_de_passe'] == request.form['verif_mot_de_passe']:
                # On chiffre le mdp avec hashpw 
                # gensalt pour hacher le mdp
                mot_de_passe_chiffre = bcrypt.hashpw(
                    request.form['mot_de_passe'].encode('utf-8'),
                    bcrypt.gensalt()
                )
                db_users.insert_one({
                    "nom": request.form['utilisateur'],
                    "mdp": mot_de_passe_chiffre})
                # On ajoute le cookie utilisateur de connexion
                session["utilisateur"] = request.form['utilisateur']
                return redirect(url_for('index'))
            else :
                # On affiche l'erreur les mdps sont différents
                return render_template("register.html", random.choice(wrongPWMsgs))

    # Autrement si c'est GET on affiche la page
    else : 
        return render_template("register.html")

# On crée le route pour la connexion de l'utilisateur
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # On vérifie si la méthode est POST pour traiter le formulaire reçu
    if request.method == "POST": 
    # on récupère la table "utilisateurs" de notre base de données 
        db_users = mongo.db.utilisateurs
        # On vérifie que le nom d'utilisateur n'est pas existant
        user = db_users.find_one({"nom":request.form['utilisateur']})
        if user : 
            # On verifie avec la fonction checkpw si le mdp du formulaire correspond au mdp de la base de données
            if bcrypt.checkpw(request.form["mot_de_passe"].encode('utf-8'), user["mdp"]):
                # On ajoute le cookie utilisateur de connexion
                session["utilisateur"] = request.form['utilisateur']
                return redirect(url_for('index'))
        # Sinon on affiche l'erreur 
        return render_template("login.html", erreur = "Les identifiants ne sont pas reconnus")

    # Si c'est GET 
    else :
        # On affiche la page de connexion
        return render_template("login.html")

# On crée le route pour la déconnexion de l'utilisateur
@app.route("/logout")
def logout():
    # On supprime le cookie de connexion de notre dictionnaire session
    session.clear()
    return redirect(url_for("index"))

# On créer le route pour la publication d'une annonce
@app.route("/publier_annonce", ['GET', 'POST'])
@app.route("/publier_annonce", methods = ['GET', 'POST'])
def publier_annonce():
    # On vérifie que l'utilisateur est connecté
    if "utilisateur" in session :
        # (POST) On vérifie s'il tente de poster ou d'afficher la page pour poster 
        if request.method == "POST":
            # On récupère la collection qui stockent les annonces 
            db_annonces = mongo.db.annonces

            ### A FINIR 
            # On verifie que description et title ne sont pas vide
                # On envoie l'annonce dans la bdd et on retourne sur la page d'accueil
            # Sinon erreur

        # (GET) On affiche la page pour publier 
        else:
            return render_template("publier_annonce.html")
    # On redirige vers la connexion
    else :
        return redirect(url_for("logoin"))


# On teste notre base de données
@app.route('/test')
def test():
    db_test = mongo.db.test
    test = db_test.find({})
    return render_template("test.html", test=test)

# On exécute de notre application flask à laquelle on accède via le port 4200
if __name__ == "__main__":
    