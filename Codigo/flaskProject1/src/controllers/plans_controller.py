from src.models.plano_contratado_model import PlanoContratado
from src.models.plan_model import Plan
from src.CustomExcepions import PlanNotFoundException, FreePlanException, UserNotFoundException, UserAlreadyHasPlanException, UserNotAdminException, PlanPurchaseInterestNotFoundException, UserAlreadyHasInterestException
from src.models.user_model import User
from src.models.interest_model import PlanPurchaseInterest
from src.models.user_admin_model import UserAdmin
from src.enums.interest_enum import InterestStatusEnum
from src.utils.email_sender import EmailSender
from typing import List

def contratar_plano(plan_id: int, client_id: int, admin_id: int, interest_id: int):
    try:
        
        # pagamento = Pagamento.get_by_id(pagamento_id)
        
        user = User.get_by_id(client_id)
        
        admin = User.get_by_id(admin_id)
    
        if not user or not admin:
            raise UserNotFoundException("Usuário não encontrado")
        
        plano = Plan.get_by_id(plan_id)
        
        if not plano:
            raise PlanNotFoundException("Plano não encontrado")
        
        plano_contratado = PlanoContratado.contratar_plano(client_id, plano)
        
        interest = PlanPurchaseInterest.get_interest_by_id(interest_id)
        
        if not interest:
            raise PlanPurchaseInterestNotFoundException("Interesse não encontrado")
        
        if interest.status == InterestStatusEnum.PENDING.value:
            interest.status = InterestStatusEnum.ATTENDED.value
            interest.save()
        
        return plano_contratado.to_dict()
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e


def update_plan_by_id(plan_id: int, plan_info: dict):
    try:
        plan = Plan.update_by_id(plan_id, plan_info)
        return plan
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e


def get_all_plans():
    try:
        plans = Plan.get_all()
        return [plan.to_dict() for plan in plans]
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e


def get_plan_by_id(plan_id: int):
    try:
        plan = Plan.get_by_id(plan_id)
        return plan.to_dict()
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e


def check_payment_info(payment_info: dict):
    try:
        plan_id = payment_info.get('plan_id')
        user_id = payment_info.get('user_id')
        return plan_id, user_id
    except Exception as e:
        print(e)
        raise e
     
def check_if_is_a_free_plan(plan_id: int)-> bool:
    try:
        
        plan = Plan.get_by_id(plan_id)
        if not plan or plan.nome == 'Free':
            return True
        return False
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e
    
def check_if_user_has_an_active_plan(user_id: int)-> bool:
    try:
        plano_ativo = PlanoContratado.get_planos_pagos_ativos(user_id)
            
        if plano_ativo is not None:
            return plano_ativo
        
        return False
    
    except Exception as e:
        print(e)
        raise e
    
    

def get_user_plan_by_id(user_id: int):
    try:
        plano_contratado = PlanoContratado.get_plano_finalizado_ou_ativo_usuario(user_id)
        if not plano_contratado:
            raise PlanNotFoundException("Usuário não possui plano ativo / finalizado")
        
        # Buscar os dados completos do plano
        plano = Plan.get_by_id(plano_contratado.plan_id)
        if not plano:
            raise PlanNotFoundException("Plano não encontrado")
        
        # Retornar dados do plano com informações do plano contratado
        plano_data = plano.to_dict()
        plano_data['limite_pesquisas'] = plano_contratado.limite_pesquisas  # Usar limite atual do usuário
        plano_data['status'] = plano_contratado.status
        
        return plano_data
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e
    
    
def register_interest_controller(user_id: int, plan_id: int):
    try:
        
        email_sender = EmailSender()
        
        user  = User.get_by_id(user_id)
        
        if PlanPurchaseInterest.check_if_user_has_an_interest(user_id):
            raise UserAlreadyHasInterestException("Usuário já possui um interesse pendente")
        
        
        if not user:
            raise UserNotFoundException("Usuário não encontrado")
        
        plan_of_interest = Plan.get_by_id(plan_id)
        
        if not plan_of_interest:
            raise PlanNotFoundException("Plano não encontrado")
        
        user_has_plan = check_if_user_has_a_paid_plan(user_id, plan_of_interest)

        admins = UserAdmin.get_all_admins()
        
        if user_has_plan:
            user_plan = PlanoContratado.get_plano_ativo_usuario(user_id)
            
            plano_do_usuario  = Plan.get_by_id(user_plan.plan_id)

            message = f"O usuário {user.nome_completo} está interessado em contratar o plano {plan_of_interest.nome} e já possui um plano ativo {plano_do_usuario.nome}. Caso queira adicionar a diferença de preço e adicionar o numero de pesquisas, custará {plan_of_interest.preco - plano_do_usuario.preco} reais e será adicionado {plan_of_interest.limite_pesquisas - plano_do_usuario.limite_pesquisas} pesquisas. Entre em contato com o email {user.email} ou  {user.telefone} para concluir a venda."

            plan_interest = PlanPurchaseInterest.create_interest(user_id, plan_id, message)
            
            
            email_sender.send_plan_interest_notification_with_plan(user, plan_of_interest, admins, plano_do_usuario)
        
        else:
            message = f"O usuário {user.nome_completo} está interessado em contratar o plano {plan_of_interest.nome} e {plan_of_interest.preco} reais, porém não possui um plano ativo. Entre em contato com o email {user.email} ou  {user.telefone} para concluir a venda."
            
            plan_interest = PlanPurchaseInterest.create_interest(user_id, plan_id, message)
            
            email_sender.send_plan_interest_notification_without_plan(user, plan_of_interest, admins)
        
        return plan_interest.to_dict()
    
    except UserAlreadyHasInterestException as e:
        print(e)
        raise UserAlreadyHasInterestException
        
    except UserAlreadyHasPlanException as e:
        print(e)
        raise UserAlreadyHasPlanException
        
    except UserNotFoundException as e:
        print(e)
        raise UserNotFoundException
    
    except PlanNotFoundException as e:
        print(e)
        raise PlanNotFoundException
    
    except Exception as e:
        print(e)
        raise e
    
    
def get_interesses(user_id: int) -> List[PlanPurchaseInterest]:
    try:
        
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException("Usuário não encontrado")
        
        interesses = PlanPurchaseInterest.get_all_interests_with_relations()
        
        return interesses
    
    except UserNotFoundException as e:
        print(e)
        raise e
    
    except UserNotAdminException as e:
        print(e)
        raise e
    
    except Exception as e:
        print(e)
        raise e 



def check_if_user_has_a_paid_plan(user_id: int, plan_of_interest: Plan) -> bool:
    try:
        plano_contratado = PlanoContratado.get_planos_pagos_ativos(user_id)
        
        if plano_contratado is not None:
            # Busca o plano atual do usuário
            plano_atual = Plan.get_by_id(plano_contratado.plan_id)
            
            if plan_of_interest.preco > plano_atual.preco:
                return True
            else:
                raise UserAlreadyHasPlanException("Usuário já possui um plano ativo mais caro")
        else:
            return False
    
    except Exception as e:
        print(e)
        raise e