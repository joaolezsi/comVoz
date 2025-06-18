import os

try:
    import src.secret
except:
    pass

"""DATABASE"""
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

"""MONGO"""
MONGO_URI = 'mongodb+srv://desenvolvimento_tis4:tis4@cluster0.ouioq2s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
MONGO_DB_DATABASE = 'Tis4'
PESQUISAS_COLLECTION = 'Pesquisas'
ENVIOS_COLLECTION = 'Envio'
RESPOSTAS_COLLECTION = 'Respostas'

"""SMTP"""
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

"""JWT"""
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

"""SECRET KEY"""
SECRET_KEY = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}