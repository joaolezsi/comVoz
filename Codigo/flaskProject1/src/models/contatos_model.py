from datetime import datetime
from src.database import db
from typing import Optional, Dict, Any, List
from src.CustomExcepions import UserNotFoundError


class Contatos(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    user = db.relationship('User', backref='contatos')
    
    def __repr__(self):
        return f"<Contatos(id={self.id}, nome='{self.nome}', email='{self.email}', telefone='{self.telefone}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
        }
    
    
    @staticmethod
    def create_multiple_contatos(contatos: List[Dict[str, Any]], user_id: int) -> List['Contatos']:
        try:
            contatos_list = []
            for contato in contatos:
                new_contato = Contatos()
                new_contato.nome = contato.get('nome', None)
                new_contato.email = contato.get('email', None)
                new_contato.telefone = contato.get('telefone', None)
                new_contato.user_id = user_id
                
                db.session.add(new_contato)
                contatos_list.append(new_contato)
                
            db.session.commit()
            
            return contatos_list
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_all_contatos(user_id: int) -> List['Contatos']:
        try:
            return Contatos.query.filter_by(user_id=user_id).all()
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_contato_by_id(contato_id: int) -> 'Contatos':
        try:
            return Contatos.query.get(contato_id)
        except Exception as e:
            db.session.rollback()
            raise e
    

    @staticmethod
    def update_contato(contato_id: int, contato: Dict[str, Any]) -> 'Contatos':
        try:
            contato_obj = Contatos.query.get(contato_id)
            if contato_obj:
                contato_obj.nome = contato.get('nome', contato_obj.nome)
                contato_obj.email = contato.get('email', contato_obj.email)
                contato_obj.telefone = contato.get('telefone', contato_obj.telefone)
                
                db.session.commit()
                return contato_obj
            else:
                raise UserNotFoundError(f"Contato com ID {contato_id} não encontrado")
            
        except UserNotFoundError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise e

