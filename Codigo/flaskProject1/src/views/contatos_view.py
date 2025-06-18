from flask_smorest import Blueprint, abort
from flask import request, jsonify
from src.models.pesquisa_model import Pesquisa
from src.models.user_model import User
from marshmallow import Schema, fields, validate
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.CustomExcepions import LimitePesquisaException, UserNotFoundError, InvalidDataException
from src.controllers.contatos_controller import buscar_contatos, criar_contatos_by_list, allowed_file, criar_contatos_excel
from src.schemas.contatos_schema import CreateContatoSchema
from werkzeug.utils import secure_filename
from src.globalvars import UPLOAD_FOLDER
import os


contatos_blueprint = Blueprint("contatos", __name__, description="Endpoints para gerenciamento de contatos")


@contatos_blueprint.route("/contatos", methods=["GET"])
@jwt_required()
def listar_contatos():
    try:
        user_id = get_jwt_identity()
        
        contatos = buscar_contatos(user_id)
        
        return jsonify(contatos), 200
    
    except UserNotFoundError as e:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    except Exception as e:
        return jsonify({"error": "Erro ao listar contatos"}), 500


@contatos_blueprint.route("/contatos", methods=["POST"])
@contatos_blueprint.arguments(CreateContatoSchema)
@jwt_required()
def criar_contato(contato_data: dict):
    try:
        user_id = get_jwt_identity()
        
        contato_list = [contato_data]
        
        if not contato_list:
            raise InvalidDataException("Nenhum contato fornecido")
        
        contato = criar_contatos_by_list(contato_list, user_id)
        
        return jsonify(contato), 201
    
    except InvalidDataException as e:
        return jsonify({"error": "Dados inválidos"}), 400
    
    except UserNotFoundError as e:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    except Exception as e:
        return jsonify({"error": "Erro ao criar contato"}), 500



@contatos_blueprint.route("/contatos/by_excel", methods=["POST"])
@jwt_required()
def criar_contatos_by_excel():
    try:
        user_id = get_jwt_identity()
        print(f"Recebendo arquivo para user_id={user_id}")

        if 'file' not in request.files:
            print("Nenhum arquivo enviado no request.")
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        file = request.files['file']

        if file.filename == '':
            print("Nenhum arquivo selecionado.")
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(f"Nome do arquivo recebido: {filename}")
            print(f"UPLOAD_FOLDER: {UPLOAD_FOLDER}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            print(f"Arquivo salvo em: {file_path}")
            print("Chamando criar_contatos_excel...")
            contatos = criar_contatos_excel(filename, user_id)
            print("Retornando contatos criados.")
            return jsonify({
                "message": "Contatos criados com sucesso",
                "contatos": contatos
            }), 201
        else:
            print("Tipo de arquivo não permitido.")
            return jsonify({"error": "Tipo de arquivo não permitido. Use apenas arquivos .xlsx, .xls ou .csv"}), 400

    except InvalidDataException as e:
        print(f"Erro de dados: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print(f"Erro inesperado na view: {str(e)}")
        return jsonify({"error": "Erro ao criar contatos por excel"}), 500


@contatos_blueprint.route("/contatos", methods=["GET"])
@jwt_required()
def get_contatos_by_user_id():
    try:
        user_id = get_jwt_identity()
        contatos = buscar_contatos(user_id)
        return jsonify(contatos), 200
    
    except UserNotFoundError as e:
        return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao buscar contatos"}), 500
