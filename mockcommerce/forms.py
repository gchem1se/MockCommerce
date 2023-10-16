from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, TelField, EmailField, HiddenField, DateField, FloatField, FileField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from .models import Product

MIN_USERNAME_LENGTH = 5
MAX_USERNAME_LENGTH = 20
MIN_PASSWORD_LENGTH = 8
MAX_PRODUCT_NAME_LENGTH = 250
MAX_PRODUCT_DESCRIPTION_LENGTH = 2500

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=MIN_USERNAME_LENGTH, max=MAX_USERNAME_LENGTH)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=MIN_PASSWORD_LENGTH)])

class SigninForm(LoginForm):
    pass

class AddToCartForm(FlaskForm):
    ### for handling adding to session cart the current product
    prodID = HiddenField(validators=[DataRequired()])
    quantity = IntegerField('Quantità', validators=[DataRequired()])
    purchasePrice = HiddenField(validators=[DataRequired()])

class RemoveForm(FlaskForm):
    ### for handling remove buttons
    prodID = HiddenField(validators=[DataRequired()])

class CheckoutForm(FlaskForm):
    userID = HiddenField(validators=[DataRequired()])
    purchaseDate = HiddenField(validators=[DataRequired()]) 
    orders = HiddenField(validators=[DataRequired()]) 
    # ^^ will contain a JSON string with orders data, make sure to add a server-side validation of this

    shippingName = StringField('Nome', validators=[DataRequired()]) 
    shippingSurname = StringField('Cognome', validators=[DataRequired()]) 
    shippingNation = StringField('Nazione', validators=[DataRequired()])
    shippingProvince = StringField('Provincia', validators=[DataRequired()])
    shippingCity = StringField('Città', validators=[DataRequired()]) 
    shippingStreet = StringField('Via', validators=[DataRequired()])
    shippingHouseNumber = StringField('Civico', validators=[DataRequired()])
    shippingPostalCode = StringField('CAP', validators=[DataRequired()]) 
    shippingPhone = TelField('Cellulare')
    shippingEmail = EmailField('Email', validators=[Email()])

    cardNumber = StringField('Numero della carta', validators=[DataRequired()])
    expiryDate = DateField('Scadenza', validators=[DataRequired()])
    securityCode = StringField('CVV', validators=[DataRequired()])

class AlterProductForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=MAX_PRODUCT_NAME_LENGTH)]) 
    description = TextAreaField('Descrizione', validators=[DataRequired(), Length(max=MAX_PRODUCT_DESCRIPTION_LENGTH)]) 
    category = SelectField('Categoria', validators=[DataRequired()]) 
    img = FileField('Immagine')
    # ^^ I can't set validators after construction. It simply does not work. Dunno y.
    price = FloatField('Prezzo', validators=[DataRequired()]) 
    availability = IntegerField('Disponibilità', validators=[DataRequired()]) 
    lastUpdateDate = HiddenField(validators=[DataRequired()]) 

    def set_categories(self, categories):
        self.category.choices = [(x.id, x.name) for x in categories]

    def set_default_values(self, product:Product):
        self.name.data = product.name
        self.description.data = product.description
        self.category.data = str(product.category.id)
        # ^^ select's options IDs are strings
        self.price.data = product.price
        self.availability.data = product.availability