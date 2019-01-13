from flask import Flask, session, request, render_template, Response
from models import db, Document, Tag
from flask_migrate import Migrate
from datetime import timedelta
import config

app = Flask(__name__)

app.config.from_object('config')

# postgresql://scott:tiger@localhost/mydatabase
app.config['SQLALCHEMY_DATABASE_URI'] = config.database['engine'] + "://" + config.database['user'] + ":" + config.database['password'] + "@" + config.database['hostname'] + "/" + config.database['database']

db.init_app(app)

# flask migrate support
migrate = Migrate(app, db)


# init DBs
@app.before_first_request
def startup():
    db.create_all()


@app.before_request
def make_session_permanent():
    # https://stackoverflow.com/a/11785722/
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=14)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def dashboard():
    return render_template('new.html')
