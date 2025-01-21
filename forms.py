from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, SelectMultipleField, fields
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, EqualTo
import mysql.connector

class RegistrationForm(FlaskForm):
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    plz = IntegerField('PLZ', validators=[DataRequired()])
    stadt = StringField('Stadt', validators=[DataRequired()])
    strasse = StringField('Straße', validators=[DataRequired()])
    kennwort = PasswordField('Kennwort', validators=[DataRequired()])
    kennwort2 = PasswordField('Kennwort wiederholen', validators=[DataRequired(), EqualTo('kennwort')])
    rolle = SelectField('Rolle', choices=[('Lehrkraft', 'Lehrkraft'), ('Raumbetreuer', 'Raumbetreuer')], validators=[DataRequired()])
    submit = SubmitField('Registrieren')
    räume = SelectMultipleField('Räume', choices=[])  # Feld für die Raumauswahl


class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    kennwort = PasswordField('Kennwort', validators=[DataRequired()])
    submit = SubmitField('Anmelden')

class TicketForm(FlaskForm):
    titel = StringField('Titel', validators=[DataRequired()])
    beschreibung = fields.TextAreaField('Beschreibung', validators=[DataRequired()])
    raum = SelectField('Raum', choices=[], validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="ticketsystem"
        )
        cursor = mydb.cursor()
        cursor.execute("SELECT id, raum_code FROM raum")  # Abfrage für die Raumauswahl
        räume = cursor.fetchall()
        self.raum.choices = [(raum[0], raum[1]) for raum in räume]
        cursor.close()
        mydb.close()