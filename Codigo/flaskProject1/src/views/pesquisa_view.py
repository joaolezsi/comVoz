from flask_smorest import Blueprint, abort
from flask import request, jsonify
from src.models.pesquisa_model import Pesquisa
from src.models.user_model import User
from marshmallow import Schema, fields, validate
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from src.schemas.pesquisa_schema import PesquisaSchema, PesquisaResponseSchema, QuestoesToUpdateSchema
from src.controllers.pesquisa_controller import criar_nova_pesquisa, buscar_todas_pesquisas, buscar_pesquisa_por_id, desativar_pesquisa, deletar_pesquisa, atualizar_pesquisa, enviar_pesquisa_controller, ativar_pesquisa
from src.controllers.dashboard_controller import get_estatisticas_pesquisa_frontend
from src.CustomExcepions import LimitePesquisaException, UserNotFoundError, QuestionNotFoundException, PesquisaNotFoundException, EmailSenderException, LimiteEnviosException, UserWithoutContatosException, UserWithoutPlanException, NpsQuestionsException


pesquisa_blueprint = Blueprint("pesquisas", __name__, description="Endpoints para gerenciamento de pesquisas")

@pesquisa_blueprint.route("/criar_pesquisa", methods=["POST"])
@pesquisa_blueprint.arguments(PesquisaSchema)	
@jwt_required()
def criar_pesquisa(pesquisa_data: dict):
    """Cria uma nova pesquisa"""
    try:
    
        pesquisa_dict = criar_nova_pesquisa(pesquisa_data)
        
        return jsonify(pesquisa_dict), 201
    
    except NpsQuestionsException as e:
        return jsonify({"error": "A pesquisa deve conter pelo menos 5 perguntas do tipo NPS para gerar um dashboard adequado"}), 400
    
    except QuestionNotFoundException as e:
        return jsonify({"error": 'Pergunta não encontrada'}), 404
    
    except UserNotFoundError as e:
        return jsonify({"error": 'Usuário não encontrado'}), 404
     
    except LimitePesquisaException as e:
        return jsonify({"error": 'Limite de pesquisas atingido'}), 400
        
    except Exception as e:
        print(f"Erro ao criar pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao criar pesquisa"}), 500


@pesquisa_blueprint.route("/pesquisas", methods=["GET"])
@pesquisa_blueprint.response(200, PesquisaSchema(many=True))
@jwt_required()
def listar_pesquisas():
    """Lista todas as pesquisas"""
    try:
        
        user_id = get_jwt_identity()
        
        print(user_id)
        
        ativa = request.args.get("ativa", None)
        
        pesquisas = buscar_todas_pesquisas(user_id, ativa)
        return jsonify(pesquisas), 200
        
    except Exception as e:
        print(f"Erro ao listar pesquisas: {str(e)}")
        return jsonify({"error": "Erro ao listar pesquisas"}), 500


@pesquisa_blueprint.route("/pesquisas/<string:pesquisa_id>", methods=["GET"])
def obter_pesquisa(pesquisa_id: str):
    """Obtém uma pesquisa pelo ID"""
    try:
        pesquisa = buscar_pesquisa_por_id(pesquisa_id)
        
        return jsonify(pesquisa), 200
    
    except PesquisaNotFoundException as e:  
        return jsonify({"error": str(e)}), 404
    
    except Exception as e:
        print(f"Erro ao obter pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao obter pesquisa"}), 500


@pesquisa_blueprint.route("/pesquisas/<string:pesquisa_id>", methods=["PUT"])
@pesquisa_blueprint.arguments(QuestoesToUpdateSchema)
@jwt_required()
def update_pesquisa(questoes_data: dict, pesquisa_id: str):
    """Atualiza uma pesquisa existente"""
    try:
        
        ids_perguntas = questoes_data['perguntas']
        
        pesquisa_atualizada = atualizar_pesquisa(pesquisa_id, ids_perguntas)
        
        return jsonify(pesquisa_atualizada), 200
      

    except QuestionNotFoundException as e:
        return jsonify({"error": 'Pergunta não encontrada'}), 404
    
    except PesquisaNotFoundException as e:
        return jsonify({"error": 'Pesquisa não encontrada'}), 404
    
    except Exception as e:
        print(f"Erro ao atualizar pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao atualizar pesquisa"}), 500
        
        


