from typing import List

class PlanPurchaseInterest:
    @classmethod
    def get_user_interests(cls, user_id: int) -> List["PlanPurchaseInterest"]:
        """Busca todos os interesses de um usuário específico"""
        return cls.query.filter_by(user_id=user_id).all() 