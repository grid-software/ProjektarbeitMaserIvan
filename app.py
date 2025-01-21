from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
from forms import RegistrationForm, LoginForm
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'extremgeheimerkey'  # Ersetze dies durch einen sicheren Schlüssel!

# Funktion für die Datenbankverbindung
def get_db_connection():
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="ticketsystem"
    )
    return mydb

@app.route('/', methods=['GET','POST'])
def Ticketsystem():
    if 'user_id' in session:
        user_id = session['user_id']
        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Hier musst du die Abfrage an deine Tabellenstruktur anpassen
        cursor.execute("SELECT t.id, t.title, s.beschreibung as status FROM ticket t JOIN `user` u ON t.user_id = u.id JOIN status s ON t.status_id = s.id WHERE u.id = %s", (user_id,))
        tickets = cursor.fetchall()

        cursor.close()
        mydb.close()

        return render_template('ticketseite.html', user_id=user_id, tickets=tickets)

    else:
        return redirect((url_for('login')))
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            mydb = get_db_connection()
            cursor = mydb.cursor()

            sql = "INSERT INTO `user` (vorname, nachname, email, plz, stadt, strasse, passwort, rollen_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            if form.rolle.data == 'Lehrkraft':
                rollen_id = 1
            else:  # Raumbetreuer
                rollen_id = 2

            val = (form.vorname.data, form.nachname.data, form.email.data, form.plz.data, form.stadt.data, form.strasse.data, generate_password_hash(form.kennwort.data), rollen_id)
            cursor.execute(sql, val)
            mydb.commit()

            if form.rolle.data == 'Raumbetreuer':
                return redirect(url_for('raum_auswahl', user_id=cursor.lastrowid))  # Weiterleitung zur Raumauswahl
            else:
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

@app.route('/raum_auswahl/<int:user_id>', methods=['GET', 'POST'])
def raum_auswahl(user_id):
    mydb = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT id, raum_code FROM raum WHERE raumbetreuuer IS NULL")
    räume = cursor.fetchall()

    if not räume:  # Überprüfen, ob freie Räume verfügbar sind
        flash('Keine freien Räume verfügbar.')
        return redirect(url_for('keinRaum'))  # Oder eine andere Seite, falls gewünscht


    if request.method == 'POST':
        try:
            ausgewählte_räume = request.form.getlist('räume')
            for raum_id in ausgewählte_räume:
                update_sql = "UPDATE raum SET raumbetreuuer = %s WHERE id = %s"
                cursor.execute(update_sql, (user_id, raum_id))
            mydb.commit()
            flash('Räume erfolgreich zugewiesen!')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f"Fehler beim Zuweisen der Räume: {err}")
            flash('Fehler beim Zuweisen der Räume.')
        finally:
            if mydb.is_connected():
                cursor.close()
                mydb.close()

    return render_template('raum_auswahl.html', title='Räume auswählen', räume=räume, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        try:
            mydb = get_db_connection()
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM `user` WHERE email = %s", (form.email.data,))
            user = cursor.fetchone()

            if user and check_password_hash(user[7], form.kennwort.data):
                flash('Anmeldung erfolgreich!')
                session['user_id'] = user[0]  # Benutzer-ID in der Sitzung speichern
                return redirect(url_for('index'))
            else:
                error = 'Ungültige E-Mail-Adresse oder Passwort'
        except mysql.connector.Error as err:
            print(f"Fehler bei der Datenbankabfrage: {err}")
            flash('Fehler bei der Anmeldung. Bitte versuchen Sie es erneut.')
        finally:
            if mydb.is_connected():
                cursor.close()
                mydb.close()
    return render_template('login.html', title='Anmelden', form=form, error=error)

@app.route('/index')
def index():
    if 'user_id' in session:
        # Benutzer ist angemeldet
        user_id = session['user_id']
        # ... hier kannst du die Benutzerdaten laden und im Template verwenden ...
        return render_template('ticketseite.html', user_id=user_id) 
    else:
        # Benutzer ist nicht angemeldet
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Benutzer aus der Sitzung entfernen
    return redirect(url_for('login'))

@app.route('/keinRaum')
def keinRaum():
    return render_template('kein_Raum.html')

if __name__ == '__main__':
    app.run(debug=True)