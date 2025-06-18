from marshmallow import Schema, fields, validate, ValidationError
from src.enums.questionTipe_enum import QuestionTypeEnum

class RespostaSchemaDict(Schema): 
    pergunta_id = fields.Int(required=True)
    resposta = fields.Raw(required=True)  
    tipo_pergunta = fields.Str(required=True)

    

class RespostasSchema(Schema):
    respostas = fields.List(fields.Nested(RespostaSchemaDict), required=True)
    nome = fields.String(required=True)
    email = fields.String(required=True)
    pesquisa_id = fields.Str(required=True)

