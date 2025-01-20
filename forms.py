from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo

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

def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        mydb = get_db_connection()  # Datenbankverbindung holen
        cursor = mydb.cursor()

        # Raumauswahl nur anzeigen, wenn die Rolle "Raumbetreuer" ist
        if self.rolle.data == 'Raumbetreuer':
            print("test test123")
            # Nur freie Räume laden
            cursor.execute("SELECT id, raum_code FROM raum WHERE raumbetreuuer IS NULL")  
            räume = cursor.fetchall()
            self.räume.choices = [(raum[0], raum[1]) for raum in räume]  # choices für SelectMultipleField setzen

        cursor.close()
        mydb.close()