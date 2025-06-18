from datetime import datetime
from src.database import db
from typing import Optional, Dict, Any



class OpcoesQuestao(db.Model):
    __tablename__ = 'question_options'
    
    id = db.Column(db.Integer, primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    texto = db.Column(db.String(255), nullable=False)

    
    questao = db.relationship('Questao', backref='opcoes')
    
    def __repr__(self):
        return f"<OpcoesQuestao(id={self.id}, texto='{self.texto}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'texto': self.texto,
            'questao_id': self.questao_id,
        }




