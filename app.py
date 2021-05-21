from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app=Flask(__name__)

conn = sqlite3.connect('répértoire.db',check_same_thread=False)
cur = conn.cursor()


def creer_table():
    cur.execute('CREATE TABLE IF NOT EXISTS PERSONNES(nom TEXT, prenom TEXT, adresse_mail TEXT)')
    conn.commit()


def ajouter_personne(donnes):
    ''' dans données mettre dans un tuple
    et dans l'odre de la table les données a inserer dans la table en STR'''
    data = donnes
    cur.execute('INSERT INTO PERSONNES(nom, prenom, adresse_mail) VALUES (?,?,?)', data)
    conn.commit()


def modifier(donnees, place):
    '''dans données mettre les variables a changer
    et la valeur qui servira de repere et
    dans place mettre le nom des valeur a changer tjr dans des TUPLE et
    dans le meme ordreet le tout en STR'''
    modif = donnees
    cur.execute('UPDATE PERSONNES SET ' + str(place[0]) + '=? WHERE ' + str(place[1]) + '=?', modif)
    conn.commit()


def supprimer(donnees, place):
    '''pareil que  pour modifier '''
    data = donnees
    cur.execute('DELETE FROM PERSONNES WHERE ' + str(place) + '=?', data)
    conn.commit()


def select(donnees, place):
    '''pareil que pour modifier et suprimmer'''
    data = (str(donnees),)
    cur.execute('SELECT nom, prenom, adresse_mail FROM PERSONNES WHERE ' + str(place) + '=?', data)
    conn.commit()
    liste = cur.fetchall()
    return liste


def fermer_fenetre():
    '''à utiliser quand on ferme la page web pour arreter la table'''
    cur.close()
    conn.close()


@app.route('/')
def index():
    if request.method == 'POST':
        return render_template('template2.html')
    else:
        return render_template('templates.html')

@app.route('/post-login', methods=['get', 'post'])
def login():
    if request.method == 'post':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        ajouter_personne((nom,prenom,email))
        return render_template('template2.html')

@app.route('/create', methods=['get', 'post'])
def create():
    return render_template('template3.html')

@app.route('/suppr/', methods = ['get','post'])
def suppr():
    if request.method == 'post':
        email = request.form['emails']
        supprimer((email),('adresse_mail'))
        return render_template('templates.html')
    else:
        return render_template('templates.html')


#creer_table()
#ajouter_personne(('VINCENT', 'Guilhem', 'guilhem10v@live.fr'))
#modifier(('Vincent3', 'guilhem10v@live.fr'), ('nom', 'adresse_mail'))
#print(select(('guilhem10v@live.fr'), ('adresse_mail')))
#suprimmer(('Vincent3'), ('nom'))
#fermer_fenetre()

if __name__ == "__main__":
    app.run( host='192.168.1.72', port = '5000')
