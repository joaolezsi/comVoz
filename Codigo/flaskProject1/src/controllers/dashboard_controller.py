from src.models.pesquisa_model import Pesquisa 
from src.models.envio_model import Envio_Pesquisa
from src.models.respostas_model import Resposta
from typing import List, Dict, Any
from src.CustomExcepions import PesquisaNotFoundException
import numpy as np
from pprint import pprint
from bson import ObjectId



def get_dashboard_principal_data(user_id: int):
    try:
        
        response = {
            "pesquisas_ativas": 0,
            "respostas_recebidas": 0,
            "taxa_resposta": 0,
            "score": 0,
        }
        
        print(f"user_id: {user_id}")
        pesquisas_ativas = Pesquisa.get_pesquisas_ativas_by_user_id(user_id)
        
        pesquisas_ids = [pesquisa.id for pesquisa in pesquisas_ativas]
        
        taxa_resposta = Envio_Pesquisa.get_estatisticas_envios_by_pesquisa_ids(pesquisas_ids)
        
        num_of_answers = Resposta.get_num_of_answers_by_list_of_pesquisa_ids(pesquisas_ids)
        
        nps_answers_grouped_by_pesquisa_email = Resposta.get_nps_answers_by_list_of_pesquisa_ids_grouped_by_pesquisa_email(pesquisas_ids)
        
        if len(nps_answers_grouped_by_pesquisa_email) == 0:
            score = "Respostas NPS insuficientes para calcular o score"
        else:
            score = calculate_overall_nps_score(nps_answers_grouped_by_pesquisa_email)
            
        response["pesquisas_ativas"] = len(pesquisas_ativas)
        response["respostas_recebidas"] = num_of_answers
        response["taxa_resposta"] = taxa_resposta
        response["score"] = score
        
        return response
        
    except Exception as e:
        print(f"Erro ao buscar dados do dashboard: {e}")
        raise e
        
        
        
def calculate_overall_nps_score(respostas: List[Dict[str, Any]]) -> float:
    """
    Calcula o NPS score geral de uma pesquisa ou mais pesquisas baseado em todas as respostas nps.
    O NPS é calculado por pessoa/pesquisa, fazendo a média das respostas de cada pessoa antes de classificar
    como promotor ou detrator.
        
    Args:
        respostas (List[Dict[str, Any]]): Lista de dicionários contendo as respostas NPS
            Cada dicionário deve ter a estrutura: {'resposta': int, 'tipo_pergunta': str, '_id': ObjectId, ...}
            
    Returns:
        float: Score NPS geral (-100 a 100)
    """
    if not respostas:
        return 0.0
    
    total_relevante = 0  
    promotores = 0
    detratores = 0
            

    for doc in respostas:
        resposta = doc.get('respostas', [])
        if len(resposta) == 0:
            continue
        
        sum_respostas = sum(r.get('resposta', 0) for r in resposta)
        media_respostas = sum_respostas / len(resposta)
            
        if media_respostas >= 9:
            promotores += 1
            total_relevante += 1
        elif media_respostas <= 6:
            detratores += 1 
            total_relevante += 1
        
    if total_relevante == 0:
        return 0.0
    
    
    percentual_promotores = (promotores / total_relevante) * 100
    percentual_detratores = (detratores / total_relevante) * 100
        
    nps_score = percentual_promotores - percentual_detratores
    return round(nps_score, 2)



def get_nps_by_pesquisa(pesquisa: Pesquisa, respostas: List[int]) -> Dict[str, Any]:
    """
    Obtém o NPS de uma pesquisa específica
        
    Args:
        pesquisa_id (int): ID da pesquisa
            
    Returns:
        Dict[str, Any]: Dicionário com informações do NPS
    """
    try:
                
        nps_score = calculate_overall_nps_score(respostas)
            
        return {
                "pesquisa_id": str(pesquisa.id),
                "nps_score": nps_score,
                "total_respostas": len(respostas),
                "promotores": sum(1 for r in respostas if r >= 9),
                "neutros": sum(1 for r in respostas if 7 <= r <= 8),
                "detratores": sum(1 for r in respostas if r <= 6)
        }
            
    except Exception as e:
        print(f"Erro ao calcular NPS: {e}")
        raise e
    
    
def calcular_nps_por_pergunta(respostas: List[int]) -> Dict[str, Any]:
    """
    Calcula o NPS por pergunta
    """
    try: 
        promotores = 0
        detratores = 0
        neutros = 0
        total_respostas = 0
        
        for score in respostas:
            if score >= 9:
                promotores += 1
            elif score <= 6:
                detratores += 1
            else:
                neutros += 1
            total_respostas += 1
            
            
        percentual_promotores = (promotores / total_respostas) * 100
        percentual_detratores = (detratores / total_respostas) * 100
        nps_score = percentual_promotores - percentual_detratores
        
        return {
            "promotores": promotores,
            "detratores": detratores,
            "neutros": neutros,
            "nps_score": nps_score
        }
        
    except Exception as e:
        print(f"Erro ao calcular NPS por pergunta: {e}")
        raise e
        

