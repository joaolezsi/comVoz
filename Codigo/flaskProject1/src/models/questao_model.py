from datetime import datetime
from src.database import db
from typing import Optional, Dict, Any, List
from src.CustomExcepions import QuestionNotFoundException
from src.enums.questionTipe_enum import QuestionTypeEnum
from src.models.opcoes_questao_model import OpcoesQuestao
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

class Questao(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    
    usuario = db.relationship('User', backref='questoes')
    
    
    def __repr__(self):
        return f"<Questao(id={self.id}, texto='{self.texto}', tipo='{self.tipo}')>"
    
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            if self.tipo == QuestionTypeEnum.MULTIPLE_CHOICE.value:
                opcoes = []
                for op in self.opcoes:
                    opcoes.append({"id": op.id, "texto": op.texto})
                
            else:
                opcoes = None
        
            return {
                "id": self.id,
                "texto": self.texto,
                "tipo": self.tipo,
                "user_id": self.user_id if self.user_id else None,
                "opcoes": opcoes
                }
        
        except Exception as e:
            print(e)
            raise e
    
    
    @staticmethod
    def get_questoes(user_id: int = None) -> List['Questao']:
        """
        Busca todas as questões padrão e opcionalmente as questões de um usuário específico
        
        Args:
            user_id (Optional[int]): ID do usuário para buscar suas questões específicas
            
        Returns:
            List[Questao]: Lista de questões encontradas
        """
        try:
            
            
            questions = Questao.query.options(
                    joinedload(Questao.opcoes)
                ).filter(
                    or_(
                        Questao.user_id == None,
                        Questao.user_id == user_id
                    )
                ).all()
            
            
            if not questions:
                raise QuestionNotFoundException("Nenhuma questão encontrada")   
            
            return questions
        
        except QuestionNotFoundException as e:
            print(e)
            raise QuestionNotFoundException
        
        except Exception as e:
            print(e)
            raise e
     
     
    @staticmethod
    def create_questao(lista_de_questoes: List[Dict[str, Any]], user_id: int) -> List['Questao']:
        try:
            questoes_criadas = []
            
            for questao in lista_de_questoes:
                tipo_questao = QuestionTypeEnum.from_int(questao['tipo'])
                
                questao_model = Questao(
                    texto=questao.get('texto'),
                    tipo=tipo_questao.value,
                    user_id=user_id if user_id else None
                )
                
                db.session.add(questao_model)
                db.session.flush()  
                
                opcoes = questao.get('opcoes', None)
                
                if tipo_questao == QuestionTypeEnum.MULTIPLE_CHOICE and opcoes is not None:
                    for opcao in opcoes:
                        opcao_model = OpcoesQuestao(
                            questao_id=questao_model.id,
                            texto=opcao['texto']
                        )
                        db.session.add(opcao_model)
                
                questoes_criadas.append(questao_model)
            
            db.session.commit()
            
            questoes_com_opcoes = Questao.query.options(
                joinedload(Questao.opcoes)
            ).filter(
                Questao.id.in_([q.id for q in questoes_criadas])
            ).all()
            
            return questoes_com_opcoes
            
        except Exception as e:
            db.session.rollback()
            print(e)
            raise e
    
    
    def get_questoes_usuario(user_id: int) -> List['Questao']:
        """
        Busca todas as questões do usuário
        """
        try:
            questions = Questao.query.options(joinedload(Questao.opcoes).filter(Questao.user_id == user_id)).all()

            if not questions:
                raise QuestionNotFoundException("Nenhuma questão encontrada")
            
            return questions
        
        except QuestionNotFoundException as e:
            print(e)
            raise QuestionNotFoundException
        
        except Exception as e:
            print(e)
            raise e
    
    def get_by_id(question_id: int) -> Optional['Questao']:
        """
        Busca uma questão pelo ID
        
        Args:
            question_id (int): ID da questão
            
        Returns:
            Questao: Questão encontrada ou None se não encontrada
        """
        try:
            question = Questao.query.get(question_id)
            
            if not question:
                raise QuestionNotFoundException("Questão não encontrada")
            
            return question
        
        except QuestionNotFoundException as e:
            print(e)
            raise QuestionNotFoundException
        
        except Exception as e:
            print(e)
            raise e
    
    @staticmethod
    def init_questoes_padrao():
        """Inicializa as questões padrão no banco de dados"""
        try:
            # Verifica se já existem questões padrão
            if Questao.query.filter_by(user_id=None).first():
                print("Questões padrão já inicializadas!")
                return
            
            questoes_padrao =[
                {
                    "texto": "Com que probabilidade você recomendaria nossa empresa a um amigo ou colega?",
                    "tipo": 2
                },
                {
                    "texto": "Nosso serviço atendeu às suas expectativas?",
                    "tipo": 1,
                    "opcoes": [
                        {"texto": "Sim, totalmente"},
                        {"texto": "Parcialmente"},
                        {"texto": "Não atendeu"}
                    ]
                },
                {
                    "texto": "O que mais te agradou em sua experiência com nossa empresa?",
                    "tipo": 3
                },
                {
                    "texto": "Você teve alguma dificuldade ao utilizar nossos serviços?",
                    "tipo": 1,
                    "opcoes": [
                        {"texto": "Sim"},
                        {"texto": "Não"}
                    ]
                },
                {
                    "texto": "Como você avalia a qualidade do atendimento que recebeu?",
                    "tipo": 1,
                    "opcoes": [
                        {"texto": "Excelente"},
                        {"texto": "Bom"},
                        {"texto": "Regular"},
                        {"texto": "Ruim"}
                    ]
                },
                {
                    "texto": "Você teve algum problema não resolvido durante sua experiência conosco?",
                    "tipo": 1,
                    "opcoes": [
                        {"texto": "Sim, mais de um"},
                        {"texto": "Sim, um"},
                        {"texto": "Não"}
                    ]
                },
                {
                    "texto": "Como você avaliaria a rapidez no atendimento às suas solicitações?",
                    "tipo": 2
                },
                {
                    "texto": "Descreva de forma geral como foi sua experiência com nossa empresa:",
                    "tipo": 3
                },
                {
                    "texto": "Você considera nossa empresa confiável?",
                    "tipo": 1,
                    "opcoes": [
                        {"texto": "Sim, totalmente"},
                        {"texto": "Parcialmente"},
                        {"texto": "Não"}
                    ]
                },
                {
                    "texto": "O que poderíamos melhorar para oferecer uma experiência ainda melhor?",
                    "tipo": 3
                },
                {
                    "texto": "Como você avalia a facilidade de uso dos nossos serviços?",
                    "tipo": 2
                },
                {
                    "texto": "Qual a probabilidade de você continuar utilizando nossos serviços?",
                    "tipo": 2
                },
                {
                    "texto": "Como você avalia a qualidade dos nossos produtos/serviços?",
                    "tipo": 2
                },
                {
                    "texto": "Qual a probabilidade de você indicar nossos produtos/serviços para sua rede de contatos?",
                    "tipo": 2
                },
                {
                    "texto": "Como você avalia o valor agregado que nossos serviços trazem para seu negócio?",
                    "tipo": 2
                }
            ]

            
            Questao.create_questao(questoes_padrao, None)
            print("Questões padrão inicializadas com sucesso!")
            
        except Exception as e:
            print(f"Erro ao inicializar questões padrão: {str(e)}")
            raise e
    
    
    @staticmethod
    def get_questoes_by_id(question_ids: List[int]) -> List['Questao']:
        """
        Obtém questões pelo ID
        """
        try:
            questions = Questao.query.filter(Questao.id.in_(question_ids)).all()
            
            if not questions:
                return []
            
            return questions
        
        except Exception as e:
            print(e)
            raise e
