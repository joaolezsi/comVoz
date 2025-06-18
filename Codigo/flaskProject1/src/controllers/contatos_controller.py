from src.models.user_model import User
from src.CustomExcepions import UserNotFoundError
from src.models.contatos_model import Contatos
from typing import List, Dict, Any
from src.globalvars import ALLOWED_EXTENSIONS
import pandas as pd
from src.schemas.contatos_schema import ContatoExcelSchema
from src.models.contatos_model import Contatos
from src.CustomExcepions import InvalidDataException
import os

def buscar_contatos(user_id: int):
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError("Usuário não encontrado")
        
        contatos = Contatos.get_all_contatos(user_id)
        
        formatted_contatos = [contato.to_dict() for contato in contatos]
        
        return formatted_contatos
    
    except UserNotFoundError as e:
        raise UserNotFoundError("Usuário não encontrado")
    
    except Exception as e:
        raise e


def criar_contatos_excel(filename: str, user_id: int) -> list:
    """
    Cria contatos a partir de um arquivo Excel ou CSV
    
    Args:
        filename (str): Nome do arquivo Excel ou CSV
        user_id (int): ID do usuário
        
    Returns:
        list: Lista de contatos criados
        
    Raises:
        InvalidDataException: Se os dados do arquivo forem inválidos
    """
    try:
        file_extension = filename.rsplit('.', 1)[1].lower()
        print(f"Processando arquivo '{filename}' para user_id={user_id} (extensão: {file_extension})")

        if file_extension == 'csv':
            df = pd.read_csv(f"uploads/{filename}", sep=None, engine='python')
        else:
            df = pd.read_excel(f"uploads/{filename}")

        
        df.columns = [col.strip().lower() for col in df.columns]
        df = df.where(pd.notnull(df), None)
        if 'telefone' in df.columns:
            df['telefone'] = df['telefone'].astype(str)
            df['telefone'] = df['telefone'].replace({'None': None, 'nan': None})
        print(f"Colunas encontradas no arquivo: {list(df.columns)}")

        required_columns = ['email']
        if not all(col in df.columns for col in required_columns):
            print("Coluna 'email' não encontrada no arquivo.")
            raise InvalidDataException("O arquivo deve conter pelo menos a coluna 'email'")

        df = df.rename(columns={
            'nome': 'nome',
            'email': 'email',
            'telefone': 'telefone'
        })

        print(f"Primeiras linhas do arquivo:\n{df.head()}")

        schema = ContatoExcelSchema(many=True)
        contatos_validados = schema.load(df.to_dict('records'))
        print(f"Total de contatos validados: {len(contatos_validados)}")

        Contatos.create_multiple_contatos(contatos_validados, user_id)
        os.remove(f"uploads/{filename}")

        print(f"Contatos criados com sucesso para user_id={user_id}")
        return contatos_validados

    except Exception as e:
        print(f"Erro ao processar arquivo '{filename}' para user_id={user_id}: {str(e)}")
        raise InvalidDataException(f"Erro ao processar arquivo: {str(e)}")

def criar_contatos_by_list(contatos_list: List[Dict[str, Any]], user_id: int):
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError("Usuário não encontrado")

        contatos = Contatos.create_multiple_contatos(contatos_list, user.id)
        
        formatted_contatos = [contato.to_dict() for contato in contatos]
        
        return formatted_contatos
    
    except UserNotFoundError as e:
        raise UserNotFoundError("Usuário não encontrado")
    
    except Exception as e:
        raise e



def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

