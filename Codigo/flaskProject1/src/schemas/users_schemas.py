from marshmallow import Schema, fields, validate


class RegisterUserSchema(Schema):
    nome_completo = fields.String(required=True)
    email = fields.String(required=True)
    telefone = fields.String(required=True)
    empresa = fields.String(required=True)
    cargo = fields.String(required=True)
    cnpj = fields.String(required=True)
    password = fields.String(required=True)
    passwordRepeat = fields.String(required=True)
    
    
class LoginUserSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    

class LoggedUserSchema(Schema):
    id = fields.Integer(required=True)
    nome_completo = fields.String(required=True)
    email = fields.String(required=True)
    telefone = fields.String(required=True)
    empresa = fields.String(required=True)
    cargo = fields.String(required=True)
    cnpj = fields.String(required=True)
    token = fields.String(required=False)



