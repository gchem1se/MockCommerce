### all which is meant to be done with or by the $app object
### must remain here

import locale

locale.setlocale(locale.LC_ALL, 'it_IT.utf8')

### init app with instance folder
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
### -----

### init CSRF protection
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
csrf.init_app(app)
### -----

### create engine for db operations
from sqlalchemy import create_engine

# don't move this, it uses app's configs
ngn = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
### -----

### attach login manager
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
### -----

### attach session manager
from flask_session import Session
Session(app)
### -----

### register all the routes in the views module
from .views.buying import buying
from .views.selling import selling
from .views.auth import auth

app.register_blueprint(buying)
app.register_blueprint(selling)
app.register_blueprint(auth)
### -----
