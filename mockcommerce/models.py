from flask_login import UserMixin
import locale

class User(UserMixin):
    def __init__(self, userID:int, username:str):
        self.id = userID
        self.username = username

class Product:
    def __init__(
        self, 
        productID:int = -1, 
        name:str = "", 
        description:str = "", 
        category:int = -1, 
        img_path:str = "broken.png", 
        sellerID:int = -1, 
        price:float = -1.0, 
        availability:int = -1, 
        insertion_date:str = "", 
        last_update_date:str = "", 
        selled:int = -1,
        status:int = -1,
    ):
        self.id = productID
        self.name = name
        self.description = description
        self.category = category
        self.img_path = img_path
        self.price = price
        self.formattedPrice = locale.currency(price)
        self.sellerID = sellerID
        self.availability = availability
        self.insertion_date = insertion_date
        self.last_update_date = last_update_date
        self.selled = selled
        self.status = status

class Category:
    def __init__(self, categoryID:int=-1, name:str="", description:str=""):
        self.id = categoryID
        self.name = name
        self.description = description

class Order:
    def __init__(
        self, 
        orderID:int = -1, 
        cumulativeOrderID:int = -1, 
        product:Product = Product(), 
        purchasePrice:float = -1.0, 
        quantity:int = -1
    ):
        self.id = orderID
        self.cumulativeID = cumulativeOrderID
        self.product = product
        self.purchasePrice = purchasePrice
        self.formattedPurchasePrice = locale.currency(purchasePrice)
        self.quantity = quantity
        self.totalPrice = self.purchasePrice * self.quantity

class CumulativeOrder():
    def __init__(
        self, 
        ordersList:list = [],
        cumulativeID:int = -1, 
        purchaseDate:str = "", 
        totalPrice:float = -1.0, 
        userID:int = -1, 
        shippingName:str = "", 
        shippingSurname:str = "", 
        shippingNation:str = "", 
        shippingProvince:str = "", 
        shippingCity:str = "", 
        shippingStreet:str = "", 
        shippingHouseNumber:str = "", 
        shippingPostalCode:str = "", 
        shippingPhone:str = "", 
        shippingEmail:str = ""
    ):
        self.cumulativeID = cumulativeID
        self.ordersList = ordersList
        self.purchaseDate = purchaseDate
        self.totalPrice = totalPrice
        self.formattedTotalPrice = locale.currency(totalPrice)
        self.userID = userID
        self.shippingName = shippingName
        self.shippingSurname = shippingSurname
        self.shippingNation = shippingNation
        self.shippingProvince = shippingProvince
        self.shippingCity = shippingCity
        self.shippingStreet = shippingStreet
        self.shippingHouseNumber = shippingHouseNumber
        self.shippingPostalCode = shippingPostalCode
        self.shippingAddress = ", ".join([shippingNation, shippingCity, shippingStreet, shippingHouseNumber, shippingPostalCode])
        self.shippingPhone = shippingPhone
        self.shippingEmail = shippingEmail