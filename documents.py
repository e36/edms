from flask import Flask, session, request, render_template, Response, Blueprint, flash, g, redirect, url_for
from models import Document, Tag, db
from datetime import timedelta
import config


documents = Blueprint('documents', __name__, template_folder='templates', static_folder='static/documents')


@documents.route('/documents/<int:docid>')
def document_index(docid):

    # displays one specific document

    # query the document info
    document_data = Document.query.get(docid)

    # filename = config.document_directory + document_data.document_filename
    # document_data.document_filename = filename

    return render_template('document.html', data=document_data)
