from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
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

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    kennwort = PasswordField('Kennwort', validators=[DataRequired()])
    submit = SubmitField('Anmelden')