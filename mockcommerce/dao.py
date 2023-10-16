from werkzeug.security import generate_password_hash, check_password_hash
from . import ngn
import sqlite3
from .models import Product, Category, Order, CumulativeOrder
from .utils import log

def get_user_id_by_username(username):
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row


    user = cnx.execute("SELECT ID FROM UTENTI WHERE USERNAME = ?", (username,)).fetchone()
    if user:
        userID = int(user.ID)
    else:
        userID = False
        
    cnx.close()
    
    return userID

def check_user_for_login(username, password):
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row

    userID = get_user_id_by_username(username)
    if userID:
        hashed_psw = cnx.execute("SELECT PSW_HASH FROM UTENTI WHERE ID = ?", (userID, )).fetchone().PSW_HASH
        if not check_password_hash(hashed_psw, password):
            userID = None

    cnx.close()
    
    return userID

def add_user(username, password):
    cnx = ngn.connect()

    userID = get_user_id_by_username(username)
    if userID:        
        # user already found
        return -1

    try:
        log("ADDING NEW USER")
  
        trans = cnx.begin()
    
        cnx.execute("INSERT INTO UTENTI('USERNAME', 'PSW_HASH') VALUES (?, ?)", (username, generate_password_hash(password)))
        trans.commit()
    
        cnx.close()

        log("USER ADDED SUCCESFULLY")

        return True
    except Exception as e:
        log(e)

        trans.rollback()

        cnx.close()
        return False

def get_user_by_id(userID):
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row

    user = cnx.execute("SELECT * FROM UTENTI WHERE ID = ?", (userID,)).fetchone()

    cnx.close()
    
    return user

def get_all_categories():
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row
    
    categorie = cnx.execute("SELECT * FROM CATEGORIE").fetchall()

    for i in range(len(categorie)):
        categorie[i] = Category(
            categoryID = int(categorie[i].ID), 
            name = categorie[i].NOME,
            description = categorie[i].DESCRIZIONE
        )

    cnx.close()

    return categorie


def get_product_by_id(productID):    
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row 

    articolo = cnx.execute("SELECT A.*, C.NOME AS C_NOME FROM ARTICOLI AS A, CATEGORIE AS C WHERE A.CATEGORIA = C.ID AND A.ID = ?", (productID, )).fetchone()

    articolo = Product(
        productID = int(articolo.ID), 
        name = articolo.NOME, 
        category = Category(categoryID = articolo.CATEGORIA, name = articolo.C_NOME),
        description = articolo.DESCRIZIONE, 
        img_path = articolo.IMG_PATH, 
        sellerID = int(articolo.ID_VENDITORE), 
        price = float(articolo.PREZZO), 
        availability = int(articolo.DISPONIBILITA),
        insertion_date = articolo.DATA_INSERIMENTO,
        last_update_date = articolo.DATA_ULTIMA_MODIFICA,
        selled = int(articolo.VENDUTI),
        status = int(articolo.STATO)

    )

    cnx.close()

    return articolo

def get_all_products():    
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row  

    articoli = cnx.execute("SELECT A.*, C.NOME AS C_NOME FROM ARTICOLI AS A, CATEGORIE AS C WHERE A.CATEGORIA = C.ID AND A.DISPONIBILITA <> 0 AND A.STATO <> 0").fetchall()

    for i in range(len(articoli)):
        articoli[i] = Product(
            productID = int(articoli[i].ID), 
            name = articoli[i].NOME, 
            category = Category(categoryID = articoli[i].CATEGORIA, name = articoli[i].C_NOME),
            description = articoli[i].DESCRIZIONE, 
            img_path = articoli[i].IMG_PATH, 
            price = float(articoli[i].PREZZO), 
        )

    cnx.close()

    return articoli


def get_products_selled_by_user(userID):
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row 

    articoli = cnx.execute("SELECT A.*, C.NOME AS C_NOME FROM ARTICOLI AS A, CATEGORIE AS C WHERE A.CATEGORIA = C.ID AND A.ID_VENDITORE = ? AND A.STATO <> 0", (userID, )).fetchall()

    for i in range(len(articoli)):
        articoli[i] = Product(
            productID = int(articoli[i].ID), 
            name = articoli[i].NOME, 
            category = Category(categoryID = int(articoli[i].CATEGORIA), name = articoli[i].C_NOME),
            description = articoli[i].DESCRIZIONE, 
            img_path = articoli[i].IMG_PATH, 
            price = float(articoli[i].PREZZO), 
            availability = int(articoli[i].DISPONIBILITA),
            insertion_date = articoli[i].DATA_INSERIMENTO,
            last_update_date = articoli[i].DATA_ULTIMA_MODIFICA,
            selled = int(articoli[i].VENDUTI),
        )

    cnx.close()

    return articoli

