from src.database import MongoDBConnection
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.globalvars import RESPOSTAS_COLLECTION
from src.models.contatos_model import Contatos
from src.enums.questionTipe_enum import QuestionTypeEnum
from marshmallow import ValidationError
from src.models.pesquisa_model import Pesquisa


class Resposta:
    
    @property
    def id(self) -> ObjectId:
        return self._id
    
    @id.setter
    def id(self, value: ObjectId):
        self._id = value
        
    @property
    def data_resposta(self) -> datetime:
        return self._data_resposta
    
    @data_resposta.setter
    def data_resposta(self, value: datetime):
        self._data_resposta = value
        
    @property
    def pesquisa_id(self) -> ObjectId:
        return self._pesquisa_id
    
    @pesquisa_id.setter
    def pesquisa_id(self, value: ObjectId):
        self._pesquisa_id = value
        
        
    @property
    def nome(self) -> str:
        return self._nome
    
    @nome.setter
    def nome(self, value: str):
        self._nome = value
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str):
        self._email = value
        
    @property
    def respostas(self) -> List[Dict[str, Any]]:
        return self._respostas
    
    @respostas.setter
    def respostas(self, value: List[Dict[str, Any]]):
        self._respostas = value
    
    
    def __init__(self, pesquisa_id: str, respostas: List[Dict[str, Any]], nome: str, email: str):
        self.pesquisa_id = pesquisa_id
        self.respostas : List[Dict[str, Any]] = respostas
        self.nome : str = nome
        self.email : str = email
        self.data_resposta : datetime = datetime.utcnow()



    def to_dict(self) -> Dict[str, Any]:
        return {
            'pesquisa_id': self.pesquisa_id,
            'respostas': self.respostas,
            'nome': self.nome,
            'email': self.email,
            'data_resposta': self.data_resposta
        }
        
    def to_save(self) -> Dict[str, Any]:
        return {
            'pesquisa_id': ObjectId(self.pesquisa_id),
            'respostas': self.respostas,
            'nome': self.nome,
            'email': self.email,
            'data_resposta': self.data_resposta
        }
        
        
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Resposta':
        
        _id = data['_id']
        if isinstance(_id, str):
            _id = ObjectId(_id)
            
            
        resposta = Resposta(
            pesquisa_id=data.get('pesquisa_id'),
            respostas=data.get('respostas'),
            nome=data.get('nome'),
            email=data.get('email')
        )
        
        resposta.id = _id
        
        resposta.data_resposta = data.get('data_resposta')
        
        return resposta
    
    @staticmethod
    def get_collection():
        return MongoDBConnection.dataBase()[RESPOSTAS_COLLECTION]
    
    
    @staticmethod
    def validate_resposta(data: Dict[str, Any]) -> Dict[str, Any]:
        tipo = data.get('tipo_pergunta')
        resposta = data.get('resposta')

        if tipo == QuestionTypeEnum.MULTIPLE_CHOICE.value:
            if not isinstance(resposta, int):
                raise ValidationError("Para perguntas de múltipla escolha, a resposta deve ser um número inteiro")
        
        elif tipo == QuestionTypeEnum.NPS.value:
            if not isinstance(resposta, int) or resposta < 0 or resposta > 10:
                raise ValidationError("Para perguntas NPS, a resposta deve ser um número inteiro entre 0 e 10")
        
        elif tipo == QuestionTypeEnum.TEXT.value:
            if not isinstance(resposta, str):
                raise ValidationError("Para perguntas de texto, a resposta deve ser uma string")
        
        return data


    @staticmethod
    def create_multiplas_respostas(respostas_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            
            respostas = respostas_data.get('respostas')
            for resposta in respostas:
                Resposta.validate_resposta(resposta)

            resposta = Resposta(
                pesquisa_id=respostas_data.get('pesquisa_id'),
                respostas=respostas_data.get('respostas'),
                nome=respostas_data.get('nome'),
                email=respostas_data.get('email')
            )
            
            
            Resposta.get_collection().insert_one(resposta.to_save())

            return respostas

        except ValidationError as e:
            raise ValidationError(f"Erro ao validar respostas: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Erro ao criar respostas: {str(e)}")


    @staticmethod
    def check_if_email_already_answered(email: str, pesquisa_id: str) -> bool:
        try:
            resposta = Resposta.get_collection().find_one({'email': email, 'pesquisa_id': pesquisa_id})
            return resposta is not None
        except Exception as e:
            raise Exception(f"Erro ao verificar se o email já respondeu a pesquisa: {str(e)}")



    @staticmethod
    def get_nps_answers_by_list_of_pesquisa_ids_grouped_by_pesquisa_email(pesquisa_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        """
        Busca respostas NPS agrupadas por email e pesquisa_id

        Args:
            pesquisa_ids (List[ObjectId]): Lista de IDs das pesquisas

        Returns:
            List[Dict[str, Any]]: Lista de respostas NPS agrupadas por email e pesquisa_id
        """
        try:
            
            answers = Resposta.get_collection().aggregate([
                {
                    '$match': {
                        'pesquisa_id': {'$in': pesquisa_ids}
                    }
                },
                {
                    '$unwind': '$respostas'  
                },
                {
                    '$match': {
                        'respostas.tipo_pergunta': 'nps'  
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'email': '$email',
                            'pesquisa_id': '$pesquisa_id'
                        },
                        'respostas': {
                            '$push': {
                                'pergunta_id': '$respostas.pergunta_id',
                                'resposta': '$respostas.resposta',
                                'tipo_pergunta': '$respostas.tipo_pergunta'
                            }
                        },
                        'nome': {'$first': '$nome'},
                        'data_resposta': {'$first': '$data_resposta'}
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'email': '$_id.email',
                        'pesquisa_id': '$_id.pesquisa_id',
                        'nome': 1,
                        'data_resposta': 1,
                        'respostas': 1
                    }
                }
            ])
            
            nps_answers = list(answers)
            return nps_answers
            
        except Exception as e:
            print(f"Erro ao buscar respostas NPS: {str(e)}")
            return []


    @staticmethod
    def get_num_of_answers_by_list_of_pesquisa_ids(pesquisa_ids: List[ObjectId]) -> int:
        try:
            num_of_answers = Resposta.get_collection().count_documents({'pesquisa_id': {'$in': pesquisa_ids}})
            return num_of_answers
        except Exception as e:
            raise Exception(f"Erro ao buscar numero de respostas da pesquisa: {str(e)}")


    @staticmethod
    def get_answers_by_questions_ids(pesquisa: Pesquisa) -> List[Dict[str, Any]]:
        try:
            
            questions_ids = []
            pergunta_textos = {}
            for pergunta in pesquisa.perguntas:
                pergunta_id = pergunta.get("id")
                pergunta_texto = pergunta.get("texto")
                questions_ids.append(pergunta_id)
                pergunta_textos[pergunta_id] = pergunta_texto
            
            answers = Resposta.get_collection().aggregate([
                {
                    '$match': {
                        'pesquisa_id': pesquisa.id,
                        'respostas.pergunta_id': {'$in': questions_ids}
                    }
                },
                {
                    '$unwind': '$respostas'
                },
                {
                    '$match': {
                        'respostas.pergunta_id': {'$in': questions_ids}
                    }
                },
                {
                    '$group': {
                        '_id': '$respostas.pergunta_id',
                        'respostas': {
                            '$push': '$respostas.resposta'
                        }
                    }
                }
            ])
            
            
            resultado = []
            for answer in answers:
                pergunta_id = answer['_id']
                resultado.append({
                    'id': pergunta_id,
                    'texto': pergunta_textos.get(pergunta_id, ''),
                    'respostas': answer['respostas']
                })
            
            return resultado
        
        except Exception as e:
            print(f"Erro ao buscar respostas: {str(e)}")
            return []
