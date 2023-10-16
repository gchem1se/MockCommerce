from flask import render_template, url_for, redirect, request, Blueprint, flash, session
from ..forms import LoginForm, SigninForm
from ..dao import get_user_by_id, check_user_for_login, add_user
from flask_login import login_user, login_required, logout_user
from ..models import User
from ..utils import Messages, valid_password, valid_username
from .. import login_manager

m = Messages()

### configure login manager
login_manager.login_view = 'auth.login_page'
login_manager.login_message = m.loginMessage

@login_manager.user_loader
def load_user(userID):
	currUser = get_user_by_id(userID)

	if currUser:
		currUser = User(userID=currUser.ID, username=currUser.USERNAME)
	else:
		currUser = None
	return currUser
### -----

auth = Blueprint('auth', __name__)

@auth.route('/signin')
def signin_page():
	form = SigninForm()
	return render_template("signin.html", form=form)

@auth.route('/signin', methods=["POST"])
def signin_fun():
	form = SigninForm()
	if not form.validate_on_submit():
		flash(m.errInvalidFields, 'error')
		return render_template("signin.html", form=form)

	### getting user input
	username = request.form.get('username').strip()
	if not valid_username(username):
		flash(m.errSigninUsername, 'error')
		return render_template("signin.html", form=form)

	password = request.form.get('password')
	if not valid_password(password):
		flash(m.errSigninPassword, 'error')
		return render_template("signin.html", form=form)
	### -----

	return_code = add_user(username, password)

	if return_code == -1:
		flash(m.errSignin, 'error')
		return render_template("signin.html", form=form)
	elif return_code:
		flash(m.succSignin, 'success')
		return redirect(url_for('auth.login_page'))
	else:
		flash(m.errGeneric, 'error')
		return render_template("signin.html", form=form)
		

@auth.route('/login')
def login_page():
	form = LoginForm()
	return render_template("login.html", form=form)

@auth.route('/login', methods=["POST"])
def login_fun():
	form = LoginForm()


	if not form.validate_on_submit():
		flash(m.errInvalidFields, 'error')
		return render_template("login.html", form=form)
	
	### getting user input
	username = request.form.get('username').strip()
	password = request.form.get('password')
	# to redirect after login
	next_url = request.form.get("next-url") 
	### -----

	userID = check_user_for_login(username, password)
	if not userID:
		# login failed
		flash(m.errLogin, 'error')
		return render_template("login.html", form=form)

	### login succeded
	currUser = User(userID = userID, username=username)
	# save user info in session
	session["user"] = dict()
	session["user"]["username"] = currUser.username
	session["user"]["id"] = currUser.id
	# init cart
	session["cart"] = dict()

	login_user(currUser, True)
	### -----

	# redirect after login if needed
	if next_url:
		return redirect(next_url)
	return redirect(url_for('buying.home_page'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()

	### destroy session information
	session.pop("user")
	session.pop("cart")
	### -----
	
	return redirect(url_for('buying.home_page'))