def get_cumulative_orders_by_user(userID):
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row 

    ordini_cumulativi = cnx.execute("SELECT * FROM ORDINI_CUMULATIVI AS OC WHERE OC.ID_UTENTE = ?", (userID, )).fetchall()

    for i in range(len(ordini_cumulativi)):
        ordini_cumulativi[i] = CumulativeOrder(
            cumulativeID = ordini_cumulativi[i].ID,
            ordersList = [
                Order(
                    orderID = int(o.ID),
                    cumulativeOrderID = int(o.ID_CUMULATIVO), 
                    product = Product(
                        productID = int(o.ID_ARTICOLO), 
                        name = o.NOME,
                        description = o.DESCRIZIONE,
                        category = Category(
                            categoryID = int(o.CATEGORIA),
                            name = o.C_NOME,
                        ),
                        img_path = o.IMG_PATH,
                        price = float(o.PREZZO),
                        sellerID = int(o.ID_VENDITORE),
                        availability = int(o.DISPONIBILITA),
                        insertion_date = o.DATA_INSERIMENTO,
                        last_update_date = o.DATA_ULTIMA_MODIFICA,
                        selled = int(o.VENDUTI),
                        status = int(o.STATO_ARTICOLO)
                    ),
                    purchasePrice = float(o.PREZZO_ACQUISTO),
                    quantity = int(o.QUANTITA)
                )
                for o in cnx.execute(
                    "SELECT O.*, A.ID AS A_ID, A.STATO AS STATO_ARTICOLO, A.NOME, A.CATEGORIA, C.NOME AS C_NOME, A.DESCRIZIONE, A.ID_VENDITORE, A.IMG_PATH, A.PREZZO, A.DISPONIBILITA, A.DATA_INSERIMENTO, A.DATA_ULTIMA_MODIFICA, A.VENDUTI FROM ORDINI AS O, ARTICOLI AS A, CATEGORIE AS C WHERE O.ID_CUMULATIVO = ? AND O.ID_ARTICOLO = A.ID AND A.CATEGORIA = C.ID", (ordini_cumulativi[i].ID)
                ).fetchall()
            ],
            purchaseDate = ordini_cumulativi[i].DATA_ACQUISTO,
            totalPrice = float(ordini_cumulativi[i].PREZZO_TOTALE),
            userID = int(ordini_cumulativi[i].ID_UTENTE),
            shippingName = ordini_cumulativi[i].NOME_SPEDIZIONE,
            shippingSurname = ordini_cumulativi[i].COGNOME_SPEDIZIONE,
            shippingNation = ordini_cumulativi[i].NAZIONE_SPEDIZIONE,
            shippingProvince = ordini_cumulativi[i].PROVINCIA_SPEDIZIONE,
            shippingCity = ordini_cumulativi[i].CITTA_SPEDIZIONE,
            shippingStreet = ordini_cumulativi[i].VIA_SPEDIZIONE,
            shippingHouseNumber = ordini_cumulativi[i].CIVICO_SPEDIZIONE,
            shippingPostalCode = ordini_cumulativi[i].CAP_SPEDIZIONE,
            shippingPhone = ordini_cumulativi[i].CELLULARE_SPEDIZIONE,
            shippingEmail = ordini_cumulativi[i].EMAIL_SPEDIZIONE
        )

    cnx.close()

    return ordini_cumulativi

