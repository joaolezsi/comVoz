from src.models.questao_model import Questao
from typing import Dict, List, Any, Optional, Tuple
from src.models.user_model import User
from src.CustomExcepions import UserNotFoundException

def get_all_questions(user_id: int) -> List[Dict[str, Any]]:
    try:
        questoes = Questao.get_questoes(user_id)
        
        formatted_questoes = [questao.to_dict() for questao in questoes]
        return formatted_questoes
    except Exception as e:
        print(e)
        raise e



def create_questao(lista_de_questoes: List[Dict[str, Any]], user_id: int) -> List[Dict[str, Any]]:
    try: 
        
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException("Usuário não encontrado")
        
        questoes_criadas = Questao.create_questao(lista_de_questoes, user.id)
        
        formatted_questoes = [questao.to_dict() for questao in questoes_criadas]
        
        return formatted_questoes
    
    except UserNotFoundException as e:
        print(e)
        raise e
    
    except Exception as e:
        print(e)
        raise e


