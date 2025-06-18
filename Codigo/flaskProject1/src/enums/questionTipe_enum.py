from enum import Enum

class QuestionTypeEnum(Enum):
    MULTIPLE_CHOICE = "escolha"
    NPS = "nps"
    TEXT = "texto"

    @staticmethod
    def from_int(value: int) -> 'QuestionTypeEnum':
        """
        Converte um número para o enum correspondente
        
        Args:
            value (int): Número do tipo de questão
            
        Returns:
            QuestionTypeEnum: Enum correspondente ou None se não encontrado
        """
        mapping = {
            1: QuestionTypeEnum.MULTIPLE_CHOICE,
            2: QuestionTypeEnum.NPS,
            3: QuestionTypeEnum.TEXT
        }
        return mapping.get(value)

    @staticmethod
    def from_str(value: str) -> 'QuestionTypeEnum':
        """
        Converte uma string para o enum correspondente
        
        Args:
            value (str): String do tipo de questão
            
        Returns:
            QuestionTypeEnum: Enum correspondente ou None se não encontrado
        """
        for question_type in QuestionTypeEnum:
            if question_type.value == value:
                return question_type
        return None