def execute_cumulative_order(cumOrd):
    ### PLEASE NOTE
    # product availabilities are handled by a trigger in the DB!
    ### -----

    log("EXECUTING CUMORD NOW")

    cnx = ngn.connect()
    trans = cnx.begin()

    try:
        cnx.execute(
            "INSERT INTO ORDINI_CUMULATIVI\
            (\
                DATA_ACQUISTO,\
                PREZZO_TOTALE,\
                ID_UTENTE,\
                NOME_SPEDIZIONE,\
                COGNOME_SPEDIZIONE,\
                NAZIONE_SPEDIZIONE,\
                PROVINCIA_SPEDIZIONE,\
                CITTA_SPEDIZIONE,\
                VIA_SPEDIZIONE,\
                CIVICO_SPEDIZIONE,\
                CAP_SPEDIZIONE,\
                CELLULARE_SPEDIZIONE,\
                EMAIL_SPEDIZIONE\
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", (
                cumOrd.purchaseDate,
                cumOrd.totalPrice,
                cumOrd.userID,
                cumOrd.shippingName,
                cumOrd.shippingSurname,
                cumOrd.shippingNation,
                cumOrd.shippingProvince,
                cumOrd.shippingCity,
                cumOrd.shippingStreet,
                cumOrd.shippingHouseNumber,
                cumOrd.shippingPostalCode,
                cumOrd.shippingPhone,
                cumOrd.shippingEmail
            )
        )
        
        cumOrdID = cnx.execute("SELECT last_insert_rowid();").fetchone()[0]

        print("now executing insertion of all single orders")

        for ord in cumOrd.ordersList:
            cnx.execute(
                "INSERT INTO ORDINI\
                (\
                    ID_CUMULATIVO,\
                    ID_ARTICOLO,\
                    PREZZO_ACQUISTO,\
                    QUANTITA\
                ) VALUES (?,?,?,?)", 
                (
                    cumOrdID, 
                    ord.product.id,
                    ord.purchasePrice,
                    ord.quantity
                )
            )
            print("ok")
        
        log("CUMORD EXECUTED SUCCESFULLY")

        trans.commit()
        cnx.close()

        return True
    except Exception as e:
        log(e)
        trans.rollback()
        cnx.close()

        return False

def get_cumulative_orders_to_user(userID):
    cnx = ngn.connect()
    cnx.row_factory = sqlite3.Row 

    ordini_ricevuti = cnx.execute(
    "SELECT\
	    OC.ID AS ID_CUMULATIVO,\
	    O.ID AS ID_ORDINE,\
	    A.ID AS ID_ARTICOLO,\
	    A.IMG_PATH,\
	    OC.ID_UTENTE AS ID_CLIENTE,\
	    A.NOME AS NOME_ARTICOLO,\
	    OC.NOME_SPEDIZIONE,\
	    OC.COGNOME_SPEDIZIONE,\
	    OC.NAZIONE_SPEDIZIONE,\
	    OC.PROVINCIA_SPEDIZIONE,\
	    OC.CITTA_SPEDIZIONE,\
	    OC.VIA_SPEDIZIONE,\
	    OC.CIVICO_SPEDIZIONE,\
	    OC.CAP_SPEDIZIONE,\
	    OC.EMAIL_SPEDIZIONE,\
	    OC.CELLULARE_SPEDIZIONE,\
	    O.PREZZO_ACQUISTO,\
	    O.QUANTITA,\
	    OC.DATA_ACQUISTO\
    FROM\
	    ARTICOLI AS A,\
	    ORDINI AS O,\
	    ORDINI_CUMULATIVI AS OC\
    WHERE\
	    A.ID = O.ID_ARTICOLO AND\
	    O.ID_CUMULATIVO = OC.ID AND\
	    A.ID_VENDITORE = ?;",
        (userID, )
    ).fetchall()

    ordini_per_cumID = {}

    for i in range(len(ordini_ricevuti)):
        if int(ordini_ricevuti[i].ID_CUMULATIVO) not in ordini_per_cumID:
            ordini_per_cumID[int(ordini_ricevuti[i].ID_CUMULATIVO)] = [ordini_ricevuti[i]]
        else:
            ordini_per_cumID[int(ordini_ricevuti[i].ID_CUMULATIVO)].append(ordini_ricevuti[i])


    ordini_ricevuti = []
    for cumID in ordini_per_cumID:

        ordersList=[
            Order(
                orderID=ord.ID_ORDINE, 
                product=Product(
                    productID=ord.ID_ARTICOLO, 
                    name=ord.NOME_ARTICOLO,
                    img_path=ord.IMG_PATH
                ),
                purchasePrice=ord.PREZZO_ACQUISTO,
                quantity=ord.QUANTITA
            ) for ord in ordini_per_cumID[cumID]
        ]

        ordini_ricevuti.append(
            CumulativeOrder(
                cumulativeID=cumID,
                ordersList=ordersList,
                totalPrice=sum([x.purchasePrice*x.quantity for x in ordersList]),
                purchaseDate=ordini_per_cumID[cumID][0].DATA_ACQUISTO,
                userID = int(ordini_per_cumID[cumID][0].ID_CLIENTE),
                shippingName = ordini_per_cumID[cumID][0].NOME_SPEDIZIONE,
                shippingSurname = ordini_per_cumID[cumID][0].COGNOME_SPEDIZIONE,
                shippingNation = ordini_per_cumID[cumID][0].NAZIONE_SPEDIZIONE,
                shippingProvince = ordini_per_cumID[cumID][0].PROVINCIA_SPEDIZIONE,
                shippingCity = ordini_per_cumID[cumID][0].CITTA_SPEDIZIONE,
                shippingStreet = ordini_per_cumID[cumID][0].VIA_SPEDIZIONE,
                shippingHouseNumber = ordini_per_cumID[cumID][0].CIVICO_SPEDIZIONE,
                shippingPostalCode = ordini_per_cumID[cumID][0].CAP_SPEDIZIONE,
                shippingPhone = ordini_per_cumID[cumID][0].CELLULARE_SPEDIZIONE,
                shippingEmail = ordini_per_cumID[cumID][0].EMAIL_SPEDIZIONE
            )
        )

    cnx.close()

    return ordini_ricevuti

