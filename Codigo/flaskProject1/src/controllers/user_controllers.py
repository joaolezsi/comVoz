from src.CustomExcepions import MissingFieldsException, UserAlreadyExistsException, InvalidPasswordException, UserNotFoundException
from src.models.user_model import User
from src.models.plano_contratado_model import PlanoContratado


def check_user_registration_data(user_data: dict) -> None:
    try:
        required_fields = ['nome_completo', 'email', 'password', 'passwordRepeat', 'telefone', 'empresa', 'cargo', 'cnpj']
        
        if not all(field in user_data for field in required_fields):
            raise MissingFieldsException
        
        password = user_data['password']
        password_repeat = user_data['passwordRepeat']
        
        if password != password_repeat:
            raise InvalidPasswordException
        
        
    except MissingFieldsException:
        raise MissingFieldsException("Todos os campos são obrigatórios")
    
    except InvalidPasswordException:
        raise InvalidPasswordException("As senhas não conferem")
    
    except Exception as e:
        raise e
    


def create_new_user(user_data: dict) -> dict:
    try:
        
        user_exists = User.get_by_email(user_data['email'])
        
        if user_exists is not None:
            raise UserAlreadyExistsException
        
        new_user = User.create_user(user_data)
        
        token = new_user.generate_jwt()
        
        
        user_dict = new_user.to_dict()
        user_dict['token'] = token
        
        user_plan = PlanoContratado.get_plano_ativo_usuario(new_user.id)
        
        if user_plan is not None:
            user_dict['plano_contratado'] = user_plan.to_dict()
        else:
            user_dict['plano_contratado'] = None
        
        return user_dict
        
        
    except UserAlreadyExistsException:
        raise UserAlreadyExistsException("O usuário já existe")
    
    except Exception as e:
        raise e
    


def login_user(username: str, password: str) -> dict:
    try:
        user = User.get_by_email(username)
        
        if not user:
            raise UserNotFoundException
        
        if not user.check_password(password):
            raise InvalidPasswordException
        

        token = user.generate_jwt()
        
        user_dict = user.to_dict()
        
        if User.is_user_admin(user.id):
            user_dict['is_admin'] = True
        else:
            user_dict['is_admin'] = False
        
        
        user_dict['token'] = token
        
        user_plan = PlanoContratado.get_plano_ativo_usuario(user.id)
        
        if user_plan is not None:
            user_dict['plano_contratado'] = user_plan.to_dict()
        else:
            user_dict['plano_contratado'] = None
        
        return user_dict

    except InvalidPasswordException:
        raise InvalidPasswordException("Senha inválida")
    
    except UserNotFoundException:
        raise UserNotFoundException("Usuário não encontrado")
    
    except Exception as e:
        raise e


def update_user_profile(user_id: int, user_data: dict) -> dict:
    """
    Atualiza o perfil do usuário com os dados fornecidos
    
    Args:
        user_id (int): ID do usuário
        user_data (dict): Dados a serem atualizados
        
    Returns:
        dict: Dados do usuário atualizado
        
    Raises:
        UserNotFoundException: Se o usuário não for encontrado
        UserAlreadyExistsException: Se o email já estiver em uso por outro usuário
        InvalidPasswordException: Se a nova senha for inválida
        Exception: Se houver erro na atualização
    """
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException("Usuário não encontrado")
        
        # Campos permitidos para atualização (exceto email por questões de segurança)
        allowed_fields = ['nome_completo', 'telefone', 'empresa', 'cargo']
        
        # Filtra apenas os campos permitidos que foram enviados
        update_data = {}
        for field in allowed_fields:
            if field in user_data and user_data[field] is not None:
                update_data[field] = user_data[field]
        
        # Verifica se há dados para atualizar
        if not update_data:
            raise ValueError("Nenhum campo válido fornecido para atualização")
        
        # Atualiza o usuário
        updated_user = User.update_user(user_id, update_data)
        
        if not updated_user:
            raise Exception("Erro ao atualizar usuário")
        
        # Retorna os dados atualizados
        user_dict = updated_user.to_dict()
        
        # Adiciona informação se é admin
        user_dict['is_admin'] = User.is_user_admin(updated_user.id)
        
        # Adiciona plano contratado
        user_plan = PlanoContratado.get_plano_ativo_usuario(updated_user.id)
        if user_plan:
            user_dict['plano_contratado'] = user_plan.to_dict()
        else:
            user_dict['plano_contratado'] = None
        
        return user_dict
        
    except UserNotFoundException:
        raise UserNotFoundException("Usuário não encontrado")
    
    except ValueError as e:
        raise ValueError(str(e))
    
    except Exception as e:
        raise Exception(f"Erro ao atualizar perfil: {str(e)}")
