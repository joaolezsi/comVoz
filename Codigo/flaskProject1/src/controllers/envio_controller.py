from src.models.envio_model import Envio
from src.models.pesquisa_model import Pesquisa
from typing import Dict, List, Any, Optional, Tuple
from bson.objectid import ObjectId

class EnvioController:
    """
    Controller para operações relacionadas a envios de pesquisas.
    Implementa a lógica de negócio separada das rotas/views.
    """
    
    @staticmethod
    def criar_envio(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Cria um novo envio de pesquisa
        
        Args:
            data: Dados do envio da pesquisa
            
        Returns:
            Tuple: (Dados do envio criado, status_code)
        """
        try:
            # Validações adicionais de negócio
            if not data.get('pesquisa_id'):
                return {"error": "ID da pesquisa é obrigatório"}, 400
                
            if not data.get('usuario') or not data.get('usuario').get('email'):
                return {"error": "Dados do usuário são obrigatórios"}, 400
                
            # Verifica se a pesquisa existe
            pesquisa = Pesquisa.get_by_id(data['pesquisa_id'])
            if not pesquisa:
                return {"error": "Pesquisa não encontrada"}, 404
                
            # Verifica se a pesquisa está ativa
            if not pesquisa.get('ativa', False):
                return {"error": "Esta pesquisa não está ativa"}, 400
                
            # Cria o envio
            envio_id = Envio.create(data)
            envio = Envio.get_by_id(envio_id)
            
            if not envio:
                return {"error": "Erro ao criar envio"}, 500
                
            return envio, 201
            
        except Exception as e:
            print(f"Erro ao criar envio: {str(e)}")
            return {"error": f"Erro ao criar envio: {str(e)}"}, 500
    
    @staticmethod
    def listar_envios(pesquisa_id: Optional[str] = None, 
                      email: Optional[str] = None, 
                      concluido: Optional[bool] = None) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lista envios com filtragem opcional
        
        Args:
            pesquisa_id: ID da pesquisa (opcional)
            email: Email do usuário (opcional)
            concluido: Filtrar por status de conclusão (opcional)
            
        Returns:
            Tuple: (Lista de envios, status_code)
        """
        try:
            if not pesquisa_id and not email:
                return {"error": "É necessário fornecer um filtro (pesquisa_id ou email)"}, 400
                
            if pesquisa_id:
                envios = Envio.get_by_pesquisa(pesquisa_id, concluido)
            else:
                envios = Envio.get_by_usuario_email(email)
                
                # Filtra por concluído no caso de busca por email (que não suporta esse filtro diretamente)
                if concluido is not None and envios:
                    envios = [e for e in envios if e.get('concluido') == concluido]
                    
            return envios, 200
            
        except Exception as e:
            print(f"Erro ao listar envios: {str(e)}")
            return {"error": f"Erro ao listar envios: {str(e)}"}, 500
    
    @staticmethod
    def obter_envio(envio_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Obtém um envio pelo ID
        
        Args:
            envio_id: ID do envio
            
        Returns:
            Tuple: (Dados do envio ou mensagem de erro, status_code)
        """
        try:
            envio = Envio.get_by_id(envio_id)
            
            if not envio:
                return {"error": "Envio não encontrado"}, 404
                
            return envio, 200
            
        except Exception as e:
            print(f"Erro ao obter envio: {str(e)}")
            return {"error": f"Erro ao obter envio: {str(e)}"}, 500
    
    @staticmethod
    def atualizar_respostas(envio_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Atualiza as respostas de um envio
        
        Args:
            envio_id: ID do envio
            data: Dados das respostas
            
        Returns:
            Tuple: (Dados do envio atualizado ou mensagem de erro, status_code)
        """
        try:
            # Verifica se o envio existe
            envio_existente = Envio.get_by_id(envio_id)
            
            if not envio_existente:
                return {"error": "Envio não encontrado"}, 404
                
            # Verifica se o envio já foi concluído
            if envio_existente.get('concluido'):
                return {"error": "Este envio já foi concluído e não pode ser alterado"}, 400
                
            # Validações adicionais
            if not data.get('respostas'):
                return {"error": "É necessário fornecer as respostas"}, 400
                
            # Pode adicionar mais validações aqui, como verificar se todas as 
            # perguntas obrigatórias foram respondidas, formatos corretos, etc.
            
            # Busca a pesquisa para validar respostas
            pesquisa = Pesquisa.get_by_id(envio_existente['pesquisa_id'])
            if pesquisa and 'perguntas' in pesquisa:
                # Validar se todas as perguntas necessárias foram respondidas
                perguntas_ids = set(range(len(pesquisa['perguntas'])))
                respostas_ids = set(r.get('pergunta_id') for r in data['respostas'] if 'pergunta_id' in r)
                
                # Se estiver marcando como concluído, todas as perguntas devem ter respostas
                if data.get('concluido', True) and not perguntas_ids.issubset(respostas_ids):
                    return {"error": "Todas as perguntas devem ser respondidas para concluir o envio"}, 400
            
            # Atualiza as respostas
            Envio.update_respostas(
                envio_id, 
                data['respostas'], 
                data.get('concluido', True)
            )
            
            # Retorna o envio atualizado
            envio_atualizado = Envio.get_by_id(envio_id)
            return envio_atualizado, 200
            
        except Exception as e:
            print(f"Erro ao atualizar respostas: {str(e)}")
            return {"error": f"Erro ao atualizar respostas: {str(e)}"}, 500
    
    @staticmethod
    def remover_envio(envio_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Remove um envio
        
        Args:
            envio_id: ID do envio
            
        Returns:
            Tuple: (Mensagem de sucesso ou erro, status_code)
        """
        try:
            # Verifica se o envio existe
            envio_existente = Envio.get_by_id(envio_id)
            
            if not envio_existente:
                return {"error": "Envio não encontrado"}, 404
            
            # Aqui poderia haver validações adicionais
            # Como verificar se o envio já foi processado para geração de relatórios, etc.
            
            # Remove o envio
            Envio.delete(envio_id)
            
            return {"message": "Envio removido com sucesso"}, 200
            
        except Exception as e:
            print(f"Erro ao remover envio: {str(e)}")
            return {"error": f"Erro ao remover envio: {str(e)}"}, 500
    
    @staticmethod
    def obter_estatisticas(pesquisa_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Obtém estatísticas de uma pesquisa
        
        Args:
            pesquisa_id: ID da pesquisa
            
        Returns:
            Tuple: (Dados estatísticos ou mensagem de erro, status_code)
        """
        try:
            # Verifica se a pesquisa existe
            pesquisa = Pesquisa.get_by_id(pesquisa_id)
            
            if not pesquisa:
                return {"error": "Pesquisa não encontrada"}, 404
                
            # Obtém as estatísticas
            estatisticas = Envio.get_estatisticas_por_pesquisa(pesquisa_id)
            
            # Poderia enriquecer as estatísticas com mais informações aqui
            # Como dados sobre a pesquisa, empresa, etc.
            
            return estatisticas, 200
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {"error": f"Erro ao obter estatísticas: {str(e)}"}, 500 