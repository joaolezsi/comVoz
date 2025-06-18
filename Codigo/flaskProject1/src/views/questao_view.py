from flask_smorest import Blueprint, abort
from flask import request, jsonify, make_response
from src.schemas.questoes_schema import CriarQuestaoSchema, ListaCriarQuestoesSchema, RetornoQuestaoSchema
from src.controllers.questao_controller import create_questao, get_all_questions
from src.CustomExcepions import UserNotFoundException
from flask_jwt_extended import jwt_required

questao_blueprint = Blueprint("questao", __name__, description="endpoints da pagina de questoes")


@questao_blueprint.route("/criar_questoes", methods=["POST"])
@questao_blueprint.arguments(ListaCriarQuestoesSchema)
@questao_blueprint.response(201)
@jwt_required()
def criar_questoes(criar_questoes_data: dict):
    try:
        user_id = criar_questoes_data.get('user_id')
        questoes_data = criar_questoes_data.get('questoes')
        
        if not user_id or not questoes_data:
            abort(400, message="Dados inválidos")
            
        questoes_criadas = create_questao(questoes_data, user_id)
        return questoes_criadas
    
    except UserNotFoundException as e:
        print(e)
        abort(404, message="Usuário não encontrado")
    
    except Exception as e:
        print(e)
        abort(500, message="Erro ao criar questões")



@questao_blueprint.route("/get_questoes/<int:user_id>", methods=["GET"])
@questao_blueprint.response(200)
@jwt_required()
def get_questoes(user_id: int):
    try:
        questoes = get_all_questions(user_id)
        return questoes
    except Exception as e:
        print(e)
        abort(500, message="Erro ao buscar questões")