from flask_smorest import Blueprint, abort
from flask import request, jsonify, make_response
from src.schemas.users_schemas import RegisterUserSchema, LoginUserSchema, LoggedUserSchema
from src.CustomExcepions import MissingFieldsException, UserAlreadyExistsException, InvalidPasswordException, UserNotFoundException
from src.controllers.user_controllers import check_user_registration_data, create_new_user, login_user, update_user_profile
from src.middleware.basic_auth import BasicAuth
from flask_jwt_extended import jwt_required, get_jwt_identity

user_blueprint = Blueprint("pagina_de_usuarios", __name__, description="endpoints da pagina de usuarios")


@user_blueprint.route("/usuarios/resgistrar", methods=["POST"])
@user_blueprint.arguments(RegisterUserSchema)
@user_blueprint.response(201, LoggedUserSchema)
def registrar_usuario(user_data: dict):
    try:
        check_user_registration_data(user_data)
        
        new_user = create_new_user(user_data)
        
        # Cria resposta com token no header
        response = make_response(jsonify(new_user), 201)
        if 'token' in new_user:
            response.headers['Authorization'] = f"Bearer {new_user['token']}"
        
        return response
        
    except MissingFieldsException as e:
        print(e)
        return jsonify({"error": "Está faltando campos obrigatórios para o registro do usuário"}), 400
    except UserAlreadyExistsException as e:
        print(e)
        return jsonify({"error": "O usuário já existe"}), 409
    except InvalidPasswordException as e:
        print(e)
        return jsonify({"error": "As senhas não conferem"}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao registrar o usuário"}), 500
    

@user_blueprint.route("/usuarios/login", methods=["GET"])
@user_blueprint.response(200, LoggedUserSchema)
def login_usuario():
    try:
        username, password = BasicAuth.decode_auth(request.headers.get("Authorization"))
        
        if not username or not password:
            return jsonify({"error": "Credenciais inválidas"}), 401
        
        logged_user = login_user(username, password)

        # Cria resposta com token no header
        response = make_response(jsonify(logged_user), 200)
        if 'token' in logged_user:
            response.headers['Authorization'] = f"Bearer {logged_user['token']}"
        
        return response

    except UserNotFoundException as e:
        print(e)
        return jsonify({"error": "Usuário não encontrado"}), 404
    except InvalidPasswordException as e:
        print(e)
        return jsonify({"error": "Senha inválida"}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro ao fazer login"}), 500


@user_blueprint.route("/usuarios/perfil", methods=["PUT"])
@jwt_required()
def atualizar_perfil():
    try:
        user_id = get_jwt_identity()
        
        # Verificar se é JSON
        if not request.is_json:
            return jsonify({"error": "Content-Type deve ser application/json"}), 400
            
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400
        
        print(f"Dados recebidos para atualização: {user_data}")  # Debug
        
        updated_user = update_user_profile(int(user_id), user_data)
        
        if not updated_user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        return jsonify({
            "message": "Perfil atualizado com sucesso",
            "user": updated_user
        }), 200
        
    except ValueError as e:
        print(f"Erro de validação: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Erro ao atualizar perfil: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500


@user_blueprint.route("/usuarios/perfil", methods=["GET"])
@jwt_required()
def obter_perfil():
    try:
        user_id = get_jwt_identity()
        print(f"Obtendo perfil para usuário ID: {user_id}")  # Debug
        
        from src.models.user_model import User
        from src.models.plano_contratado_model import PlanoContratado
        
        user = User.get_by_id(int(user_id))
        
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        user_dict = user.to_dict()
        
        # Adiciona informação se é admin
        user_dict['is_admin'] = User.is_user_admin(user.id)
        
        # Adiciona plano contratado
        user_plan = PlanoContratado.get_plano_ativo_usuario(user.id)
        if user_plan:
            user_dict['plano_contratado'] = user_plan.to_dict()
        else:
            user_dict['plano_contratado'] = None
        
        return jsonify(user_dict), 200
        
    except Exception as e:
        print(f"Erro ao obter perfil: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

