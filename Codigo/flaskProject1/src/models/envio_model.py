from src.database import MongoDBConnection
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.globalvars import ENVIOS_COLLECTION
from src.models.contatos_model import Contatos
from pymongo.operations import UpdateOne


class Envio_Pesquisa:
    """
    Modelo para a collection de envios no MongoDB
    
    Exemplo de documento:
    {
        "_id": ObjectId("..."),
        "pesquisa_id": ObjectId("..."),
        "enviado_para": joao.silva@empresa.com,
        "data_envio": ISODate("2024-05-01T14:30:00.000Z"),
        "concluido": true,
    }
    """
    
    @staticmethod
    def to_dict(pesquisa_id, enviado_para, data_envio, concluido):
        
        if isinstance(pesquisa_id, str):
            pesquisa_id_obj = ObjectId(pesquisa_id)
            
        return {
            "pesquisa_id": pesquisa_id_obj,
            "enviado_para": enviado_para,
            "data_envio": data_envio,
            "concluido": concluido
        }
    
    @staticmethod
    def get_collection():
        """Retorna a collection de envios"""
        return  MongoDBConnection.dataBase()[ENVIOS_COLLECTION]
    
    
    @staticmethod
    def create_multiplos_envios(contatos: List[Contatos], pesquisa_id: str) -> List[Dict[str, Any]]:
        """
        Cria múltiplos envios de pesquisa
        
        Args:
            contatos: Lista de contatos
            pesquisa_id: ID da pesquisa
            
        Returns:
            List[Dict]: Lista de envios criados
        """
        try:
            db = Envio_Pesquisa.get_collection()
            now = datetime.utcnow()
            
            envios = []
            for contato in contatos:
                contato_email = contato.email
                
                envio_data = Envio_Pesquisa.to_dict(pesquisa_id, contato_email, now, False)
                envios.append(envio_data)
            
            result = db.insert_many(envios)
            return str(result.inserted_ids)
            
        except Exception as e:
            print(f"Erro ao criar envio: {str(e)}")
            raise
    
    @staticmethod
    def get_by_id(envio_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um envio pelo ID
        
        Args:
            envio_id: ID do envio
            
        Returns:
            Optional[Dict]: Envio encontrado ou None
        """
        try:
            result = Envio_Pesquisa.get_collection().find_one({"_id": ObjectId(envio_id)})
            
            # Converte ObjectId para string na resposta
            if result:
                result['_id'] = str(result['_id'])
                if 'pesquisa_id' in result and isinstance(result['pesquisa_id'], ObjectId):
                    result['pesquisa_id'] = str(result['pesquisa_id'])
                if 'empresa_id' in result and isinstance(result['empresa_id'], ObjectId):
                    result['empresa_id'] = str(result['empresa_id'])
                    
            return result
            
        except Exception as e:
            print(f"Erro ao buscar envio: {str(e)}")
            raise
    
    @staticmethod
    def get_by_usuario_email(email: str) -> List[Dict[str, Any]]:
        """
        Busca envios pelo email do usuário
        
        Args:
            email: Email do usuário
            
        Returns:
            List[Dict]: Lista de envios
        """
        try:
            cursor = Envio_Pesquisa.get_collection().find({"enviado_para": email})
            
            # Converte ObjectId para string na resposta
            result = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'pesquisa_id' in doc and isinstance(doc['pesquisa_id'], ObjectId):
                    doc['pesquisa_id'] = str(doc['pesquisa_id'])
                if 'empresa_id' in doc and isinstance(doc['empresa_id'], ObjectId):
                    doc['empresa_id'] = str(doc['empresa_id'])
                result.append(doc)
                
            return result
            
        except Exception as e:
            print(f"Erro ao buscar envios por email: {str(e)}")
            raise
        
    @staticmethod
    def get_estatisticas_envios_by_pesquisa_ids(pesquisa_ids: List[ObjectId]) -> float:
        """
        Busca numero de envios por IDs de pesquisa
        
        Args:
            pesquisa_ids: Lista de IDs de pesquisa

        Returns:
            Envio_Pesquisa: Envios das pesquisas
        """
        
        try:
            db = Envio_Pesquisa.get_collection()
            result = list(db.find({"pesquisa_id": {"$in":pesquisa_ids}}))
            
            if result:
                num_concluidos = 0
                num_nao_concluidos = 0
                for doc in result:
                    if doc['concluido']:
                        num_concluidos += 1
                    else:
                        num_nao_concluidos += 1
                        
                if num_concluidos + num_nao_concluidos > 0:
                    taxa_conclusao = (num_concluidos / len(result)) * 100
                else:
                    taxa_conclusao = 0

                return taxa_conclusao
            return 0
        except Exception as e:
            print(f"Erro ao buscar numero de envios por IDs de pesquisa: {str(e)}")
            raise
        
        
        
    @staticmethod
    def get_by_pesquisa_id_and_email(pesquisa_id: str, email: str) -> List[Dict[str, Any]]:
        """
        Busca envios por pesquisa e email
        
        Args:
            pesquisa_id: ID da pesquisa
            email: Email do usuário
        
        Returns:
            List[Dict]: Lista de envios
        """
        try:
            cursor = Envio_Pesquisa.get_collection().find({"pesquisa_id": ObjectId(pesquisa_id), "enviado_para": email})
            
            result = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'pesquisa_id' in doc and isinstance(doc['pesquisa_id'], ObjectId):
                    doc['pesquisa_id'] = str(doc['pesquisa_id'])
                result.append(doc)
                
            return result
            
        except Exception as e:
            print(f"Erro ao buscar envios por pesquisa e email: {str(e)}")
            raise
    
    @staticmethod
    def get_by_pesquisa(pesquisa_id: str, concluido: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Busca envios por pesquisa
        
        Args:
            pesquisa_id: ID da pesquisa
            concluido: Filtrar por concluídos ou não (opcional)
            
        Returns:
            List[Dict]: Lista de envios
        """
        try:
            # Prepara filtros
            filters = {"pesquisa_id": ObjectId(pesquisa_id)}
            if concluido is not None:
                filters["concluido"] = concluido
                
            cursor = Envio_Pesquisa.get_collection().find(filters)
            
            # Converte ObjectId para string na resposta
            result = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'pesquisa_id' in doc and isinstance(doc['pesquisa_id'], ObjectId):
                    doc['pesquisa_id'] = str(doc['pesquisa_id'])
                if 'empresa_id' in doc and isinstance(doc['empresa_id'], ObjectId):
                    doc['empresa_id'] = str(doc['empresa_id'])
                result.append(doc)
                
            return result
            
        except Exception as e:
            print(f"Erro ao buscar envios por pesquisa: {str(e)}")
            raise
    
    @staticmethod
    def update_respostas(envios: List[Dict[str, Any]]) -> bool:
        """
        Atualiza as respostas de múltiplos envios
        
        Args:
            envios: Lista de dicionários com os dados dos envios contendo as respostas
            
        Returns:
            bool: True se pelo menos um envio foi atualizado com sucesso
        """
        try:
            print(f"Iniciando atualização de {len(envios)} envios")
            
            # Prepara as operações de atualização em lote
            operations = []
            
            for index, envio in enumerate(envios):
                try:
                    
                    
                    filter_query = {
                        "pesquisa_id": ObjectId(envio['pesquisa_id']),
                        "enviado_para": envio['enviado_para']
                    }
                    
                    update_data = {
                        "$set": {
                            "respostas": envio['respostas'],
                            "concluido": True,
                            "data_conclusao": datetime.utcnow()
                        }
                    }
                    
                    operations.append(UpdateOne(filter_query, update_data))
                    print(f"✓ Operação preparada com sucesso para envio {index + 1}")
                    
                except Exception as e:
                    print(f"Erro ao processar envio {index + 1}:")
                    print(f"- Erro: {str(e)}")
                    print(f"- Dados do envio: {envio}")
                    raise e
            
            if operations:
                print(f"Executando bulk_write com {len(operations)} operações")
                result = Envio_Pesquisa.get_collection().bulk_write(operations)
                print(f"Resultado do bulk_write:")
                print(f"- Modificados: {result.modified_count}")
                print(f"- Inseridos: {result.inserted_count}")
                print(f"- Atualizados: {result.upserted_count}")
                print(f"- Deletados: {result.deleted_count}")
                return result
            
            print("Nenhuma operação para executar")
            return False
            
        except Exception as e:
            print(f"Erro ao atualizar respostas em lote:")
            print(f"- Tipo do erro: {type(e).__name__}")
            print(f"- Mensagem: {str(e)}")
            print(f"- Dados recebidos: {envios}")
            raise e
    
    @staticmethod
    def delete(envio_id: str) -> bool:
        """
        Remove um envio do banco
        
        Args:
            envio_id: ID do envio
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            result = Envio.get_collection().delete_one({"_id": ObjectId(envio_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Erro ao remover envio: {str(e)}")
            raise
    
    @staticmethod
    def get_estatisticas_por_pesquisa(pesquisa_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de respostas por pesquisa
        
        Args:
            pesquisa_id: ID da pesquisa
            
        Returns:
            Dict: Estatísticas da pesquisa
        """
        try:
            # Converte para ObjectId
            pesquisa_id_obj = ObjectId(pesquisa_id)
            
            # Total de envios
            total_envios = Envio_Pesquisa.get_collection().count_documents({"pesquisa_id": pesquisa_id_obj})
            
            # Total de envios concluídos
            total_concluidos = Envio_Pesquisa.get_collection().count_documents({
                "pesquisa_id": pesquisa_id_obj,
                "concluido": True
            })
            
            # Taxa de conclusão
            taxa_conclusao = (total_concluidos / total_envios) * 100 if total_envios > 0 else 0
            
            # Agrupa respostas por pergunta (usando pipeline de agregação do MongoDB)
            pipeline = [
                {"$match": {"pesquisa_id": pesquisa_id_obj, "concluido": True}},
                {"$unwind": "$respostas"},
                {"$group": {
                    "_id": {
                        "pergunta_id": "$respostas.pergunta_id",
                        "pergunta": "$respostas.pergunta"
                    },
                    "respostas": {"$push": "$respostas.resposta"}
                }}
            ]
            
            resultado_agregacao = list(Envio_Pesquisa.get_collection().aggregate(pipeline))
            
            # Processa resultados da agregação
            perguntas_stats = []
            for item in resultado_agregacao:
                pergunta_id = item["_id"]["pergunta_id"]
                pergunta = item["_id"]["pergunta"]
                respostas = item["respostas"]
                
                # Conta frequência de cada resposta
                frequencia = {}
                for resposta in respostas:
                    if resposta in frequencia:
                        frequencia[resposta] += 1
                    else:
                        frequencia[resposta] = 1
                
                perguntas_stats.append({
                    "pergunta_id": pergunta_id,
                    "pergunta": pergunta,
                    "total_respostas": len(respostas),
                    "frequencia": frequencia
                })
            
            return {
                "pesquisa_id": str(pesquisa_id_obj),
                "total_envios": total_envios,
                "total_concluidos": total_concluidos,
                "taxa_conclusao": taxa_conclusao,
                "estatisticas_perguntas": perguntas_stats
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            raise 