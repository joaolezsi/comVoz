from typing import Dict, List, Any, Optional, Tuple
from bson.objectid import ObjectId
from src.utils.email_sender import EmailSender
from src.models.pesquisa_model import Pesquisa
from src.models.questao_model import Questao
from src.models.user_model import User
from src.models.plano_contratado_model import PlanoContratado
from src.schemas.pesquisa_schema import PesquisaSchema, PesquisaResponseSchema
from src.CustomExcepions import UserNotFoundError, LimitePesquisaException, QuestionNotFoundException, PesquisaNotFoundException, LimiteEnviosException, UserWithoutContatosException, EmailSenderException, UserWithoutPlanException, NpsQuestionsException
from src.globalvars import PESQUISAS_COLLECTION
from bson.objectid import ObjectId
from src.models.contatos_model import Contatos
from src.models.envio_model import Envio_Pesquisa
from src.enums.questionTipe_enum import QuestionTypeEnum
import random

def criar_nova_pesquisa(pesquisa_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria uma nova pesquisa
    
    Args:
        pesquisa_data: Dados da pesquisa
        
    Returns:
        Dict[str, Any]: Dados da pesquisa criada
    """
    try:
        
        user_id, titulo, descricao, perguntas = check_pesquisas_data(pesquisa_data)
        
        user = get_user_by_id(user_id)
        
        plano_contratado = PlanoContratado.get_plano_ativo_usuario(user_id)
        
        if plano_contratado is None:
            raise LimitePesquisaException("Usuário não possui um plano ativo")
            
        if plano_contratado.limite_pesquisas <= 0:
            raise LimitePesquisaException("Limite de pesquisas atingido")
        
        perguntas = get_perguntas_by_id(perguntas)
        
       
        nps_questions = [p for p in perguntas if p.tipo == QuestionTypeEnum.NPS.value]
        if len(nps_questions) < 5:
            raise NpsQuestionsException("A pesquisa deve conter pelo menos 5 perguntas do tipo NPS para gerar um dashboard adequado")
        
        pesquisa = Pesquisa(user_id, titulo, perguntas, descricao)
        
        nova_pesquisa = pesquisa.create()
        
        plano_contratado.decrementar_limite_pesquisas()
        
        nova_pesquisa_dict = nova_pesquisa.to_dict()
        
        return nova_pesquisa_dict
    
    except NpsQuestionsException as e:
        raise NpsQuestionsException(f"Erro ao verificar questões NPS: {str(e)}")
    
    except UserNotFoundError as e:
        raise UserNotFoundError(f"Erro ao obter usuário: {str(e)}")	
    
    except LimitePesquisaException as e:
        raise LimitePesquisaException(f"Erro ao verificar limite de pesquisas: {str(e)}")
    
    except Exception as e:
        raise e
 
def atualizar_pesquisa(pesquisa_id: str, questoes_list: List[int]) -> Dict[str, Any]:
    """
    Atualiza uma pesquisa existente
    
    Args:
        pesquisa_id: ID da pesquisa a ser atualizada
        questoes_data: Dados das questões a serem atualizadas
        
    Returns:
        Dict[str, Any]: Dados da pesquisa atualizada
    """
    try:
        pesquisa = Pesquisa.get_by_id(pesquisa_id)
        
        if not pesquisa:
            raise PesquisaNotFoundException("Pesquisa não encontrada")
        
        questoes = get_perguntas_by_id(questoes_list)
        
        pesquisa_atualizada = pesquisa.update(questoes)
        
        pesquisa_atualizada_dict = pesquisa_atualizada.to_dict()
        
        return pesquisa_atualizada_dict
    
    except QuestionNotFoundException as e:
        raise QuestionNotFoundException(f"Erro ao atualizar questões: questões não encontradas")
    
    except PesquisaNotFoundException as e:
        raise PesquisaNotFoundException(f"Erro ao atualizar pesquisa: pesquisa não encontrada")
    
    except Exception as e:
        raise e
 
    
     
def buscar_todas_pesquisas(user_id: int, ativa: bool) -> List[Pesquisa]:
    """
    Busca todas as pesquisas de um usuário
    
    Args:
        user_id: ID do usuário
        
    Returns:
        List[Pesquisa]: Lista de pesquisas encontradas
    """
    try:
        pesquisas = Pesquisa.get_all(user_id, ativa)
        
        formatted_pesquisas = []
        
        for pesquisa in pesquisas:
            pesquisa_dict = pesquisa.to_dict()
            formatted_pesquisas.append(pesquisa_dict)
            
        return formatted_pesquisas
    
    except Exception as e:
        raise e


def buscar_pesquisa_por_id(pesquisa_id: str) -> Pesquisa:
    """
    Busca uma pesquisa pelo ID
    
    Args:
        pesquisa_id: ID da pesquisa
        
    Returns:
        Pesquisa: Pesquisa encontrada
    """
    try:
        
        pesquisa = Pesquisa.get_by_id(pesquisa_id)
        
        formatted_pesquisa = pesquisa.to_dict()

        return formatted_pesquisa
    
    except PesquisaNotFoundException as e:
        raise PesquisaNotFoundException(f"Erro ao buscar pesquisa: pesquisa não encontrada")
    
    except Exception as e:
        raise e


def desativar_pesquisa(pesquisa_id: str) -> Pesquisa:
    """
    Desativa uma pesquisa pelo ID
    
    Args:
        pesquisa_id: ID da pesquisa
    """ 
    try:
        
        pesquisa = Pesquisa.get_by_id(pesquisa_id)
        
        pesquisa_modificada = pesquisa.desativar()
        
        return pesquisa_modificada
    
    except PesquisaNotFoundException as e:  
        raise PesquisaNotFoundException(f"Erro ao desativar pesquisa: pesquisa não encontrada")
    
    except Exception as e:
        raise e


def ativar_pesquisa(pesquisa_id: str) -> Pesquisa:
    """
    Ativa uma pesquisa pelo ID
    
    Args:
        pesquisa_id: ID da pesquisa
    """ 
    try:
        pesquisa = Pesquisa.get_by_id(pesquisa_id)
        pesquisa_modificada = pesquisa.ativar()
        return pesquisa_modificada
    
    except PesquisaNotFoundException as e:  
        raise PesquisaNotFoundException(f"Erro ao ativar pesquisa: pesquisa não encontrada")
    
    except Exception as e:
        raise e


def deletar_pesquisa(pesquisa_id: str) -> bool:
    """
    Deleta uma pesquisa pelo ID
    
    Args:
        pesquisa_id: ID da pesquisa
        
    Returns:
        bool: True se a pesquisa foi deletada com sucesso
    """
    try:
        pesquisa_to_delete = Pesquisa.get_by_id(pesquisa_id)
        
        deleted = pesquisa_to_delete.delete()
        
        if not deleted:
            raise PesquisaNotFoundException("Pesquisa não encontrada")
        
        return deleted
        
    except PesquisaNotFoundException as e:
        raise PesquisaNotFoundException(f"Erro ao deletar pesquisa: pesquisa não encontrada")
    
    except Exception as e:
        raise e


def get_perguntas_by_id(perguntas_id: List[int]) -> List['Questao']:
    """
    Obtém perguntas pelo ID
    
    Args:
        perguntas_id: IDs das perguntas
        
    Returns:
        List[Questao]: Lista de perguntas encontradas
    """
    try:
        
        perguntas = Questao.get_questoes_by_id(perguntas_id)
        
        if not perguntas:
            raise QuestionNotFoundException("Nenhuma questão encontrada")
    
        return perguntas
    
    except Exception as e:
        raise e


def get_user_by_id(user_id: int) -> User:
    """
    Obtém um usuário pelo ID
    
    Args:
        user_id: ID do usuário
        
    Returns:
        User: Usuário encontrado
    """
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError("Usuário não encontrado")
        
        return user
    
    except Exception as e:
        raise UserNotFoundError(f"Erro ao obter usuário: {str(e)}")
      


def check_pesquisas_data(pesquisa_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Verifica se os dados da pesquisa são válidos
    
    Args:
        pesquisa_data: Dados da pesquisa
        
    Returns:
        Tuple: (user_id, cnpj, titulo, descricao, perguntas)
    """
    try:
        user_id = pesquisa_data.get('user_id')
        titulo = pesquisa_data.get('titulo')
        descricao = pesquisa_data.get('descricao', None)
        perguntas = pesquisa_data.get('perguntas')
        
        
        if not user_id or not titulo or not perguntas:
            raise ValueError("Dados incompletos")
        
        return user_id, titulo, descricao, perguntas

    except Exception as e:
        raise ValueError(f"Erro ao validar dados da pesquisa: {str(e)}")





def enviar_pesquisa_controller(pesquisa_id: str, user_id: int):
    """
    Envia uma pesquisa para um usuário
    """
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError("Usuário não encontrado")
        
        pesquisa = Pesquisa.get_by_id(pesquisa_id)
        
        if not pesquisa:
            raise PesquisaNotFoundException("Pesquisa não encontrada")
        
        plano_user = PlanoContratado.get_plano_finalizado_ou_ativo_usuario(user_id)
        
        if not plano_user:
            raise UserWithoutPlanException("Usuário não possui um plano ativo")
        
        limite_de_envios = plano_user.limite_de_envios
        
        contatos = Contatos.get_all_contatos(user_id)   
        
        if not contatos:
            raise UserWithoutContatosException("Usuário não possui contatos")
        
        if limite_de_envios <= 0:
            raise LimiteEnviosException("Limite de envios atingido")
        
        if len(contatos) > limite_de_envios:
            selected_contatos = random.sample(contatos, limite_de_envios)
          
        else:
            selected_contatos = contatos
        
        plano_user.decrementar_limite_de_envios(len(selected_contatos))
        empresa = user.empresa
        
        email_sender = EmailSender()
        email_sender.send_pesquisa(selected_contatos, pesquisa, empresa)	
        
        envios = Envio_Pesquisa.create_multiplos_envios(selected_contatos, pesquisa_id)     
        
        return f"Pesquisa enviada para {len(selected_contatos)} contatos"
        

    except UserWithoutPlanException as e:
        raise UserWithoutPlanException(f"Erro ao enviar pesquisa: {str(e)}")
    
    except UserWithoutContatosException as e:
        raise UserWithoutContatosException(f"Erro ao enviar pesquisa: {str(e)}")
    
    except LimiteEnviosException as e:
        raise LimiteEnviosException(f"Erro ao enviar pesquisa: {str(e)}")
    
    except UserNotFoundError as e:
        raise UserNotFoundError(f"Erro ao obter usuário: {str(e)}")
    
    except PesquisaNotFoundException as e:
        raise PesquisaNotFoundException(f"Erro ao obter pesquisa: {str(e)}")
    
    except Exception as e:
        raise e