@pesquisa_blueprint.route("/pesquisas/<string:pesquisa_id>", methods=["DELETE"])
@jwt_required()
def remover_pesquisa(pesquisa_id: str):
    """Remove uma pesquisa"""
    try:
        
        deleted = deletar_pesquisa(pesquisa_id)
    
        if deleted:
            return jsonify({"message": "Pesquisa removida com sucesso"}), 200
     
    except PesquisaNotFoundException as e:  
        return jsonify({"error": 'Pesquisa não encontrada'}), 404 
        
    except Exception as e:
        print(f"Erro ao remover pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao remover pesquisa"}), 500


@pesquisa_blueprint.route("/pesquisas/<string:pesquisa_id>/desativar", methods=["PATCH"])
@jwt_required()
def desativar(pesquisa_id: str):
    """Desativa uma pesquisa"""
    try:
        
        pesquisa_desativada = desativar_pesquisa(pesquisa_id)
        
        formatted_pesquisa = pesquisa_desativada.to_dict()
        
        return jsonify(formatted_pesquisa), 200
    
    
    except PesquisaNotFoundException as e:  
        return jsonify({"error": 'Pesquisa não encontrada'}), 404
        
    except Exception as e:
        print(f"Erro ao desativar pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao desativar pesquisa"}), 500 
    
    
    
@pesquisa_blueprint.route("/pesquisas/enviar_pesquisa/<string:pesquisa_id>", methods=["POST"])
@jwt_required()
def enviar_pesquisa(pesquisa_id: str):
    """Envia uma pesquisa para um usuário"""
    try:
        user_id = get_jwt_identity()

        resposta = enviar_pesquisa_controller(pesquisa_id, user_id)
        
        return jsonify({"message": resposta}), 200
    
    except UserWithoutPlanException as e:
        return jsonify({"error": str(e)}), 400
    
    except UserNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    
    except PesquisaNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    
    except UserWithoutContatosException as e:
        return jsonify({"error": str(e)}), 400
    
    except LimiteEnviosException as e:
        return jsonify({"error": str(e)}), 400
    
    except EmailSenderException as e:
        return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        print(f"Erro ao enviar pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao enviar pesquisa"}), 500
    
    
@pesquisa_blueprint.route("/pesquisas/<string:pesquisa_id>/ativar", methods=["PATCH"])
@jwt_required()
def ativar(pesquisa_id: str):
    """Ativa uma pesquisa"""
    try:
        pesquisa_ativada = ativar_pesquisa(pesquisa_id)
        formatted_pesquisa = pesquisa_ativada.to_dict()
        return jsonify(formatted_pesquisa), 200
    
    except PesquisaNotFoundException as e:  
        return jsonify({"error": 'Pesquisa não encontrada'}), 404
        
    except Exception as e:
        print(f"Erro ao ativar pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao ativar pesquisa"}), 500
    
    
@pesquisa_blueprint.route("/pesquisas/<string:pesquisa_id>/estatisticas", methods=["GET"])
@jwt_required()
def obter_estatisticas_pesquisa(pesquisa_id: str):
    """Obtém estatísticas detalhadas de uma pesquisa"""
    try:
        estatisticas = get_estatisticas_pesquisa_frontend(pesquisa_id)
        return jsonify(estatisticas), 200
    
    except PesquisaNotFoundException as e:
        return jsonify({"error": "Pesquisa não encontrada"}), 404
    
    except Exception as e:
        print(f"Erro ao obter estatísticas da pesquisa: {str(e)}")
        return jsonify({"error": "Erro ao obter estatísticas da pesquisa"}), 500
    
    
