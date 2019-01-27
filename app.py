from flask import (Flask, session, request, render_template, Response, Blueprint, flash, g, redirect, url_for)
from models import db, Document, Tag
from flask_migrate import Migrate
from datetime import timedelta
from serializer import ma
import config

# init app
app = Flask(__name__)

# get config shiz
app.config.from_object('config')

# SQLalchemy init
db.init_app(app)

# marshmallow / serializer init
ma.init_app(app)

# flask migrate support
migrate = Migrate(app, db)

# import and init blueprints
from documents import documents

app.register_blueprint(documents)


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
def new():

    # this is the new queue, where newly uploaded files can be viewed.

    # query all documents with the status NEW
    new_docs = Document.query.filter_by(status="NEW").all()
    thumb_dir = config.thumnail_directory

    # data = {'data':new_docs, 'thumb_dir':thumb_dir}

    return render_template('new.html', thumb_dir=thumb_dir, data=new_docs)



