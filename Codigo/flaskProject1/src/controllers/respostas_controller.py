from typing import List, Dict, Any
from src.models.respostas_model import Resposta
from src.models.envio_model import Envio_Pesquisa
from marshmallow import ValidationError
from src.CustomExcepions import EmailAlreadyAnsweredException


def create_respostas_data(respostas_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Cria múltiplas respostas para uma pesquisa
    
    Args:
        respostas_data: Dicionário com os dados das respostas
        
    Returns:
        List[Dict]: Lista de respostas criadas
    """
    try:
       
        
        user_email = respostas_data.get('email')
        pesquisa_id = respostas_data.get('pesquisa_id')
        
        already_answered = Resposta.check_if_email_already_answered(user_email, pesquisa_id)
        
        if already_answered:
            raise EmailAlreadyAnsweredException("Email já respondeu a pesquisa")
        
        respostas = Resposta.create_multiplas_respostas(respostas_data)
       
        
        
        envios = Envio_Pesquisa.get_by_pesquisa_id_and_email(pesquisa_id, user_email)
        
        
        if len(envios) > 0:
            
            for envio in envios:
                envio['respostas'] = respostas
                envio['concluido'] = True
            
            Envio_Pesquisa.update_respostas(envios)
        
        
        return respostas
    
    
    except EmailAlreadyAnsweredException as e:
        raise EmailAlreadyAnsweredException(f"Email já respondeu a pesquisa: {str(e)}")
    
    except ValidationError as e:
        print("\n=== ERRO DE VALIDAÇÃO ===")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        raise ValidationError(f"Erro ao criar respostas: {str(e)}")
    
    except Exception as e:
        print("\n=== ERRO NO PROCESSAMENTO ===")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"Dados recebidos: {respostas_data}")
        raise Exception(f"Erro ao criar respostas: {str(e)}")

