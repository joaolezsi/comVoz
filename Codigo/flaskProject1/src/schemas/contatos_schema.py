from marshmallow import Schema, fields, validate


class CreateContatoSchema(Schema):
    nome = fields.String(allow_none=True)
    email = fields.String(required=True)
    telefone = fields.String(allow_none=True)


class ContatosListSchema(Schema):
    contatos = fields.List(fields.Nested(CreateContatoSchema), required=True)


class ContatoExcelSchema(Schema):
    nome = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=True)
    telefone = fields.Str(required=False, allow_none=True)



