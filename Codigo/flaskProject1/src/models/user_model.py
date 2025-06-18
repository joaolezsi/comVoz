from src.database import db, bcrypt, jwt
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import re
from typing import Optional, List, Dict, Any
from src.CustomExcepions import InvalidPasswordException, PlanNotFoundException, UserAlreadyHasPlanException
from src.models.plan_model import Plan
from src.models.plano_contratado_model import PlanoContratado
from src.enums.plan_enum import PlanEnum
from src.models.user_admin_model import UserAdmin
from src.enums.plan_enum import PlanStatusEnum

class User(db.Model):
    """
    Modelo de usuário para o sistema
    
    Attributes:
        id (int): Identificador único do usuário
        nome_completo (str): Nome completo do usuário
        email (str): Email do usuário (único)
        telefone (str): Telefone do usuário
        empresa (str): Nome da empresa
        cargo (str): Cargo do usuário
        cnpj (str): CNPJ da empresa
        password_hash (str): Hash da senha do usuário
        created_at (datetime): Data de criação do usuário
        updated_at (datetime): Data da última atualização
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    empresa = db.Column(db.String(150), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    interests = db.relationship('PlanPurchaseInterest', back_populates='user', lazy=True)
    planos_contratados = db.relationship('PlanoContratado', backref='user', lazy=True)
    admin_info = db.relationship('UserAdmin', back_populates='user', uselist=False, lazy=True)
    
    
    def create_test_users():
        try:
            # Cria usuário admin
            admin_data = {
                'nome_completo': 'Pedro Maximo',
                'email': 'pedromaximocc@gmail.com',
                'telefone': '11999999999',
                'empresa': 'ComVoz',
                'cargo': 'Administrador',
                'cnpj': '00000000000000',
                'password': 'Admin@123'
            }
            
            # Verifica se o admin já existe
            existing_admin = User.get_by_email(admin_data['email'])
            if not existing_admin:
                admin = User.create_admin_user(admin_data)
                print(f"Usuário admin criado com sucesso! ID: {admin.id}")
            else:
                print(f"Usuário admin já existe! ID: {existing_admin.id}")
            
            # Cria usuário de teste
            test_user_data = {
                'nome_completo': 'Usuário Teste',
                'email': 'teste@comvoz.com',
                'telefone': '11988888888',
                'empresa': 'Empresa Teste',
                'cargo': 'Analista',
                'cnpj': '11111111111111',
                'password': 'Teste@123'
            }
            
            # Verifica se o usuário de teste já existe
            existing_test_user = User.get_by_email(test_user_data['email'])
            if not existing_test_user:
                # Cria o usuário sem plano inicial
                test_user = User(
                    nome_completo=test_user_data['nome_completo'],
                    email=test_user_data['email'],
                    telefone=test_user_data['telefone'],
                    empresa=test_user_data['empresa'],
                    cargo=test_user_data['cargo'],
                    cnpj=test_user_data['cnpj']
                )
                test_user.set_password(test_user_data['password'])
                
                db.session.add(test_user)
                db.session.flush()
                
                # Busca o plano Enterprise
                enterprise_plan = Plan.query.filter_by(nome='Enterprise').first()
                if not enterprise_plan:
                    raise PlanNotFoundException("Plano Enterprise não encontrado")
                
                # Contrata o plano Enterprise para o usuário
                plano_contratado = PlanoContratado(
                    user_id=test_user.id,
                    plan_id=enterprise_plan.id,
                    limite_pesquisas=enterprise_plan.limite_pesquisas,
                    limite_de_envios=enterprise_plan.limite_de_envios,
                    status=PlanStatusEnum.ATIVO.value
                )
                
                db.session.add(plano_contratado)
                db.session.commit()
                
            else:
                pass  # Usuário de teste já existe
                
        except Exception as e:
            db.session.rollback()
            raise e

    def set_password(self, password: str) -> None:
        """
        Define a senha do usuário com hash
        
        Args:
            password (str): Senha em texto plano
            
        Raises:
            ValueError: Se a senha for muito curta
        """
        try:
            if len(password) < 8:
                raise InvalidPasswordException("A senha deve ter pelo menos 8 caracteres")
            self.password_hash = generate_password_hash(password).decode('utf-8')
            
        except InvalidPasswordException as e:
            raise InvalidPasswordException("A senha deve ter pelo menos 8 caracteres")
        
        except Exception as e:
            raise e

    def check_password(self, password: str) -> bool:
        """
        Verifica se a senha fornecida corresponde à senha do usuário
        
        Args:
            password (str): Senha a ser verificada
            
        Returns:
            bool: True se a senha estiver correta, False caso contrário
        """
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            raise e

    def generate_jwt(self):
        """
        Gera um token JWT para o usuário, incluindo se ele é admin
        """
        # Verificar se o usuário é admin através da tabela UserAdmin
        is_admin = User.is_user_admin(self.id)
        
        additional_claims = {
            'is_admin': bool(is_admin),
            'email': self.email,
            'nome': self.nome_completo
        }
        return create_access_token(identity=str(self.id), additional_claims=additional_claims)

    def to_dict(self):
        """
        Converte o objeto usuário para um dicionário
        
        Returns:
            dict: Dicionário com os dados do usuário (exceto senha)
        """
        try:
            return {
                'id': self.id,
                'nome_completo': self.nome_completo,
                'email': self.email,
                'telefone': self.telefone,
                'empresa': self.empresa,
                'cargo': self.cargo,
                'cnpj': self.cnpj
            }
        except Exception as e:
            raise e

    def __repr__(self):
        """Representação string do objeto usuário"""
        try:
            return f'<User {self.email}>'
        except Exception as e:
            raise e

    @staticmethod
    def create_user(data: Dict[str, Any]) -> 'User':
        """
        Cria um novo usuário no sistema com o plano FREE
        
        Args:
            data (dict): Dicionário com os dados do usuário
                {
                    'nome_completo': str,
                    'email': str,
                    'telefone': str,
                    'empresa': str,
                    'cargo': str,
                    'cnpj': str,
                    'password': str
                }
                
        Returns:
            User: Usuário criado
            
        Raises:
            ValueError: Se os dados forem inválidos
            PlanNotFoundException: Se o plano FREE não for encontrado
            UserAlreadyHasPlanException: Se o usuário já tiver um plano ativo
            Exception: Se houver erro ao criar o usuário
        """
        try:
            # Busca o plano FREE
            free_plan = Plan.query.filter_by(nome='Free').first()
            if not free_plan:
                raise PlanNotFoundException("Plano FREE não encontrado")
            
            # Cria o usuário
            user = User(
                nome_completo=data['nome_completo'],
                email=data['email'],
                telefone=data['telefone'],
                empresa=data['empresa'],
                cargo=data['cargo'],
                cnpj=data['cnpj']
            )
            
            # Define a senha
            user.set_password(data['password'])
            
            # Adiciona o usuário ao banco
            db.session.add(user)
            db.session.commit()
            
            # Contrata o plano FREE para o usuário
            PlanoContratado.setar_plano_gratuito(user.id)
            
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao criar usuário: {str(e)}")

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """
        Busca um usuário pelo ID
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        try:
            return User.query.get(user_id)
        except Exception as e:
            raise e

    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """
        Busca um usuário pelo email
        
        Args:
            email (str): Email do usuário
            
        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            raise e

    @staticmethod
    def get_all() -> List['User']:
        """
        Retorna todos os usuários cadastrados
        
        Returns:
            List[User]: Lista de usuários
        """
        try:
            return User.query.all()
        except Exception as e:
            raise e

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> Optional['User']:
        """
        Atualiza os dados de um usuário
        
        Args:
            user_id (int): ID do usuário
            data (dict): Dados a serem atualizados
            
        Returns:
            Optional[User]: Usuário atualizado ou None
            
        Raises:
            Exception: Se houver erro ao atualizar o usuário
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return None
                
            # Atualiza os campos fornecidos
            for key, value in data.items():
                if hasattr(user, key) and key != 'password':
                    setattr(user, key, value)
                    
            # Se uma nova senha foi fornecida
            if 'password' in data:
                user.set_password(data['password'])
                
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao atualizar usuário: {str(e)}")

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Remove um usuário do sistema
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            bool: True se o usuário foi removido, False caso contrário
            
        Raises:
            Exception: Se houver erro ao remover o usuário
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return False
                
            db.session.delete(user)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao remover usuário: {str(e)}")


    @staticmethod
    def create_admin_user(data: Dict[str, Any]) -> 'User':
        """
        Cria um novo usuário administrador no sistema
        
        Args:
            data (dict): Dicionário com os dados do usuário administrador
                
        Returns:
            User: Usuário administrador criado
            
        Raises:
            Exception: Se houver erro ao criar o usuário administrador
        """
        try:
            user = User(
                nome_completo=data['nome_completo'],
                email=data['email'],
                telefone=data['telefone'],
                empresa=data['empresa'],
                cargo=data['cargo'],
                cnpj=data['cnpj']
            )
            
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.flush()  
            
            # Busca o plano Enterprise
            enterprise_plan = Plan.query.filter_by(nome='Enterprise').first()
            if not enterprise_plan:
                raise PlanNotFoundException("Plano Enterprise não encontrado")
            
            # Contrata o plano Enterprise para o admin
            plano_contratado = PlanoContratado(
                user_id=user.id,
                plan_id=enterprise_plan.id,
                limite_pesquisas=enterprise_plan.limite_pesquisas,
                limite_de_envios=enterprise_plan.limite_de_envios,
                status=PlanStatusEnum.ATIVO.value
            )
            
            db.session.add(plano_contratado)
           
            admin = UserAdmin(
                user_id=user.id,
                nivel_acesso='admin'
            )
            db.session.add(admin)
            
            db.session.commit()
            
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao criar usuário administrador: {str(e)}")

    @staticmethod
    def create_default_admin():
        """
        Cria um usuário administrador padrão se não existir nenhum
        """
        try:
            # Verifica se já existe algum administrador
            admin_exists = UserAdmin.query.first()
            if not admin_exists:
                default_admin = {
                    'nome_completo': 'Administrador Padrão',
                    'email': 'admin@comvoz.com',
                    'telefone': '11999999999',
                    'empresa': 'ComVoz',
                    'cargo': 'Administrador',
                    'cnpj': '00000000000000',
                    'password': 'Admin@123'
                }
                User.create_admin_user(default_admin)
        except Exception as e:
            raise Exception(f"Erro ao criar administrador padrão: {str(e)}")

    @staticmethod
    def is_user_admin(user_id: int) -> bool:
        """
        Verifica se um usuário é administrador
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            bool: True se o usuário é administrador, False caso contrário
        """
        try:
            admin = UserAdmin.query.filter_by(user_id=user_id).first()
            return admin is not None
        except Exception as e:
            raise e


