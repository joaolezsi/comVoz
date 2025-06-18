from marshmallow import Schema, fields


class CriarOpcoesQuestaoSchema(Schema):
    texto = fields.String(required=True)
    

class CriarQuestaoSchema(Schema):
    texto = fields.String(required=True)
    tipo = fields.Integer(required=True)
    opcoes = fields.List(fields.Nested(CriarOpcoesQuestaoSchema), required=False, allow_none=True)



class ListaCriarQuestoesSchema(Schema):
    questoes = fields.List(fields.Nested(CriarQuestaoSchema), required=True)
    user_id = fields.Integer(required=True)

class RetornoOpcoesQuestaoSchema(Schema):
    id = fields.Integer(required=True)
    texto = fields.String(required=True)
    questao_id = fields.Integer(required=True)


class RetornoQuestaoSchema(Schema):
    id = fields.Integer(required=True)
    texto = fields.String(required=True)
    tipo = fields.Integer(required=True)
    opcoes = fields.List(fields.Nested(RetornoOpcoesQuestaoSchema), required=False, allow_none=True)
    user_id = fields.Integer(allow_none=True)




