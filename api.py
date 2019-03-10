from flask import Flask, session, request, render_template, Response, Blueprint, abort
from models import Document, Tag, db
from serializer import DocumentSchema, TagSchema
import json

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

        db.session.add(document)
        db.session.commit()

    schema = DocumentSchema()
    return schema.jsonify(document)


@api.route('/new/bulk', methods=['POST'])
def bulk_add_tag():
    """
    Adds a tag to multiple documents.  The payload is set up like this:
    { 'tag': string,
      'doc_ids': []
    }
    :return: nada
    """

    doc_ids = json.loads(request.form['doc_ids'])
    tag_text = request.form['tag']

    for docid in doc_ids:

        document = Document.query.filter_by(id=docid).first_or_404()

        if tag_text not in document.tags:

            newtag = Tag(document_id=docid, tag=tag_text, is_deleted=False)
            document.tags.append(newtag)

            db.session.add(document)

    db.session.commit()

    return 'OK'


@api.route('new/finish', methods=['POST'])
def finish_documents():
    """
    Sets the status of the documents from NEW to OK, thereby releasing them to the main workflow.
    { 'tag': string,
      'doc_ids': []
    }
    :return:
    """

    doc_ids = json.loads(request.form['doc_ids'])

    for docid in doc_ids:

        document = Document.query.filter_by(id=docid).first_or_404()

        document.status = "OK"

        db.session.add(document)

    db.session.commit()


@api.route('/test', methods=['GET'])
def test():
    return "Test!"
