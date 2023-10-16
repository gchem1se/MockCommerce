from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required
from ..dao import get_all_products, get_all_categories, execute_cumulative_order, get_cumulative_orders_by_user, get_product_by_id
from ..forms import CheckoutForm, AddToCartForm, RemoveForm
from ..models import CumulativeOrder, Product, Order
import locale
import datetime
import json
from ..utils import Messages, log, valid_phone, valid_email, valid_postal_code, valid_card_expiry_date, valid_card_number, valid_CVV

m = Messages()

buying = Blueprint('buying', __name__)

@buying.route('/')
def home_page():
	username = None
	if "user" in session:
		username = session["user"]["username"]

	return render_template(
		"home.html", 
		categorie = get_all_categories(), 
		products = get_all_products(), 
		username = username
	)

@buying.route('/products/<int:id>')
def product_details_page(id):
	username = None
	sellerID = None
	
	if "user" in session:
		sellerID = session["user"]["id"]
		username = session["user"]["username"]

	form = AddToCartForm()

	product = get_product_by_id(id)

	if product.status == 0:
		flash(m.errProductIsUnlisted, 'error')
		return redirect(url_for('buying.home_page'))

	if product.sellerID == sellerID:
		flash(m.infoProductIsYours, 'success')

	return render_template(
		"product_details.html", 
		product = product,
		username=username, 
		form=form
	)

@buying.route('/products/<int:id>', methods=["POST"])
@login_required
def add_to_cart_fun(id):
	form = AddToCartForm()
	if not form.validate_on_submit():
		log(form.errors)
		flash(m.errGeneric, 'error')
	else:
		quantity = int(request.form.get('quantity'))
		
		# session["cart"] will be like:
		# { 1:2, 2:5, 8:10, 7:1 } | { prodID: quantity }

		if id in session["cart"]:
			session["cart"][id] += quantity
		else:
			session["cart"][id] = quantity

		flash(m.succAddToCart, 'success')

	return render_template(
		"product_details.html", 
		product = get_product_by_id(id), 
		username=session["user"]["username"], 
		form=form
	)

@buying.route('/my-orders')
@login_required
def my_orders_page():
	return render_template(
		"my_orders.html", 
		cumulativeOrders = get_cumulative_orders_by_user(session["user"]["id"]), 
		username=session["user"]["username"], 
		userID=session["user"]["id"]
	)

@buying.route('/checkout')
@login_required
def checkout_page():
	removeForm = RemoveForm()
	form = CheckoutForm()
	products = dict()
	
	quantities = dict()
	# ^^ quantities the user set in the details page forms
	totalPrice = 0.0
	# ^^ initial price, before changing quantity inputs

	### let's do a cleanup of no more listed products
	keysList = list(session["cart"].keys())
	# ^^ using this because if a pop() happens inside the for, 
	# we get "dictionary changed value during iteration" error
	for prodID in keysList:
		products[prodID] = get_product_by_id(prodID)
		if products[prodID].status == 1:
			quantities[prodID] = session["cart"][prodID]
			totalPrice += products[prodID].price * session["cart"][prodID]
		else:
			session["cart"].pop(prodID)
			products.pop(prodID)
			# advice user
			flash(m.errNotAvailableAnymore, 'error')
			return redirect(url_for('buying.checkout_page'))
	### -----

	formattedTotalPrice = locale.currency(totalPrice)
	
	return render_template(
		"checkout.html", 
		products=products, 
		quantities=session["cart"], 
		totalPrice = totalPrice, 
		formattedTotalPrice = formattedTotalPrice, 
		username=session["user"]["username"], 
		form=form, 
		userID=session["user"]["id"], 
		removeForm=removeForm
	)

