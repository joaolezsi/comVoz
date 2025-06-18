from src.database import db
from datetime import datetime


class UserAdmin(db.Model):
    """
    Modelo para usuários administradores
    
    Attributes:
        id (int): Identificador único do registro de administrador
        user_id (int): ID do usuário que é administrador
        nivel_acesso (str): Nível de acesso do administrador
        data_nomeacao (datetime): Data em que o usuário foi nomeado administrador
    """
    __tablename__ = 'user_admin'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    nivel_acesso = db.Column(db.String(50), nullable=False, default='admin')
    data_nomeacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Usando string reference para evitar importação circular
    user = db.relationship('User', back_populates='admin_info', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<UserAdmin {self.user_id}>'
    
    @staticmethod
    def get_all_admins():
        admins = UserAdmin.query.all()
        if not admins:
            return []
        return [admin.user for admin in admins]
    
