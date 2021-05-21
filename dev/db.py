import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext

from . import models

### GESTION DE LA BD ###
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource(current_app.config['PATH'] + '/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    # new_user(pseudo="Baratinus", sexe="homme", email="p.baratinus@gmail.com", datebirthday="09/06/2003", password="azerty")

def gestion_db(function):
    """Décorateur pour éviter la répétiton de code
    """
    def function_decorator(*args):
        db = get_db()
        cur = db.cursor()
        f = function(*args, cursor=cur)
        # sauvegarder les changements
        db.commit()
        cur.close()
        return f
    return function_decorator
### FIN DE LA GESTION DE LA BD ###

### FONCTIONS DE LA BD UTILISATEUR ###
@gestion_db
def new_user(user:models.User, cursor:sqlite3.Cursor=None):
    cursor.execute(f"INSERT INTO User (pseudo,firstname,lastname,sexe,email,adress,city,postalcode,phone,datebirthday,password,temporarypassword,isadmin) VALUES ('{user.pseudo}','{user.firstname}','{user.lastname}','{user.sexe}','{user.email}','{user.adress}','{user.city}','{user.postalcode}','{user.phone}','{user.datebirthday}','{user.password}', '{user.temporarypassword}','{user.isadmin}')")

@gestion_db
def delete_user(user:models.User, cursor:sqlite3.Cursor=None) :
    cursor.execute(f"DELETE FROM User WHERE pseudo=? ", user.pseudo)

@gestion_db
def get_user(column:str, value:str, /, cursor:sqlite3.Cursor=None) -> models.User:
    """obtenir les informations d'un utilisateur en fonction de l'email

    Args:
        column (str): non de la colonne (vf schema.sql), attention mettre une colonne à valeur UNIQUE
        value (str): valeur de la colonne respective
        cursor (sqlite3.Cursor, optional): ne pas remplir. Defaults to None.

    Returns:
        models.User: utilisateur, si aucun utilisateur existe renvoie None
    """
    cursor.execute(f"SELECT * FROM User WHERE {column}='{value}'")
    try:
        param = cursor.fetchall()[0]
        user = models.User()
        user.pseudo = param[0]
        user.firstname = param[1]
        user.lastname = param[2]
        user.sexe = param[3]
        user.email = param[4]
        user.adress = param[5]
        user.city = param[6]
        user.postalcode = param[7]
        user.phone = param[8]
        user.datebirthday = param[9]
        user.password = param[10]
        user.temporarypassword = param[11]
        user.isadmin = param[12]
        return user
    except:
        return None

### FIN DES FONCTIONS DE LA BD UTILISATEUR ###

### FONCTIONS DE RECUPERATION D'INFORMATIONS ###
@gestion_db
def is_value_in_column(table:str, column:str, value:str, /, cursor:sqlite3.Cursor=None) -> bool:
    cursor.execute(f"SELECT {column} FROM {table} WHERE {column}='{value}'")
    a = len(cursor.fetchall())
    return(a != 0)

@gestion_db
def get_table(table:str, /, cursor:sqlite3.Cursor=None) -> tuple:
    result = [] 
    for p in cursor.execute(f"SELECT * FROM {table}"):
        result.append(tuple([e for e in p]))
    return tuple(result)
### FIN DES FONCTIONS DE RECUPERATION D'INFORMATIONS ###