def get_dados_relatorio_pesquisa(pesquisa_id):
    try:
        
        
        pesquisa = Pesquisa.get_by_id(pesquisa_id)
        
        
        if not pesquisa:
            raise Exception("Pesquisa não encontrada ou não pertence ao usuário")
    
        nps_answers = Resposta.get_nps_answers_by_list_of_pesquisa_ids_grouped_by_pesquisa_email([pesquisa.id])
        
        nps_geral = calculate_overall_nps_score(nps_answers)
        
        resultados = {
            "titulo_pesquisa": pesquisa.titulo,
            "total_respostas": 0,
            "nps_geral": nps_geral,
            "perguntas": []
        }
        
        answers_by_question_ids = Resposta.get_answers_by_questions_ids(pesquisa)
        
        total_respostas = 0
        
        for answer in answers_by_question_ids:
            pergunta_id = answer['id']
            respostas = answer['respostas']
            total_respostas += len(respostas)
            statistics = calcular_nps_por_pergunta(respostas)
            
            resultados["perguntas"].append({
                "id": pergunta_id,
                "texto": answer['texto'],
                "nps": statistics,
                "total_respostas": len(respostas),
                "distribuicao": {
                    "1-6": statistics['detratores'],
                    "7-8": statistics['neutros'],
                    "9-10": statistics['promotores']
                }
            })
        
        resultados["total_respostas"] = total_respostas
        
        return resultados
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        raise e 
    
        
        
        

def get_estatisticas_pesquisa_frontend(pesquisa_id: str) -> Dict[str, Any]:
    """
    Adapta os dados do relatório para o formato esperado pelo frontend de estatísticas
    
    Args:
        pesquisa_id: ID da pesquisa
        
    Returns:
        Dict: Dados formatados para o frontend
    """
    try:
        # Usa a função existente do relatório
        dados_relatorio = get_dados_relatorio_pesquisa(pesquisa_id)
        

        pesquisa_id_obj = ObjectId(pesquisa_id)
        total_envios = Envio_Pesquisa.get_collection().count_documents({"pesquisa_id": pesquisa_id_obj})
        total_concluidos = Envio_Pesquisa.get_collection().count_documents({
            "pesquisa_id": pesquisa_id_obj,
            "concluido": True
        })
        
        taxa_conversao = (total_concluidos / total_envios) * 100 if total_envios > 0 else 0
        
        # Formata respostasPorAlternativa para o frontend
        respostas_por_alternativa = []
        for pergunta in dados_relatorio.get("perguntas", []):
            # Para perguntas NPS, cria alternativas baseadas na distribuição
            alternativas = []
            
            total_responses = pergunta["total_respostas"]
            distribuicao = pergunta["distribuicao"]
            
            if total_responses > 0:
                # Calcula porcentagens
                porcentagem_detratores = (distribuicao["1-6"] / total_responses) * 100
                porcentagem_neutros = (distribuicao["7-8"] / total_responses) * 100
                porcentagem_promotores = (distribuicao["9-10"] / total_responses) * 100
                
                alternativas = [
                    {
                        "texto": "Detratores (1-6)",
                        "porcentagem": round(porcentagem_detratores, 1)
                    },
                    {
                        "texto": "Neutros (7-8)", 
                        "porcentagem": round(porcentagem_neutros, 1)
                    },
                    {
                        "texto": "Promotores (9-10)",
                        "porcentagem": round(porcentagem_promotores, 1)
                    }
                ]
            
            respostas_por_alternativa.append({
                "id": pergunta["id"],
                "texto": pergunta["texto"],
                "total_respostas": pergunta["total_respostas"],
                "alternativas": alternativas
            })
        
        # Para distribuição de respostas, você pode implementar uma query temporal
        # Por agora, vou retornar uma estrutura básica
        distribuicao_respostas = get_distribuicao_temporal_respostas(pesquisa_id)
        
        return {
            "respostas": dados_relatorio["total_respostas"],
            "taxaConversao": round(taxa_conversao, 1),
            "respostasPorAlternativa": respostas_por_alternativa,
            "distribuicaoRespostas": distribuicao_respostas
        }
        
    except Exception as e:
        print(f"Erro ao obter estatísticas para frontend: {e}")
        raise e


def get_distribuicao_temporal_respostas(pesquisa_id: str) -> List[Dict[str, Any]]:
    """
    Obtém a distribuição temporal das respostas
    
    Args:
        pesquisa_id: ID da pesquisa
        
    Returns:
        List: Lista com distribuição por data
    """
    try:
        
        
        pesquisa_id_obj = ObjectId(pesquisa_id)
        
        # Pipeline de agregação para agrupar por data
        pipeline = [
            {"$match": {"pesquisa_id": pesquisa_id_obj, "concluido": True}},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$data_envio"
                    }
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        resultado = list(Envio_Pesquisa.get_collection().aggregate(pipeline))
        
        # Formata para o frontend
        distribuicao = []
        for item in resultado:
            distribuicao.append({
                "data": item["_id"],
                "valor": item["count"]
            })
        
        return distribuicao
        
    except Exception as e:
        print(f"Erro ao obter distribuição temporal: {e}")
        # Retorna lista vazia em caso de erro
        return []


