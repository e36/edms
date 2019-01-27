from flask_marshmallow import Marshmallow
from models import Document, Tag

ma = Marshmallow()


class DocumentSchema(ma.ModelSchema):
    class Meta:
        model = Document


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tag

