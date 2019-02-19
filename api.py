from flask import Flask, session, request, render_template, Response, Blueprint, abort
from models import Document, Tag, db
from serializer import DocumentSchema, TagSchema

api = Blueprint('api', __name__, template_folder='templates', static_folder='static/documents')


@api.route('/document/<int:docid>', methods=['GET'])
def get_document(docid):
    # retrieved one specific document

    # query the document info
    document = Document.query.get(docid)

    # filename = config.document_directory + document_data.document_filename
    # document_data.document_filename = filename

    schema = DocumentSchema()
    return schema.jsonify(document)


@api.route('/update/document', methods=['POST'])
def update_document():
    # updates a document)

    doc_id = request.form['document_id']
    document = Document.query.filter_by(id=doc_id).first()

    if not document:
        return abort(400)

    # check to see if the various bits of data exist
    if request.form['title']:
        document.title = request.form['title']

    if request.form['description']:
        document.description = request.form['description']

    if document.status == 'NEW':
        document.status = "OK"

    db.session.add(document)
    db.session.commit()

    schema = DocumentSchema()
    return schema.jsonify(document)


@api.route('/new/tag', methods=['POST'])
def new_tag():
    # adds a new tag to a document

    document_id = request.form['document_id']
    tag = request.form['tag']

    document = Document.query.filter_by(id=document_id).first_or_404()

    if tag not in document.tags:

        newtag = Tag(document_id=document_id, tag=tag, is_deleted=False)
        document.tags.append(newtag)

        if document.status == 'NEW':
            document.status = "OK"

        db.session.add(document)
        db.session.commit()

    schema = DocumentSchema()
    return schema.jsonify(document)


@api.route('/test', methods=['GET'])
def test():
    return "Test!"
