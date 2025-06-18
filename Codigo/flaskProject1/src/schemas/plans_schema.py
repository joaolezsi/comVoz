from marshmallow import Schema, fields


class PlanSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str(required=True)
    descricao = fields.Str(required=True)
    preco = fields.Float(required=True)
    limite_pesquisas = fields.Int(required=True)

class PlanResponseSchema(Schema):
    plans = fields.List(fields.Nested(PlanSchema))


class PlanUpdateSchema(Schema):
    nome = fields.Str(required=True)
    descricao = fields.Str(required=True)
    preco = fields.Float(required=True)
    limite_pesquisas = fields.Int(required=True)


class PlanPurchaseInterestSchema(Schema):
    user_id = fields.Int(required=True)
    plan_id = fields.Int(required=True)


class PlanRequestSchema(Schema):
    plan_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    interest_id = fields.Int(required=True)



class SubscriptionResponseSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    plan_id = fields.Int(required=True)
    limite_pesquisas = fields.Int(required=True)
    status = fields.Str(required=True)
