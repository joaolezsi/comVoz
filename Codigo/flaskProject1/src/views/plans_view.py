from flask_smorest import Blueprint, abort
from flask import request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from src.schemas.plans_schema import PlanSchema, PlanRequestSchema, PlanUpdateSchema, SubscriptionResponseSchema, PlanPurchaseInterestSchema    
from src.CustomExcepions import MissingFieldsException, UserAlreadyExistsException, InvalidPasswordException, UserNotFoundException, UserAlreadyHasPlanException, PlanNotFoundException, UserNotAdminException, UserAlreadyHasInterestException
from src.middleware.basic_auth import BasicAuth
from src.models.plan_model import Plan
from src.controllers.plans_controller import check_payment_info, check_if_is_a_free_plan, check_if_user_has_an_active_plan, contratar_plano, get_all_plans, get_plan_by_id, update_plan_by_id, get_user_plan_by_id, register_interest_controller, get_interesses
from src.CustomExcepions import FreePlanException
from src.models.plan_purchase_interest import PlanPurchaseInterest

plans_blueprint = Blueprint("plans", __name__, description="Endpoints para gerenciar planos")


@plans_blueprint.route("/plans", methods=["GET"])
@plans_blueprint.response(200, PlanSchema(many=True))
@jwt_required()
def get_plans():
    try:
        plans = get_all_plans()
        return jsonify(plans), 200
    
    except PlanNotFoundException as e:
        print(e)
        return jsonify({"error": "Nenhum plano encontrado"}), 404
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao obter planos"}), 500


@plans_blueprint.route("/plan/<int:plan_id>", methods=["GET"])
@plans_blueprint.response(200, PlanSchema)
@jwt_required()
def get_plan_by_id(plan_id: int):
    try:
        plan = get_plan_by_id(plan_id)
        return jsonify(plan), 200
    
    except PlanNotFoundException as e:
        print(e)
        return jsonify({"error": "Plano não encontrado"}), 404
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao obter plano"}), 500


@plans_blueprint.route("/plans/update_plan/<int:plan_id>", methods=["POST"])
@plans_blueprint.arguments(PlanUpdateSchema)
@plans_blueprint.response(200, PlanSchema)
@jwt_required()
def update_plan(plan_info: dict, plan_id: int):
    try:
        plan = update_plan_by_id(plan_id, plan_info)
        return jsonify(plan), 200

    except PlanNotFoundException as e:
        print(e)
        return jsonify({"error": "Plano não encontrado"}), 404

    except Exception as e:
        print(e)        
        return jsonify({"error": "Erro ao atualizar plano"}), 500
    

@plans_blueprint.route("/plans/subscribe_plan", methods=["POST"])
@plans_blueprint.arguments(PlanRequestSchema)
@jwt_required()
def contratar_plano_pago(payment_info: dict):
    try:
        print(payment_info)
        plan_id = payment_info.get('plan_id')
        client_id = payment_info.get('user_id')
        interest_id = payment_info.get('interest_id')
    
        claims = get_jwt()
        print(claims)
        admin_id = get_jwt_identity()
        is_admin = claims.get('is_admin')
        
        if not is_admin:
            raise UserNotAdminException("Usuário não é administrador, contate o administrador do sistema para contratar um plano")
        
        is_free_plan = check_if_is_a_free_plan(plan_id)
        
        if is_free_plan:
            raise FreePlanException("Plano precisa ser pago")
    
        active_plan = check_if_user_has_an_active_plan(client_id)
            
        if active_plan:
            raise UserAlreadyHasPlanException("Usuário já possui um plano ativo")
        
        response = contratar_plano(plan_id, client_id, admin_id, interest_id)

        return response
    
    
    except UserNotAdminException as e:
        print(e)
        return jsonify({"error": "Usuário não é administrador, contate o administrador do sistema para contratar um plano"}), 400
    
    except UserAlreadyHasPlanException as e:
        print(e)
        return jsonify({"error": "Usuário já possui um plano ativo"}), 400

    except PlanNotFoundException as e:
        print(e)
        return jsonify({"error": "Plano não encontrado"}), 404

    except FreePlanException as e:
        print(e)
        return jsonify({"error": "Plano precisa ser pago"}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao contratar plano"}), 500



@plans_blueprint.route("/plans/get_user_plan/<int:user_id>", methods=["GET"])
@plans_blueprint.response(200, PlanSchema)
@jwt_required()
def get_user_plan(user_id: int):
    try:
        plan = get_user_plan_by_id(user_id)
        return jsonify(plan), 200
    
    except PlanNotFoundException as e:
        print(e)
        return jsonify({"error": "Plano usuario nao possui plano ativo ou finalizados no sistema"}), 404
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao obter plano do usuário"}), 500
    
    
   
@plans_blueprint.route("/plans/registrar_interesse", methods=["POST"])
@plans_blueprint.arguments(PlanPurchaseInterestSchema)
@jwt_required()
def register_interest(payment_info: dict):
    try: 
        user_id = payment_info.get('user_id')
        plan_id = payment_info.get('plan_id')
        
        if not user_id or not plan_id:
            return jsonify({"error": "user_id e plan_id são obrigatórios"}), 400
        
        response = register_interest_controller(user_id, plan_id)

        return jsonify("Interesse registrado com sucesso e enviado por email para Administração, aguarde a resposta !"), 200
    
    except UserAlreadyHasInterestException as e:
        print(e)
        return jsonify({"error": "Você já possui um interesse em um plano pago, não é possivel registrar outro interesse"}), 409
    
    except UserAlreadyHasPlanException as e:
        print(e)
        return jsonify({"error": "Você já possui um plano pago ativo mais caro, não é possivel contratar um plano pago mais barato"}), 400
        
    except UserNotFoundException as e:
        print(e)
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    except PlanNotFoundException as e:
        print(e)
        return jsonify({"error": "Plano não encontrado"}), 404
    
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao registrar interesse"}), 500
    
    
    
@plans_blueprint.route("/plans/get_all_interesses", methods=["GET"])
@jwt_required()
def get_all_interesses():
    try:
        claims = get_jwt()
        user_id = get_jwt_identity()
        is_admin = claims.get('is_admin')
        
        if not is_admin:
            raise UserNotAdminException("Usuário não é administrador")
        
        interesses = get_interesses(user_id)
        return jsonify(interesses), 200
    
    except UserNotFoundException as e:
        print(e)
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    except UserNotAdminException as e:
        print(e)
        return jsonify({"error": "Usuário não é administrador"}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao obter todos os interesses"}), 500

@plans_blueprint.route("/plans/get_user_interests/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_interests(user_id: int):
    try:
        interesses = PlanPurchaseInterest.get_user_interests(user_id)
        return jsonify([interesse.to_dict() for interesse in interesses]), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao obter interesses do usuário"}), 500