def unlist_product(prodID, userID):
    cnx = ngn.connect()

    isYours = cnx.execute("SELECT * FROM ARTICOLI WHERE ID = ? AND ID_VENDITORE = ?", (prodID, userID)).fetchall()
    if len(isYours) == 0:
        return False

    try:
        log("UNLISTING PRODUCT")

        trans = cnx.begin()
        cnx.execute("UPDATE ARTICOLI SET STATO = 0 WHERE ARTICOLI.ID = ?", (prodID, ))
        trans.commit()

        cnx.close()

        log("PRODUCT UNLISTED SUCCESFULLY")

        return True
    except Exception as e:
        log(e)

        trans.rollback()

        cnx.close()
        return False

def update_product(prodID, newProduct:Product, userID):
    cnx = ngn.connect()

    isYours = cnx.execute("SELECT * FROM ARTICOLI WHERE ID = ? AND ID_VENDITORE = ?", (prodID, userID)).fetchall()
    if len(isYours) == 0:
        return False    
    
    try:
        log("UPDATING PRODUCT")

        trans = cnx.begin()
        cnx.execute(
            "UPDATE ARTICOLI SET\
                NOME=?,\
                DESCRIZIONE=?,\
                CATEGORIA=?,\
                PREZZO=?,\
                DISPONIBILITA=?,\
                DATA_ULTIMA_MODIFICA=?,\
                IMG_PATH=?\
            WHERE ARTICOLI.ID = ?", 
            (
                newProduct.name,
                newProduct.description,
                newProduct.category,
                newProduct.price,
                newProduct.availability,
                newProduct.last_update_date,
                newProduct.img_path,
                prodID
            )
        )

        trans.commit()

        trans.close()
        cnx.close()

        log("PRODUCT UPDATED SUCCESFULLY")

        return True
    except Exception as e:
        log(e)

        trans.rollback()

        trans.close()
        cnx.close()

        return False

def add_product(newProduct:Product, userID):
    cnx = ngn.connect()

    if userID != newProduct.sellerID:
        return False

    try:
        log("INSERTING NEW PRODUCT")
        
        trans = cnx.begin()
        cnx.execute(
            "INSERT INTO ARTICOLI\
            (\
                NOME,\
                CATEGORIA,\
                DESCRIZIONE,\
                IMG_PATH,\
                ID_VENDITORE,\
                PREZZO,\
                DISPONIBILITA,\
                DATA_INSERIMENTO,\
                DATA_ULTIMA_MODIFICA,\
                VENDUTI,\
                STATO\
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", 
            (
                newProduct.name,
                newProduct.category,
                newProduct.description,
                newProduct.img_path, # this is broken.png
                newProduct.sellerID,
                newProduct.price,
                newProduct.availability,
                newProduct.insertion_date,
                newProduct.last_update_date,
                0, # no sells before
                1 # obv this product is sellable as it's newly inserted
            )
        )

        trans.commit()

        trans.close()

        prodID = int(cnx.execute("SELECT last_insert_rowid();").fetchone()[0])
       
        cnx.close()

        log("PRODUCT INSERTED SUCCESFULLY")

        return prodID

    except Exception as e:
        log(e)

        trans.rollback()

        trans.close()
        cnx.close()

        return False