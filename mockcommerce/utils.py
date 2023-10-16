from PIL import Image
from .forms import MIN_PASSWORD_LENGTH, MAX_USERNAME_LENGTH, MIN_USERNAME_LENGTH
import re
import datetime

IMG_MAX_WIDTH = 700
IMG_MAX_HEIGHT = 700
IMG_UPLOAD_DIRECTORY = "mockcommerce/static/img/products"

ALLOWED_CHARS_IN_PASSWORD = "[_*@$#!?=\-%]"

def upload_image(img, prodID):
    img = Image.open(img)

    width, height = img.size

    if height > 700:
        new_height = height/width * IMG_MAX_HEIGHT
        size = IMG_MAX_HEIGHT, new_height
    elif width > 700:
        new_width = height/width * IMG_MAX_WIDTH
        size = new_width, IMG_MAX_HEIGHT
    else:
        size = img.size

    img.thumbnail(size, Image.ANTIALIAS)

    img.save(IMG_UPLOAD_DIRECTORY+"/"+str(prodID)+".png", "PNG")

    return str(prodID)+".png"

def log(string):
    print("################################################")
    print(string)
    print("################################################")

class Messages:
    errGeneric = "Si è verificato un errore. Riprova"
    succAddToCart = "Il prodotto è stato aggiunto al carrello"
    succRemFromCart = "Il prodotto è stato rimosso dal carrello"
    succOrderSubmission = "L'acquisto è andato a buon fine"
    errNotAvailableAnymore = "Uno o più prodotti da te selezionati non sono più acquistabili. Ricontrolla il tuo carrello e riprova"
    errInvalidFields = "Dati inseriti non validi"
    errInvalidQuantities = "I prodotti non sono disponibili nelle quantità richieste. Ricontrolla il tuo carrello e riprova"
    errPricesChanged = "Il prezzo di uno o più prodotti è stati modificato dal venditore. Ricontrolla il tuo carrello e riprova"
    errOrderSubmission = "L'acquisto non è andato a buon fine. Riprova"
    succProductUnlisting = "Articolo rimosso"
    errImageUploading = "Si è verificato un errore nel caricamento dell'immagine. Riprova"
    succNewProductSubmission = "Articolo inserito"
    succUpdatingProduct = "Articolo modificato"
    errSignin = "Username già esistente"
    errSigninUsername = "Lo username deve essere lungo da {} a {} caratteri e non contenere caratteri speciali, eccetto '_'".format(MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH)
    errSigninPassword = "La password deve essere lunga almeno {} caratteri, e contenere lettere maiuscole e minuscole, numeri e caratteri speciali tra: {}, e non contenere spazi".format(MIN_PASSWORD_LENGTH, ALLOWED_CHARS_IN_PASSWORD[1:-1])
    loginMessage = "Accedi per proseguire"
    succSignin = "Iscrizione avvenuta"
    errLogin = "Credenziali non valide"
    errProductIsUnlisted = "Questo prodotto è stato rimosso dal venditore"
    errPhone = "Il cellulare inserito non è valido"
    errEmail = "L'email inserita non è valida"
    errPostalCode = "Il CAP inserito non è valido"
    errCardExpired = "La carta di credito inserita risulta scaduta"
    errCardNumber = "La carta di credito inserita non è valida"
    errCardCVV = "Il CVV inserito non è valido"
    errNegativePrice = "Il prezzo inserito non è valido"
    infoProductIsYours = "Questo prodotto è venduto da te"

def valid_password(password):
    valid = True
    if (len(password) < MIN_PASSWORD_LENGTH):
        valid = False
    elif not re.search("[a-z]", password):
        valid = False
    elif not re.search("[A-Z]", password):
        valid = False
    elif not re.search("[0-9]", password):
        valid = False
    elif not re.search(ALLOWED_CHARS_IN_PASSWORD, password):
        valid = False
    elif re.search("\s" , password):
        valid = False
 
    return valid

def valid_username(username):
    valid = True
    if (len(username) < MIN_USERNAME_LENGTH or len(username) > MAX_USERNAME_LENGTH):
        valid = False
    elif re.search("[^A-Za-z0-9_]", username):
        valid = False
    elif re.search("\s" , username):
        valid = False
 
    return valid

def valid_phone(phone):
    valid = True
    if re.search("[^0-9+]", phone):
        valid = False
    return valid

def valid_email(email):
    return re.match("^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$", email)

def valid_postal_code(cap):
    valid = True
    if re.search("[^0-9]", cap):
        valid = False
    return valid

def valid_card_expiry_date(exp):
    tomorrow = datetime.datetime.today() + datetime.timedelta(days = 1)
    expiry = datetime.datetime.strptime(exp, "%d/%m/%Y")

    return tomorrow - expiry < datetime.timedelta(days = 1)


def valid_card_number(number):
    valid = True
    if re.search("[^0-9]", number):
        valid = False
    return valid

def valid_CVV(cvv):
    return re.match("^[0-9][0-9][0-9]$", cvv)