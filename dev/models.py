from . import db

class User:
    def __init__(self):
        self.pseudo = ""
        self.firstname = ""
        self.lastname = ""
        self.sexe = ""
        self.email = ""
        self.adress = ""
        self.city = ""
        self.postalcode = ""
        self.phone = ""
        self.datebirthday = ""
        self.password = ""
        self.temporarypassword = ""
        self.isadmin = ""

    def __repr__(self):
        return "{} : {}".format(self.pseudo, self.email)

    def check_value(self, column:str, value:str) -> bool:
        if db.is_value_in_column("User", column, value):
            return True
        else:
            return False

    def add_user_in_database(self) :
        db.new_user(self)

    def modify_personal_informations_in_database(self) :
        db.update_user_informations(self)

    def delete_account_in_database(self) :
        db.delete_user(self)