@buying.route('/checkout', methods=["POST"])
@login_required
def checkout_fun():
	removeForm = RemoveForm()
	form = CheckoutForm()
	products = dict()
	
	quantities = session["cart"]
	totalPrice = 0.0

	### cleanup
	keysList = list(session["cart"].keys())
	for prodID in keysList:
		products[prodID] = get_product_by_id(prodID)
		if products[prodID].status == 1:
			quantities[prodID] = session["cart"][prodID]
			totalPrice += products[prodID].price * session["cart"][prodID]
		else:
			session["cart"].pop(prodID)
			products.pop(prodID)
			flash(m.errNotAvailableAnymore, 'error')
	
			return redirect(url_for('buying.checkout_page'))
	### -----

	formattedTotalPrice = locale.currency(totalPrice)

	### handling removing products from the cart
	if removeForm.validate_on_submit():
		prodID = int(request.form.get("prodID"))
		session["cart"].pop(prodID)
		products.pop(prodID)
		flash(m.succRemFromCart, 'success')
	
		return redirect(url_for('buying.checkout_page'))

	### -----

	# from now on, this validates and executes the order

	if not form.validate_on_submit():
		log(form.errors)
		flash(m.errInvalidFields, 'error')
		return render_template(
			"checkout.html", 
			products=products, 
			quantities=quantities, 
			totalPrice = totalPrice, 
			formattedTotalPrice = formattedTotalPrice, 
			username=session["user"]["username"], 
			form=form, 
			userID=session["user"]["id"], 
			removeForm=removeForm
		)

	if len(session["cart"]) == 0:
		# the page is an old cache. Let's end this here
		return render_template(
			"checkout.html", 
			products=products, 
			quantities=quantities, 
			totalPrice = totalPrice, 
			formattedTotalPrice = formattedTotalPrice, 
			username=session["user"]["username"], 
			form=form, 
			userID=session["user"]["id"], 
			removeForm=removeForm
		) 

	purchaseDate = request.form.get("purchaseDate")
	# ^^ make sure this is added by JS in the browser
	userID = int(request.form.get("userID"))
	orders = json.loads(request.form.get("orders"))
	
	### update info in session
	session["cart"] = dict()
	for prodID in orders:
		session["cart"][int(prodID)] = orders[prodID]["quantity"]
	### -----

	### getting user input
	shippingName = request.form.get("shippingName").strip()
	shippingSurname = request.form.get("shippingSurname").strip()
	shippingNation = request.form.get("shippingNation").strip()
	shippingProvince = request.form.get("shippingProvince").strip()
	shippingCity = request.form.get("shippingCity").strip()
	shippingStreet = request.form.get("shippingStreet").strip()
	shippingHouseNumber = request.form.get("shippingHouseNumber").strip()
	shippingPostalCode = request.form.get("shippingPostalCode").strip()
	shippingPhone = request.form.get("shippingPhone").strip()
	shippingEmail = request.form.get("shippingEmail").strip()
	# reformatting date to italian format
	expiryDate = datetime.datetime.strptime(request.form.get("expiryDate").strip(), "%Y-%m-%d").strftime("%d/%m/%Y")
	cardNumber = request.form.get("cardNumber").strip()
	securityCode = request.form.get("securityCode").strip()
	
	err = False
	if not valid_phone(shippingPhone):
		flash(m.errPhone, 'error')
		err = True
	elif not valid_email(shippingEmail):
		flash(m.errEmail, 'error')
		err = True
	elif not valid_postal_code(shippingPostalCode):
		flash(m.errPostalCode, 'error')
		err = True
	elif not valid_card_expiry_date(expiryDate):
		flash(m.errCardExpired, 'error')
		err = True
	elif not valid_card_number(cardNumber):
		flash(m.errCardNumber, 'error')
		err = True
	elif not valid_CVV(securityCode):
		flash(m.errCardCVV, 'error')
		err = True

	if err:
		return render_template(
			"checkout.html", 
			products=products, 
			quantities=quantities, 
			totalPrice = totalPrice, 
			formattedTotalPrice = formattedTotalPrice, 
			username=session["user"]["username"], 
			form=form, 
			userID=session["user"]["id"], 
			removeForm=removeForm
		)
	
	# recomputing totalPrice
	totalPrice = sum([orders[prodID]["purchasePrice"]*orders[prodID]["quantity"] for prodID in orders])

	### -----

	### constructing the order
	cumOrd = CumulativeOrder(
		cumulativeID = -1,
		ordersList = [
			Order(
				# even if I parse the values in JS to obtain ints and floats,
				# python's json.loads changes all fields to strings again.
				product = Product(productID = int(prodID)),
				purchasePrice = float(orders[prodID]["purchasePrice"]),
				quantity = int(orders[prodID]["quantity"]),
			) for prodID in orders
		],
		purchaseDate = purchaseDate,
		totalPrice = totalPrice,
		userID = userID,
		shippingName = shippingName,
		shippingSurname = shippingSurname,
		shippingNation = shippingNation,
		shippingProvince = shippingProvince,
		shippingCity = shippingCity,
		shippingStreet = shippingStreet,
		shippingHouseNumber = shippingHouseNumber,
		shippingPostalCode = shippingPostalCode,
		shippingPhone = shippingPhone,
		shippingEmail = shippingEmail
	)
	### -----
	
	### let's validate prices and availabilities of the order before submitting it
	err = False
	for ord in cumOrd.ordersList:
		# let's re-request the product to also check for changes made in the meanwhile
		product = get_product_by_id(ord.product.id)
		if product.availability < ord.quantity: 
			# this is also checked from a trigger in the DB
			flash(m.errInvalidQuantities, 'error')
			err = True
			break
		elif product.price != ord.purchasePrice:
			flash(m.errPricesChanged, 'error')
			err = True
			break
		elif product.status != 1:
			# let's reload the page, so the cleanup will be done again
			err = True
			break

	if err:
		return render_template(
			"checkout.html", 
			products=products, 
			quantities=quantities, 
			totalPrice = totalPrice, 
			formattedTotalPrice = formattedTotalPrice, 
			username=session["user"]["username"], 
			form=form, 
			userID=session["user"]["id"], 
			removeForm=removeForm
		)
	### -----

	# executing order 

	if execute_cumulative_order(cumOrd=cumOrd):
		flash(m.succOrderSubmission, 'success')
		# empty the cart
		session["cart"] = dict()
		return redirect(url_for('buying.my_orders_page'))
	else:
		# generic error
		flash(m.errOrderSubmission, 'error')

	return render_template(
		"checkout.html", 
		products=products, 
		quantities=quantities, 
		totalPrice = totalPrice, 
		formattedTotalPrice = formattedTotalPrice, 
		username=session["user"]["username"], 
		form=form, 
		userID=session["user"]["id"], 
		removeForm=removeForm
	)
	
