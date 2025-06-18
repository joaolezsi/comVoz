from enum import Enum


class InterestStatusEnum(Enum):
    """
    Enum para os status possíveis de um interesse de compra
    
    Attributes:
        PENDING (int): Interesse pendente (1)
        ATTENDED (int): Interesse atendido (2)
        CANCELLED (int): Interesse cancelado (3)
    """
    PENDING = 1
    ATTENDED = 2
    CANCELLED = 3
    
    @classmethod
    def from_int(cls, value: int) -> 'InterestStatusEnum':
        """
        Obtém o enum a partir de um valor inteiro
        
        Args:
            value (int): Valor inteiro do status
            
        Returns:
            InterestStatusEnum: Enum correspondente ao valor
            
        Raises:
            ValueError: Se o valor não corresponder a nenhum status
        """
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Status inválido: {value}")
    
    def to_str(self) -> str:
        """
        Converte o enum para string
        
        Returns:
            str: String representando o status
        """
        status_map = {
            InterestStatusEnum.PENDING: 'pendente',
            InterestStatusEnum.ATTENDED: 'atendido',
            InterestStatusEnum.CANCELLED: 'cancelado'
        }
        return status_map[self]