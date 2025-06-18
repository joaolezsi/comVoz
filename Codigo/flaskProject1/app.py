from flask import Flask, request
from datetime import timedelta
from src.views.user_view import user_blueprint
from src.views.plans_view import plans_blueprint
from src.views.questao_view import questao_blueprint
from src.views.pesquisa_view import pesquisa_blueprint
from src.views.contatos_view import contatos_blueprint
from src.views.respostas_view import responder_blueprint
from src.views.dashboard_view import dashboard_blueprint
from src.database import init_db
from src.globalvars import SQLALCHEMY_DATABASE_URI, JWT_SECRET_KEY, SECRET_KEY
import os
from flask_cors import CORS
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    # CORS mais simples e permissivo
    CORS(app, origins='*', supports_credentials=True)

    # Middleware simples para CORS
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    if SQLALCHEMY_DATABASE_URI is not None:
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    else:
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(basedir, 'comvoz.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Configuração da chave secreta e JWT diretamente no código
    # (não depende mais do arquivo .env)
    app.config['SECRET_KEY'] = 'chave-secreta-padrao-desenvolvimento'
    app.config['JWT_SECRET_KEY'] = 'chave-jwt-padrao-desenvolvimento'
    
    # Configurações adicionais do JWT
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'msg'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # Token expira em 24 horas
        
   
    
    # Inicializa o banco de dados relacional e suas extensões
    init_db(app)
    
    # Registrar blueprints
    app.register_blueprint(user_blueprint)
    app.register_blueprint(plans_blueprint)
    app.register_blueprint(pesquisa_blueprint)
    app.register_blueprint(questao_blueprint)
    app.register_blueprint(contatos_blueprint)
    app.register_blueprint(responder_blueprint)
    app.register_blueprint(dashboard_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    # Railway usa a variável de ambiente PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(
        debug=False,  # Desabilitando debug em produção
        host='0.0.0.0',
        port=port
    )
