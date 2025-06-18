from src.database import MongoDBConnection
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.globalvars import PESQUISAS_COLLECTION
from src.models.questao_model import Questao
from src.CustomExcepions import PesquisaNotFoundException
from pprint import pprint
class Pesquisa:
    """
    Modelo para a collection de pesquisas no MongoDB
    
    Exemplo de documento:
    {
        "_id": ObjectId("..."),
        "titulo": "Pesquisa de Satisfação 2024",
        "descricao": "Pesquisa anual de satisfação dos colaboradores",
        "perguntas": [
            {
                "pergunta": "Como você avalia o ambiente de trabalho?",
                "tipo": "escala",
                "opcoes": ["1", "2", "3", "4", "5"]
            },
            {
                "pergunta": "Você recomendaria a empresa para um amigo?",
                "tipo": "booleano",
                "opcoes": ["Sim", "Não"]
            },
            {
                "pergunta": "Deixe um comentário sobre o que poderia melhorar:",
                "tipo": "texto",
                "opcoes": []
            }
        ],
        "data_criacao": ISODate("2024-05-01T00:00:00.000Z"),
        "empresa_id": ObjectId("..."),
        "ativa": true
    }
    """
    
    @property
    def ativo(self) -> bool:
        return self._ativo
    
    @ativo.setter
    def ativo(self, value: bool):
        self._ativo = value
    
    @property
    def id(self) -> ObjectId:
        return self._id
    
    @id.setter
    def id(self, value: ObjectId):
        self._id = value
    
    @property
    def data_criacao(self) -> datetime:
        return self._data_criacao
    
    @data_criacao.setter
    def data_criacao(self, value: datetime):
        self._data_criacao = value
    
    def __init__(self, user_id: int, titulo: str, perguntas: List[Questao], descricao: str = None):
        self.user_id = user_id
        self.titulo = titulo
        self.perguntas = perguntas
        self.descricao = descricao
        self._ativo = True
        self._id = None
        self._data_criacao = None
 
     
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto para dicionário para resposta
        """
        return {
            "_id": str(self.id),
            "user_id": self.user_id,
            "titulo": self.titulo,
            "perguntas": self.perguntas,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "data_criacao": self._data_criacao
        }

    def to_save(self) -> Dict[str, Any]:
        """
        Converte o objeto para dicionário para salvar no banco
        """
        return {
            "user_id": self.user_id,
            "titulo": self.titulo,
            "perguntas": self.perguntas,
            "descricao": self.descricao,
            "ativo": self._ativo,
            "data_criacao": self._data_criacao
        }
    
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Pesquisa':
        """
        Converte um dicionário para um objeto Pesquisa
        
        Args:
            data: Dicionário com os dados da pesquisa
            
        Returns:
            Pesquisa: Objeto Pesquisa
        """
        _id = data['_id']
        if isinstance(_id, str):
            _id = ObjectId(_id)
            
        pesquisa = Pesquisa(
            user_id=data['user_id'],
            titulo=data['titulo'],
            perguntas=data['perguntas'],
            descricao=data['descricao'],
        )
        
        pesquisa.ativo = data['ativo']
        
        pesquisa.id = _id
        
        pesquisa.data_criacao = data['data_criacao']

        return pesquisa
        
    @staticmethod    
    def get_collection():
        """Retorna a collection de pesquisas"""
        return MongoDBConnection.dataBase()[PESQUISAS_COLLECTION]
    
    
    def create(self) -> 'Pesquisa':
        """
        Cria uma nova pesquisa
        
        Returns:
            Pesquisa: Pesquisa criada
        """
        try:
            database = Pesquisa.get_collection()
            
            formatted_perguntas = [pergunta.to_dict() for pergunta in self.perguntas]
            
            self.perguntas = formatted_perguntas
            
            pesquisa_data = self.to_save()
            
            pesquisa_data['data_criacao'] = datetime.now()
            
            result = database.insert_one(pesquisa_data)
            
            inserted_doc = database.find_one({"_id": result.inserted_id})
            
            if inserted_doc:
                pesquisa = Pesquisa.from_dict(inserted_doc)
                
            return pesquisa
            
        except Exception as e:
            print(f"Erro ao criar pesquisa: {str(e)}")
            raise
    
    @staticmethod
    def get_by_id(pesquisa_id: str) -> Optional['Pesquisa']:
        """
        Busca uma pesquisa pelo ID
        
        Args:
            pesquisa_id: ID da pesquisa
            
        Returns:
            Optional[Dict]: Pesquisa encontrada ou None
        """
        try:
            
            result = Pesquisa.get_collection().find_one({"_id": ObjectId(pesquisa_id)})
            
            if result:
                pesquisa_obj= Pesquisa.from_dict(result)
                    
                return pesquisa_obj
            
            else: 
                raise PesquisaNotFoundException("Pesquisa não encontrada")
            
        except PesquisaNotFoundException as e:
            raise PesquisaNotFoundException(f"Erro ao buscar pesquisa: pesquisa não encontrada")
        
        except Exception as e:
            raise e
    
    @staticmethod
    def get_all(user_id: int, ativa: bool = None) -> List['Pesquisa']:
        """
        Retorna todas as pesquisas, opcionalmente filtradas por empresa
        
        Args:
            user_id: ID do usuário
            ativa: Filtrar pesquisas ativas ou inativas (opcional)
            
        Returns:
            List[Pesquisa]: Lista de pesquisas
        """
        try:
            
            filters = {"user_id": int(user_id)}  
            if ativa is not None:
                filters['ativo'] = bool(ativa)  
                
            database = Pesquisa.get_collection()
            
            cursor = list(database.find(filters))
            
            result = []
            for doc in cursor:
                pesquisa = Pesquisa.from_dict(doc)
                result.append(pesquisa)
                
            return result
            
        except Exception as e:
            print(f"Erro ao listar pesquisas: {str(e)}")
            raise
    
    
    def update(self, questoes_list: List[Questao]) -> 'Pesquisa':
        """
        Atualiza uma pesquisa existente
        
        Args:
            pesquisa_id: ID da pesquisa
            pesquisa_data: Dados a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            
            formatted_questoes = [pergunta.to_dict() for pergunta in questoes_list]
                
            database = Pesquisa.get_collection()
            
            database.update_one(
                {"_id": self._id},
                {"$set": {"perguntas": formatted_questoes}}
            )
            
            updated_doc = database.find_one({"_id": self._id})
            
            if updated_doc:
                pesquisa = Pesquisa.from_dict(updated_doc)
            
                return pesquisa
            
            raise PesquisaNotFoundException("Pesquisa não encontrada")
        
        except PesquisaNotFoundException as e:
            raise PesquisaNotFoundException(f"Erro ao atualizar pesquisa: pesquisa não encontrada")
        
        except Exception as e:
            print(f"Erro ao atualizar pesquisa: {str(e)}")
            raise e
    
    
    def delete(self) -> bool:
        """
        Remove uma pesquisa do banco
        
        Args:
            pesquisa_id: ID da pesquisa
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            result = Pesquisa.get_collection().delete_one({"_id": self._id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Erro ao remover pesquisa: {str(e)}")
            raise
    
   
    def desativar(self) -> 'Pesquisa':
        """
        Desativa uma pesquisa (mais seguro que remover)
        
        Args:
            pesquisa_id: ID da pesquisa
            
        Returns:
            Dict[str, Any]: Documento da pesquisa desativada
        """
        try:
            result = Pesquisa.get_collection().update_one(
                {"_id": self._id},
                {"$set": {"ativo": False}}
            )
            
            if result.modified_count > 0:
                
                pesquisa_atualizada = Pesquisa.get_collection().find_one({"_id": self._id})
                if pesquisa_atualizada:
                    pesquisa = Pesquisa.from_dict(pesquisa_atualizada)
                    return pesquisa
            
            raise PesquisaNotFoundException("Pesquisa não encontrada")
        
        except PesquisaNotFoundException as e:
            raise PesquisaNotFoundException(f"Erro ao desativar pesquisa: pesquisa não encontrada")
        
        except Exception as e:
            print(f"Erro ao desativar pesquisa: {str(e)}")
            raise 
        
        
    @staticmethod
    def get_pesquisas_ativas_by_user_id(user_id: int) -> List['Pesquisa']:
        """
        Retorna todas as pesquisas ativas de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List[Pesquisa]: Lista de pesquisas ativas do usuário
        """
        try:
            database = Pesquisa.get_collection()
            cursor = list(database.find({"user_id": user_id, "ativo": True}))
            return [Pesquisa.from_dict(doc) for doc in cursor]
        except Exception as e:
            print(f"Erro ao buscar todas as pesquisas do usuário: {str(e)}")
            raise
        
    
    
    def get_all_pesquisas_by_user_id(user_id: int) -> List['Pesquisa']:
        """
        Retorna todas as pesquisas de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List[Pesquisa]: Lista de todas as pesquisas do usuários sendo ativas ou inativas
        """
        try:
            database = Pesquisa.get_collection()
            cursor = database.find({"user_id": user_id})
            return [Pesquisa.from_dict(doc) for doc in cursor]
        except Exception as e:
            print(f"Erro ao buscar todas as pesquisas do usuário: {str(e)}")

    

   

    @staticmethod
    def get_nps_by_user(user_id: int) -> Dict[str, Any]:
        """
        Obtém o NPS médio de todas as pesquisas de um usuário
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            Dict[str, Any]: Dicionário com informações do NPS médio
        """
        try:
            pesquisas = Pesquisa.query.filter_by(user_id=user_id).all()
            if not pesquisas:
                raise PesquisaNotFoundException("Nenhuma pesquisa encontrada para este usuário")
            
            nps_scores = []
            for pesquisa in pesquisas:
                nps_info = Pesquisa.get_nps_by_pesquisa(pesquisa.id)
                nps_scores.append(nps_info["nps_score"])
            
            nps_medio = sum(nps_scores) / len(nps_scores) if nps_scores else 0
            
            return {
                "user_id": user_id,
                "nps_medio": round(nps_medio, 2),
                "total_pesquisas": len(pesquisas),
                "nps_por_pesquisa": nps_scores
            }
            
        except Exception as e:
            print(f"Erro ao calcular NPS médio: {e}")
            raise e

    def ativar(self) -> 'Pesquisa':
        """
        Ativa uma pesquisa
        
        Args:
            pesquisa_id: ID da pesquisa
            
        Returns:
            Dict[str, Any]: Documento da pesquisa ativada
        """
        try:
            result = Pesquisa.get_collection().update_one(
                {"_id": self._id},
                {"$set": {"ativo": True}}
            )
            
            if result.modified_count > 0:
                pesquisa_atualizada = Pesquisa.get_collection().find_one({"_id": self._id})
                if pesquisa_atualizada:
                    pesquisa = Pesquisa.from_dict(pesquisa_atualizada)
                    return pesquisa
            
            raise PesquisaNotFoundException("Pesquisa não encontrada")
        
        except PesquisaNotFoundException as e:
            raise PesquisaNotFoundException(f"Erro ao ativar pesquisa: pesquisa não encontrada")
        
        except Exception as e:
            print(f"Erro ao ativar pesquisa: {str(e)}")
            raise 