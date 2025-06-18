from src.database import db
from typing import List, Optional
from src.enums.interest_enum import InterestStatusEnum
from datetime import datetime

class PlanPurchaseInterest(db.Model):
    """
    Modelo para registrar o interesse de compra de planos pelos usuários
    
    Attributes:
        id (int): Identificador único do interesse
        user_id (int): ID do usuário interessado
        plan_id (int): ID do plano de interesse
        interest_date (datetime): Data em que o interesse foi registrado
        status (int): Status do interesse (1: pendente, 2: atendido, 3: cancelado)
        notes (str): Observações sobre o interesse
    """
    __tablename__ = 'plan_purchase_interest'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    interest_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Integer, nullable=False, default=InterestStatusEnum.PENDING.value)
    notes = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    user = db.relationship('User', back_populates='interests')
    plan = db.relationship('Plan', back_populates='purchase_interests', foreign_keys=[plan_id])
    
    def __repr__(self):
        return f'<PlanPurchaseInterest {self.id}>'
    
    def to_dict(self):
        """
        Converte o objeto de interesse para um dicionário
        
        Returns:
            dict: Dicionário com os dados do interesse
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'interest_date': self.interest_date.isoformat(),
            'status': InterestStatusEnum.from_int(self.status).to_str(),
            'notes': self.notes
        }
    
    @staticmethod
    def create_interest(user_id: int, plan_id: int, notes: str = None) -> 'PlanPurchaseInterest':
        """
        Cria um novo interesse de compra de plano
        
        Args:
            user_id (int): ID do usuário interessado
            plan_id (int): ID do plano de interesse
            notes (str, optional): Observações sobre o interesse
            
        Returns:
            PlanPurchaseInterest: Interesse criado
            
        Raises:
            Exception: Se houver erro ao criar o interesse
        """
        try:
            interest = PlanPurchaseInterest(
                user_id=user_id,
                plan_id=plan_id,
                notes=notes,
                status=InterestStatusEnum.PENDING.value
            )
            
            db.session.add(interest)
            db.session.commit()
            
            return interest
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao criar interesse de compra: {str(e)}")
    
    @staticmethod
    def get_user_interests(user_id: int) -> List['PlanPurchaseInterest']:
        """
        Obtém todos os interesses de um usuário específico
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            List[PlanPurchaseInterest]: Lista de interesses do usuário
        """
        try:
            return PlanPurchaseInterest.query.filter_by(user_id=user_id).all()
        except Exception as e:
            raise e
    
    @staticmethod
    def update_status(interest_id: int, new_status: int, notes: str = None) -> Optional['PlanPurchaseInterest']:
        """
        Atualiza o status de um interesse
        
        Args:
            interest_id (int): ID do interesse
            new_status (int): Novo status (1: pendente, 2: atendido, 3: cancelado)
            notes (str, optional): Observações sobre a atualização
            
        Returns:
            Optional[PlanPurchaseInterest]: Interesse atualizado ou None se não encontrado
            
        Raises:
            ValueError: Se o status fornecido for inválido
        """
        try:
            
            InterestStatusEnum.from_int(new_status)
            
            interest = PlanPurchaseInterest.query.get(interest_id)
            if not interest:
                return None
                
            interest.status = new_status
            
            if notes:
                interest.notes = notes
                
            db.session.commit()
            return interest
            
        except ValueError as e:
            raise ValueError(f"Status inválido: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise e


    @staticmethod
    def get_all_interests() -> List['PlanPurchaseInterest']:
        """
        Obtém todos os interesses de compra de planos
        
        Returns:
            List[PlanPurchaseInterest]: Lista de interesses de compra de planos
        """
        try:
            return PlanPurchaseInterest.query.all()
        except Exception as e:
            raise e

    @staticmethod
    def get_all_interests_with_relations() -> List[dict]:
        """
        Obtém todos os interesses de compra de planos incluindo dados do usuário e do plano
        
        Returns:
            List[dict]: Lista de interesses com dados relacionados
        """
        try:
            interests = PlanPurchaseInterest.query.all()
            return [{
                'id': interest.id,
                'interest_date': interest.interest_date.isoformat(),
                'status': InterestStatusEnum.from_int(interest.status).to_str(),
                'notes': interest.notes,
                'user': {
                    'id': interest.user.id,
                    'name': interest.user.nome_completo,
                    'email': interest.user.email,
                    'phone': interest.user.telefone,
                    'cnpj': interest.user.cnpj,
                    'cargo': interest.user.cargo,
                    'empresa': interest.user.empresa,
                    
                },
                'plan': {
                    'id': interest.plan.id,
                    'name': interest.plan.nome,
                    'description': interest.plan.descricao,
                    "price": interest.plan.preco
                }
            } for interest in interests]
        except Exception as e:
            raise e
        

    @staticmethod
    def get_interest_by_id(interest_id: int) -> Optional['PlanPurchaseInterest']:
        """
        Obtém um interesse pelo ID
        
        Args:
            interest_id (int): ID do interesse
            
        """
        try:
            return PlanPurchaseInterest.query.get(interest_id)
        except Exception as e:
            raise e

    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    
    @staticmethod
    def check_if_user_has_an_interest(user_id: int) -> bool:
        interest = PlanPurchaseInterest.query.filter_by(user_id=user_id, status=InterestStatusEnum.PENDING.value).first()
        return interest is not None
    