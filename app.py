from flask import Flask, render_template, flash, redirect, url_for, request
from forms import RegistrationForm, LoginForm
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="ticketsystem"
            )
            cursor = mydb.cursor()

            sql = "INSERT INTO `user` (vorname, nachname, email, plz, stadt, strasse, passwort, rollen_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            if form.rolle.data == 'Lehrkraft':
                rollen_id = 1
            else:
                rollen_id = 2

            val = (form.vorname.data, form.nachname.data, form.email.data, form.plz.data, form.stadt.data, form.strasse.data, generate_password_hash(form.kennwort.data), rollen_id)
            cursor.execute(sql, val)
            mydb.commit()

            flash('Sie haben sich erfolgreich registriert!')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f"Fehler beim Einfügen in die Datenbank: {err}")
            flash('Fehler bei der Registrierung. Bitte versuchen Sie es erneut.')
        finally:
            if mydb.is_connected():
                cursor.close()
                mydb.close()
    return render_template('register.html', title='Registrieren', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="ticketsystem"
            )
            cursor = mydb.cursor()

            # Überprüfen, ob der Benutzer existiert
            cursor.execute("SELECT * FROM `user` WHERE email = %s", (form.email.data,))
            user = cursor.fetchone()

            if user and check_password_hash(user[7], form.kennwort.data):  # Index 7 ist das Passwortfeld in der Datenbank
                # Hier würdest du normalerweise die Benutzeranmeldung durchführen (z.B. mit Flask-Login)
                flash('Anmeldung erfolgreich!')
                # Weiterleitung zur Startseite oder Dashboard nach erfolgreicher Anmeldung
                return redirect(url_for('index')) 
            else:
                flash('Ungültige E-Mail-Adresse oder Passwort')
        except mysql.connector.Error as err:
            print(f"Fehler bei der Datenbankabfrage: {err}")
            flash('Fehler bei der Anmeldung. Bitte versuchen Sie es erneut.')
        finally:
            if mydb.is_connected():
                cursor.close()
                mydb.close()
    return render_template('login.html', title='Anmelden', form=form)

@app.route('/')
def index():
    return "Willkommen!"  # Oder render_template('index.html') für eine Startseite

if __name__ == '__main__':
    app.run(debug=True)