from flask import Flask,render_template,request,redirect,url_for,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4

from . import db
from . import models
from . import passwordcheck
from . import pseudocheck

app = Flask(__name__)
app.secret_key = b'\xd7\xbd\xa4\xdf\xbd\x0e\xdds\xdd\xdd\x03\x1f\xc9\xe1\xa4U'

app.config.from_object('config')

### Les Routes ###
@app.route('/')    
@app.route('/index/', methods=['GET'])
def index():
    return render_template("index.html", user_pseudo = getpseudo())



@app.route('/register/', methods=['POST', 'GET'])
def register():
    ''' 
    Fonction permettant de se s'enregistrer.
    '''
    if request.method == 'GET' :
        return render_template("register.html")

    else :
        user = models.User()
        if pseudocheck.checkPseudo((request.form['pseudo'])) == True :
            user.pseudo = request.form["pseudo"]
        else :
            flash("Pseudo Invalide, Recommencez", "error")
            return redirect(url_for('register'))   

        if (user.check_value("pseudo", request.form["pseudo"]) or user.check_value("email", request.form["email"])):
            flash("Pseudo ou email déjà existant", "error")
            return redirect(url_for('login'))

        else:
            user.firstname = request.form["firstname"].capitalize()
            user.lastname = request.form["lastname"].upper()
            user.sexe = request.form["sexe"]
            user.email = request.form["email"]
            user.adress = str(request.form["adresse"])
            user.city = request.form["ville"]
            user.postalcode = request.form["cp"]
            user.phone = request.form["telephone"]
            user.datebirthday = request.form["birthday"]
            user.temporarypassword = "NO"
            user.isadmin = "NO"


            if passwordcheck.checkPassword((request.form["password"])) == True :
                user.password = generate_password_hash(request.form["password"], method='sha256', salt_length=8)
                user.add_user_in_database()
            else : 
                flash("Mot de passe invalide", "error")
                return redirect(url_for('register'))
           
            # Connexion lors de l'enregistrement
            session["user"] = user.pseudo

            return render_template("index.html", user_pseudo = getpseudo())


@app.route('/login/', methods=['POST','GET'])
def login():
    ''' 
    Fonction permettant de se connecter.
    '''
    if request.method == 'GET' :
        return render_template("login.html")
    
    else :
        user = db.get_user("email", request.form["email"])

        if user == None:
            flash("Identifiants incorrects, veuillez vérifier votre email ou mot de passe.", "error") #Cas adresse email inexistante.
            return redirect(url_for('login'))
        
        elif check_password_hash(user.password, request.form["password"]) == True:
            session["user"] = user.pseudo
            print("Utilisateur : {user}".format(user = session["user"]) )

            if user.temporarypassword == "YES" :
                return render_template("CREATE_A_TEMPLATE:Change Password", user_pseudo = getpseudo())
            else :
                return render_template("index.html", user_pseudo = getpseudo())

        else:
            flash("Identifiants incorrects, veuillez vérifier votre email et mot de passe.", "error") #Cas mot de passe incorrect.
            return redirect(url_for('login'))

@app.route('/logout/', methods=['GET'])
def logout():
    ''' 
    Fonction permettant de se déconnecter.
    '''
    try:
        session["user"]
        session.clear()
    except KeyError :
        return render_template("index.html", user_pseudo = getpseudo())
    else:
        return render_template("index.html", user_pseudo = getpseudo())

@app.route('/profil/', methods=['GET'])
def profil():
    ''' 
    Fonction permettant d'accéder au profil de l'utilisateur.
    '''
    try:
        session["user"]
    except KeyError:
        return redirect(url_for('login'))
    else:
        user_ = db.get_user('pseudo', session['user'])
        if len(user_.firstname) == 0 :
            user_.firstname = 'Unknown'
        if len(user_.lastname) == 0 :
            user_.lastname = 'Unknown' 
        if len(user_.adress) == 0 :
            user_.adress = 'Unknown'
        if len(user_.city) == 0 :
            user_.city = 'Unknown'
        if len(user_.postalcode) == 0 :
            user_.postalcode = 'Unknown'
        if len(user_.phone) == 0 :
            user_.phone = 'Unknown'
        user_.datebirthday = formatdateprofil()
        user_.phone = formatphoneprofil()

        return render_template("profil.html", user=user_ , user_pseudo = getpseudo())

### La Gestion des Erreurs ###
@app.errorhandler(404)
def err404(error):
    return render_template('404.html', user_pseudo = getpseudo())


### Les utilitaires ###
def getpseudo() -> str:
    ''' 
    Fonction permettant d'obtenir le pseudo d'un utilisateur en fonction de si il est authentifié ou non.
    '''
    try :
        session['user']
    except KeyError :
        user_session = ''
    else :
        user = db.get_user('pseudo', session['user'])
        user_session = user.pseudo        
    return user_session

def formatdateprofil():
    ''' 
    Fonction permettant de mettre la date au format JJ/MM/AAAA
    '''
    user_ = db.get_user('pseudo', session['user'])
    birthdate = user_.datebirthday.split("-")
    new_birthday = birthdate[2] + '-' + birthdate[1] + '-' + birthdate[0]
    return new_birthday

def formatphoneprofil():
    ''' 
    Fonction permettant de mettre le numéro au format FR ou EN
    '''
    user_ = db.get_user('pseudo', session['user'])
    phonenumber = user_.phone
    if len(phonenumber) == 12 :
        new_phonenumber = phonenumber[:3] + ' ' + phonenumber[-9:-8] + ' ' + phonenumber[-8:-6] + ' ' + phonenumber[-6:-4] + ' ' + phonenumber[-4:-2] + ' ' + phonenumber[-2:]
        return new_phonenumber
    elif len(phonenumber) == 10 :
        return phonenumber[:2] + ' ' + phonenumber[-8:-6] + ' ' + phonenumber[-6:-4] + ' ' + phonenumber[-4:-2] + ' ' + phonenumber[-2:]
    else :
        return user_.phone


app.run(debug=True, port=app.config["PORT"], host=app.config["IP"])
