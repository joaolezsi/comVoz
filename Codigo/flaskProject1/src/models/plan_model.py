from datetime import datetime
from src.database import db, bcrypt, jwt
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import re
from typing import Optional, List, Dict, Any
from src.CustomExcepions import InvalidPasswordException, PlanNotFoundException
from src.enums.plan_enum import PlanEnum



class Plan(db.Model):
    """
    Modelo de plano para o sistema
    
    Attributes:
        id (int): Identificador único do plano
        nome (str): Nome do plano
        limite_pesquisas (int): Limite de pesquisas por ano
        preco (float): Preço do plano
        descricao (str): Descrição do plano
    """
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    limite_pesquisas = db.Column(db.Integer, nullable=False)
    limite_de_envios = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    
    # Relacionamentos
    planos_contratados = db.relationship('PlanoContratado', backref='plan', lazy=True)
    purchase_interests = db.relationship('PlanPurchaseInterest', back_populates='plan', lazy=True)
    
    def __repr__(self):
        return f"<Plan(id={self.id}, nome='{self.nome}', limite_pesquisas={self.limite_pesquisas}, preco={self.preco}, descricao='{self.descricao}')>"
    
    def to_dict(self):
        """
        Converte o objeto Plan em um dicionário
        
        Returns:
            dict: Dicionário com os dados do plano
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'limite_pesquisas': self.limite_pesquisas,
            'limite_de_envios': self.limite_de_envios,
            'preco': self.preco,
            'descricao': self.descricao
        }
    
    @staticmethod
    def init_plans():
        """Inicializa os planos base no banco de dados"""
        for plan_enum in PlanEnum:
            plan_data = plan_enum.value
            if not Plan.query.filter_by(nome=plan_data['nome']).first():
                plan = Plan(**plan_data)
                db.session.add(plan)
        
        db.session.commit()
        
        
    @staticmethod
    def get_all() -> List['Plan']:
        """
        Busca todos os planos cadastrados
        
        Returns:
            List[Dict[str, Any]]: Lista de planos encontrados
        """
        try:
            plans = Plan.query.all()
            
            if not plans:
                raise PlanNotFoundException("Nenhum plano encontrado")
            
            return plans
        
        except PlanNotFoundException as e:
            print(e)
            raise PlanNotFoundException
        
        except Exception as e:
            print(e)
            raise e
    
    
    @staticmethod
    def get_by_id(plan_id: int) -> Optional['Plan']:
        """
        Busca um plano pelo ID
        
        Args:
            plan_id (int): ID do plano
            
        Returns:
            Plan: Plano encontrado ou None se não encontrado
        """
        try:
            plan = Plan.query.get(plan_id)
            if not plan:
                raise PlanNotFoundException("Plano não encontrado")
            return plan
        except PlanNotFoundException as e:
            print(e)
            raise PlanNotFoundException
        
        except Exception as e:
            print(e)
            raise e
    

    @staticmethod
    def get_by_name(nome: str) -> Optional['Plan']:
        """
        Busca um plano pelo nome
        
        Args:   
            nome (str): Nome do plano
            
        Returns:
            Plan: Plano encontrado ou None se não encontrado
        """
        try:
            return Plan.query.filter_by(nome=nome).first()
        except Exception as e:
            raise e
    
    
    
    @staticmethod
    def update_by_id(plan_id: int, plan_info: dict) -> Optional['Plan']:
        """
        Atualiza um plano pelo ID
        
        
        """
        try:
            plan = Plan.query.get(plan_id)
            if not plan:
                raise PlanNotFoundException("Plano não encontrado")
            
            plan.nome = plan_info['nome']
            plan.descricao = plan_info['descricao']
            plan.preco = plan_info['preco']
            plan.limite_pesquisas = plan_info['limite_pesquisas']
            plan.limite_de_envios = plan_info['limite_de_envios']
            
            db.session.commit()
            
            
            return plan.to_dict()
        
        except PlanNotFoundException as e:
            print(e)
            raise PlanNotFoundException
        
        except Exception as e:
            print(e)
            raise e

