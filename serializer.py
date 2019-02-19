from flask_marshmallow import Marshmallow
from models import Document, Tag

ma = Marshmallow()


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tag


class DocumentSchema(ma.ModelSchema):
    class Meta:
        model = Document

    tags = ma.Nested(TagSchema, many=True)
