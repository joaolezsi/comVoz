from datetime import datetime
from src.database import db
from typing import Optional, Dict, Any
from src.CustomExcepions import PlanNotFoundException, UserAlreadyHasPlanException, UserHasBetterPlanException
from src.models.plan_model import Plan
from src.enums.plan_enum import PlanStatusEnum

class PlanoContratado(db.Model):
    """
    Modelo para gerenciar os planos contratados pelos usuários
    
    Attributes:
        id (int): Identificador único do plano contratado
        user_id (int): ID do usuário
        plan_id (int): ID do plano
        limite_pesquisas (int): Limite de pesquisas disponíveis
        status (str): Status do plano (ATIVO/INATIVO)
    """
    __tablename__ = 'user_subscription'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    limite_pesquisas = db.Column(db.Integer, nullable=False)
    limite_de_envios = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    
    
    @staticmethod
    def check_if_user_has_free_plan(user_id: int) -> Optional['PlanoContratado']:
        """
        Verifica se o usuário tem um plano gratuito
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            Optional[PlanoContratado]: Plano gratuito ou None
        """
        try:
            free_plan = Plan.get_by_name('Free')
            if not free_plan:
                raise PlanNotFoundException("Plano gratuito não encontrado")

            plano_gratuito = PlanoContratado.query.filter_by(
                user_id=user_id,
                plan_id=free_plan.id,
                status=PlanStatusEnum.ATIVO.value
            ).first()
        
            if plano_gratuito:
                return plano_gratuito
        
            return None
        except Exception as e:
            db.session.rollback()
            raise e
        
    
    @staticmethod
    def get_plano_ativo_usuario(user_id: int) -> Optional['PlanoContratado']:
        """
        Retorna o plano do usuário
        """
        try:
            return PlanoContratado.query.filter_by(user_id=user_id, status=PlanStatusEnum.ATIVO.value).first()
        except Exception as e:
            db.session.rollback()
            raise e
        
        
    @staticmethod
    def get_plano_finalizado_ou_ativo_usuario(user_id: int) -> Optional['PlanoContratado']:
        """
        Retorna o plano do usuário
        """
        try:
            plano = PlanoContratado.query.filter_by(user_id=user_id, status=PlanStatusEnum.ATIVO.value).first()
            if plano is None:
                plano = PlanoContratado.query.filter_by(user_id=user_id, status=PlanStatusEnum.FINALIZADO.value).first()
                
                if plano is None:
                    return None
                
            return plano
        except Exception as e:
            db.session.rollback()
            raise e
        
        
    def decrementar_limite_de_envios(self, numero_de_envios: int) -> bool:
        """
        Decrementa o limite de envios do plano.
        """
        try:
            self.limite_de_envios -= numero_de_envios
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def get_planos_pagos_ativos(user_id: int) -> Optional['PlanoContratado']:
        """
        Retorna o plano ativo do usuário
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            Optional[PlanoContratado]: Plano ativo ou None
        """
        try:
            plano_gratuito = Plan.get_by_name('Free')
           
            
            planos= PlanoContratado.query.filter_by(
                user_id=user_id,
                status=PlanStatusEnum.ATIVO.value
            ).filter(
                PlanoContratado.plan_id != plano_gratuito.id
            ).all()
            
            if planos:
                return planos[0]
            
            return None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao obter plano ativo: {e}")
            raise e
        
        
    @staticmethod
    def contratar_plano(user_id: int, plan: Plan) -> 'PlanoContratado':
        """
        Contrata um novo plano pago para o usuário
        """
        try:
            plano_gratuito = PlanoContratado.check_if_user_has_free_plan(user_id)
            plano_pago_existente = PlanoContratado.get_plano_ativo_usuario(user_id)
            
            if plano_gratuito is not None:
            
                if plano_gratuito.limite_pesquisas == 1:
                    plano_gratuito.decrementar_limite_pesquisas()
                    plan.limite_pesquisas += 1
                    plan.limite_de_envios += 20
            
            elif plano_pago_existente is not None:
                plan.limite_pesquisas += plano_pago_existente.limite_pesquisas
                plan.limite_de_envios += plano_pago_existente.limite_de_envios
                plano_pago_existente.status = PlanStatusEnum.INATIVO.value
                plano_pago_existente.limite_pesquisas = 0
                plano_pago_existente.limite_de_envios = 0
                db.session.commit()
                    
            plano_contratado = PlanoContratado(
                user_id=user_id,
                plan_id=plan.id,
                limite_pesquisas=plan.limite_pesquisas,
                limite_de_envios=plan.limite_de_envios,
                status=PlanStatusEnum.ATIVO.value
            )
        
            db.session.add(plano_contratado)
            db.session.commit()
        
            return plano_contratado
        except UserAlreadyHasPlanException as e:
            print(e)
            raise UserAlreadyHasPlanException("Usuário já possui um plano ativo")
        
        except Exception as e:
            print(f"Erro ao contratar plano: {e}")
            db.session.rollback()
            raise e
    
    @staticmethod
    def setar_plano_gratuito(user_id: int) -> 'PlanoContratado':
        """
        Contrata um novo plano para o usuário
        
        Args:
            user_id (int): ID do usuário
            plan_id (int): ID do plano
            
        Returns:
            PlanoContratado: Plano contratado
            
        Raises:
            PlanNotFoundException: Se o plano não for encontrado
            UserAlreadyHasPlanException: Se o usuário já tiver um plano ativo
        """
        try:
            plan = Plan.get_by_name('Free')
            if not plan:
                raise PlanNotFoundException("Plano não encontrado")
            
            plano_gratuito = PlanoContratado.check_if_user_has_free_plan(user_id)
            if plano_gratuito is not None:
                raise UserAlreadyHasPlanException("Usuário já possui um plano gratuito")
            
            plano_gratuito_contratado = PlanoContratado(
                user_id=user_id,
                plan_id=plan.id,
                limite_pesquisas=plan.limite_pesquisas,
                limite_de_envios=plan.limite_de_envios,
                status=PlanStatusEnum.ATIVO.value
            )
            
            db.session.add(plano_gratuito_contratado)
            db.session.commit()
            
            return plano_gratuito_contratado
        except Exception as e:
            print(f"Erro ao contratar plano gratuito: {e}")
            db.session.rollback()
            raise e
    
    def decrementar_limite_pesquisas(self) -> bool:
        """
        Decrementa o limite de pesquisas do plano.
        Se o limite chegar a zero, o plano é marcado como inativo.
        
        Returns:
            bool: True se o limite foi decrementado, False se não há mais limite
        """
        try:
            if self.limite_pesquisas <= 0 or self.status == PlanStatusEnum.INATIVO.value:
                return False
                
            if self.limite_pesquisas > 0:
                self.limite_pesquisas -= 1
                db.session.commit()
            
            if self.limite_pesquisas == 0:
                self.status = PlanStatusEnum.FINALIZADO.value
                db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto para dicionário
        
        Returns:
            Dict[str, Any]: Dicionário com os dados do plano contratado
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'limite_pesquisas': self.limite_pesquisas,
            'status': self.status
        } 