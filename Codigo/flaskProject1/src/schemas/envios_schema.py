from marshmallow import Schema, fields
class UsuarioSchema(Schema):
    nome = fields.String(required=True)
    email = fields.String(required=True)

class RespostaSchema(Schema):
    pergunta_id = fields.Integer(required=True)
    pergunta = fields.String(required=True)
    resposta = fields.String(required=True)

class EnvioSchema(Schema):
    pesquisa_id = fields.String(required=True)
    usuario = fields.Nested(UsuarioSchema, required=True)
    empresa_id = fields.String(required=True)

class RespostasEnvioSchema(Schema):
    respostas = fields.List(fields.Nested(RespostaSchema), required=True)
    concluido = fields.Boolean(required=False, default=True)

class EnvioResponseSchema(EnvioSchema):
    _id = fields.String(required=True)
    respostas = fields.List(fields.Nested(RespostaSchema), required=False)
    data_envio = fields.DateTime(required=True)
    concluido = fields.Boolean(required=True)
    data_conclusao = fields.DateTime(required=False)