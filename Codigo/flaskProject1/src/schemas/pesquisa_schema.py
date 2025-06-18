from marshmallow import Schema, fields, validate

class QuestoesToUpdateSchema(Schema):
    perguntas = fields.List(fields.Integer(), required=True)


class PesquisaSchema(Schema):
    titulo = fields.String(required=True)
    descricao = fields.String(required=False)
    perguntas = fields.List(fields.Integer(), required=True)
    user_id = fields.Integer(required=True)


class PesquisaResponseSchema(PesquisaSchema):
    _id = fields.String(required=True)
    data_criacao = fields.DateTime(required=True)
