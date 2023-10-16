from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required
from ..dao import get_all_categories, get_products_selled_by_user, get_product_by_id, get_cumulative_orders_to_user, unlist_product, update_product, add_product
from ..forms import RemoveForm, AlterProductForm, MAX_PRODUCT_DESCRIPTION_LENGTH, MAX_PRODUCT_NAME_LENGTH
from ..models import Product
from ..utils import Messages, upload_image, log

m = Messages()

selling = Blueprint('selling', __name__)

@selling.route('/my-products')
@login_required
def my_products_page():
	removeForm = RemoveForm()
	return render_template(
		"my_products.html", 
		products = get_products_selled_by_user(session["user"]["id"]), 
		username = session["user"]["username"], 
		removeForm = removeForm
	)

@selling.route('/my-products', methods=["POST"])
@login_required
def remove_my_product_fun():
	removeForm = RemoveForm()
	if removeForm.validate_on_submit():
		prodID = int(request.form.get('prodID'))

		if unlist_product(prodID, session["user"]["id"]):
			flash(m.succProductUnlisting, 'success')
		else:
			flash(m.errGeneric, 'error')
		
	return render_template(
		"my_products.html", 
		products = get_products_selled_by_user(session["user"]["id"]), 
		username = session["user"]["username"], 
		removeForm = removeForm
	)

@selling.route('/add-product')
@login_required
def add_product_page():
	form = AlterProductForm()
	form.set_categories(get_all_categories())

	return render_template(
		"alter_product.html", 
		username = session["user"]["username"], 
		form = form
	)

@selling.route('/add-product', methods=["POST"])
@login_required
def add_product_fun():
	form = AlterProductForm()
	form.set_categories(get_all_categories())

	if not form.validate_on_submit():
		log(form.errors)
		flash(m.errInvalidFields, 'error')
		return render_template(
			"alter_product.html", 
			username = session["user"]["username"], 
			form = form
		)

	### getting user input
	name = request.form.get("name").strip()
	if len(name) > MAX_PRODUCT_NAME_LENGTH:
		name = name[:MAX_PRODUCT_NAME_LENGTH-1]
	description = request.form.get("description").strip()
	if len(description) > MAX_PRODUCT_DESCRIPTION_LENGTH:
		description = description[:MAX_PRODUCT_DESCRIPTION_LENGTH-1]
	category = int(request.form.get("category"))
	price = round(float(request.form.get("price")), 2)
	if price < 0.0:
		flash(m.errNegativePrice, 'error')
		return render_template(
			"alter_product.html", 
			username = session["user"]["username"], 
			form = form
		)
	availability = int(request.form.get("availability"))
	lastUpdateDate = request.form.get("lastUpdateDate")
	### -----

	### constructing a new product
	newProduct = Product(
		name=name,
		description=description,
		availability=availability,
		category=category,
		price=price,
		last_update_date=lastUpdateDate,
		insertion_date=lastUpdateDate,
		sellerID=session["user"]["id"]
	)
	### -----

	# from now on, actually adding the product

	prodID = add_product(newProduct, session["user"]["id"])
	if not prodID:
		flash(m.errGeneric, 'error')
		return render_template(
			"alter_product.html", 
			username = session["user"]["username"], 
			form = form
		)

	### uploading the new image (now that I have the product ID as the name of the img derives from it)
	if "img" not in request.files or request.files["img"].filename == "":
		# the product has been loaded in the DB, but problems happened with the img.
		# let's "re-render the page, but in update mode"
		flash(m.errImageUploading, 'error')
		return redirect(url_for('selling.modify-product/'+str(prodID)))

	# a new image has been sent, this resizes it if it's too large, 
	# and renames it before uploading it
	img_path = upload_image(prodID=prodID, img=request.files["img"])
	### -----
	
	### now I have to update the img_path in the product
	newProduct.img_path = img_path
	if not update_product(prodID=prodID, newProduct=newProduct, userID=session["user"]["id"]):
		flash(m.errGeneric, 'error')
		return render_template(
			"alter_product.html", 
			username = session["user"]["username"], 
			form = form
		)
	### -----

	# done! 

	flash(m.succNewProductSubmission)
	return redirect(url_for('selling.my_products_page'))


@selling.route('/modify-product/<int:prodID>')
@login_required
def modify_product_page(prodID):
	product = get_product_by_id(prodID)
	form = AlterProductForm()
	form.set_categories(get_all_categories())
	# initial values must be the selected product's ones this time
	form.set_default_values(product)

	return render_template("alter_product.html", product = product, username = session["user"]["username"], form = form)

@selling.route('/modify-product/<int:prodID>', methods=["POST"])
@login_required
def modify_product_fun(prodID):
	# if something fails and this page is called again, the product remains unchanged
	# (and changes are lost)
	product = get_product_by_id(prodID)
	form = AlterProductForm()
	form.set_categories(get_all_categories())
	### fix 
	# without this, if the product goes to 0, is never modifiable again
	# because of some bug in the validators of WTForms.
	if product.availability == 0:
		product.availability = 1
	### -----
	form.set_default_values(product)

	if not form.validate_on_submit():
		log(form.errors)
		flash(m.errInvalidFields, 'error')
		return render_template(
			"alter_product.html", 
			product = product,
			username = session["user"]["username"], 
			form = form
		)

	# from now on, actually updating the product

	### getting user input
	name = request.form.get("name").strip()
	if len(name) > MAX_PRODUCT_NAME_LENGTH:
		name = name[:MAX_PRODUCT_NAME_LENGTH-1]
	description = request.form.get("description").strip()
	if len(description) > MAX_PRODUCT_DESCRIPTION_LENGTH:
		description = description[:MAX_PRODUCT_DESCRIPTION_LENGTH-1]
	category = int(request.form.get("category"))
	price = round(float(request.form.get("price")), 2)
	if price < 0.0:
		flash(m.errNegativePrice, 'error')
		return render_template(
			"alter_product.html", 
			product = product,
			username = session["user"]["username"], 
			form = form
		)
	availability = int(request.form.get("availability"))
	lastUpdateDate = request.form.get("lastUpdateDate")
	### -----

	### uploading the new image (this time I got the product ID beforehand so let's do this first)
	if "img" not in request.files:
		flash("Si è verificato un errore. Riprova")
		return render_template(
			"alter_product.html", 
			product = product, 
			username = session["user"]["username"], 
			form = form
		)
	if request.files["img"].filename == "":
		# image has not been modified
		img_path = str(prodID)+".png"
	else: 
		# a new image has been sent, this resizes it if it's too large, 
		# and renames it before uploading it
		img_path = upload_image(prodID=prodID, img=request.files["img"])
	### -----

	### constructing a product as a container for the changes
	newProduct = Product(
		name=name,
		description=description,
		availability=availability,
		category=category,
		price=price,
		last_update_date=lastUpdateDate,
		img_path=img_path
	)
	### -----

	if not update_product(prodID, newProduct, session["user"]["id"]):
		flash(m.errGeneric, 'error')
		return render_template(
			"alter_product.html", 
			product = product,
			username = session["user"]["username"], 
			form = form
		)

	# done!

	flash(m.succUpdatingProduct, 'success')
	return redirect(url_for('selling.my_products_page'))


@selling.route('/received-orders')
@login_required
def received_orders_page():
	return render_template(
		"received_orders.html", 
		username = session["user"]["username"], 
		cumulativeOrders = get_cumulative_orders_to_user(session["user"]["id"])
	)