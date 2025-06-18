from flask_smorest import Blueprint, abort
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.schemas.respostas_schema import RespostasSchema
from src.controllers.respostas_controller import create_respostas_data
from marshmallow import ValidationError
from src.CustomExcepions import EmailAlreadyAnsweredException

responder_blueprint = Blueprint("responder", __name__, description="Endpoints para responder pesquisas")

@responder_blueprint.route("/respostas", methods=["POST"])
@responder_blueprint.arguments(RespostasSchema, location="json")
def responder(respostas_data: dict):
    try:
        
        respostas = create_respostas_data(respostas_data)
        return jsonify(respostas), 200
    
    except EmailAlreadyAnsweredException as e:
        return jsonify({"message": "Email já respondeu a pesquisa"}), 400
    

    except ValidationError as e:
        return jsonify({"message": "Erro ao criar respostas, existem respostas que nao condizem com o tipo da pergunta ou nao foram preenchidas"}), 400
    
    except Exception as e:
        return jsonify({"message": "Erro ao criar respostas"}), 500



