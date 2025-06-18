from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from src.middleware.mongoDB import MongoDB
from src.globalvars import MONGO_URI, MONGO_DB_DATABASE
import os


# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
MongoDBConnection = MongoDB(connectionString= MONGO_URI, dataBaseName= MONGO_DB_DATABASE)


def clear_tables():
    """Limpa todas as tabelas do banco de dados"""
    try:
        # Desativa as chaves estrangeiras temporariamente
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
        
        # Obtém todas as tabelas
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Limpa cada tabela
        for table in tables:
            db.session.execute(text(f'TRUNCATE TABLE {table}'))
        
        # Reativa as chaves estrangeiras
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        
        # Commit das alterações
        db.session.commit()
        
        print("Todas as tabelas foram limpas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao limpar tabelas: {str(e)}")
        db.session.rollback()
        raise

def init_db(app):
    """Inicializa todas as extensões do banco de dados"""
    
    # Inicialização das extensões
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Importação dos modelos (após inicialização do db)
    from src.models.user_model import User
    from src.models.plan_model import Plan
    from src.models.plano_contratado_model import PlanoContratado
    from src.models.questao_model import Questao
    from src.models.contatos_model import Contatos
    
    # Criação das tabelas
    with app.app_context():
        try:
            # Testa a conexão
            db.engine.connect()
            
            # Verifica tabelas existentes
            inspector = db.inspect(db.engine)
            
            # Cria as tabelas
            db.create_all()
            
            # Limpa as tabelas antes de inicializar os dados
            # clear_tables()
            
            # Inicializa os planos
            Plan.init_plans()
            
            # Inicializa as questões padrão
            Questao.init_questoes_padrao()

            # Cria usuários de teste
            User.create_test_users()
            
            # Inicializa a conexão com o MongoDB
            MongoDBConnection.connect()
            
            # Testa uma query simples para verificar a conexão
            db.session.execute(text("SELECT 1")).scalar()
            
        except Exception as e:
            raise Exception(f"Erro ao criar banco de dados: {str(e)}") 