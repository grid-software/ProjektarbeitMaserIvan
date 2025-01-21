from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
from forms import RegistrationForm, LoginForm, TicketForm
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from wtforms import fields

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
@app.route('/')
def index():
    if 'user_id' in session:
        # Benutzer ist angemeldet
        user_id = session['user_id']
        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Abrufen der Tickets für den angemeldeten Benutzer
        cursor.execute("""
            SELECT t.id, t.title, s.beschreibung as status, r.raum_code, u.vorname, u.nachname 
            FROM ticket t 
            JOIN `user` u ON t.user_id = u.id 
            JOIN status s ON t.status_id = s.id 
            JOIN raum r ON t.raum_id = r.id  
            WHERE t.user_id = %s
        """, (user_id,))
        tickets = cursor.fetchall() 
        tickets = cursor.fetchall()

        # Überprüfen, ob der Benutzer eine Lehrkraft ist
        cursor.execute("SELECT rollen_id FROM `user` WHERE id = %s", (user_id,))
        rolle = cursor.fetchone()[0]

        if rolle == 1:  # 1 entspricht der Rolle "Lehrkraft"
            form = TicketForm()
            if form.validate_on_submit():
                try:
                    # Ticketdaten in die Datenbank einfügen
                    sql = "INSERT INTO ticket (user_id, raum_id, title, beschreibung, status_id, erstellungsdatum) VALUES (%s, %s, %s, %s, %s, CURDATE())"
                    val = (user_id, form.raum.data, form.titel.data, form.beschreibung.data, 1)  # 1 entspricht dem Status "offen"
                    cursor.execute(sql, val)
                    mydb.commit()
                    flash('Ticket erfolgreich erstellt!')
                    return redirect(url_for('index'))
                except mysql.connector.Error as err:
                    print(f"Fehler beim Einfügen des Tickets: {err}")
                    flash('Fehler beim Erstellen des Tickets.')
                finally:
                    if mydb.is_connected():
                        cursor.close()
                        mydb.close()
            return render_template('ticketseite.html', user_id=user_id, tickets=tickets, form=form,rolle=rolle)
        else:
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



@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Benutzer aus der Sitzung entfernen
    return redirect(url_for('login'))

@app.route('/keinRaum')
def keinRaum():
    return render_template('kein_Raum.html')

if __name__ == '__main__':
    app.run(debug=True)