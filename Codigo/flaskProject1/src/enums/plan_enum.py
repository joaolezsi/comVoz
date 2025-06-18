from enum import Enum

class PlanEnum(Enum):
    FREE = {
        'nome': 'Free',
        'limite_pesquisas': 1,
        'limite_de_envios': 20,
        'preco': 0.0,
        'descricao': 'Plano gratuito com limite de 1 pesquisa'
    }
    
    BASIC = {
        'nome': 'Basic',
        'limite_pesquisas': 5,
        'limite_de_envios': 200,
        'preco': 29.90,
        'descricao': 'Plano básico com limite de 5 pesquisas'
    }
    
    PRO = {
        'nome': 'Pro',
        'limite_pesquisas': 20,
        'limite_de_envios': 1000,   
        'preco': 99.90,
        'descricao': 'Plano profissional com limite de 20 pesquisas'
    }
    
    ENTERPRISE = {
        'nome': 'Enterprise',
        'limite_pesquisas': 100,
        'limite_de_envios': 10000,
        'preco': 299.90,
        'descricao': 'Plano empresarial com limite de 100 pesquisas'
    } 
    
    
class PlanStatusEnum(Enum):
    ATIVO = 'ativo'
    FINALIZADO = 'finalizado'
    INATIVO = 'inativo'

