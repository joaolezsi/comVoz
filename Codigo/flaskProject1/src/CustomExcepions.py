class MissingFieldsException(Exception):
    pass


class UserAlreadyExistsException(Exception):
    pass


class InvalidPasswordException(Exception):
    """Exceção lançada quando a senha é inválida"""
    pass


class UserNotFoundException(Exception):
    pass


class PlanNotFoundException(Exception):
    """Exceção lançada quando o plano não é encontrado"""
    pass


class UserAlreadyHasPlanException(Exception):
    """Exceção lançada quando o usuário já possui um plano ativo"""
    pass


class UserHasBetterPlanException(Exception):
    """Exceção lançada quando o usuário já possui um plano mais caro"""
    pass


class FreePlanException(Exception):
    """Exceção lançada quando o plano não é gratuito"""
    pass


class QuestionNotFoundException(Exception):
    """Exceção lançada quando a questão não é encontrada"""
    pass


class UserNotFoundError(Exception):
    """Exceção lançada quando o usuário não é encontrado"""
    pass

class UserNotFoundError(Exception):
    """Exceção lançada quando o usuário não é encontrado"""
    pass


class LimitePesquisaException(Exception):
    """Exceção lançada quando o limite de pesquisas é atingido"""
    pass

class PesquisaNotFoundException(Exception):
    """Exceção lançada quando a pesquisa não é encontrada"""
    pass


class UserNotAdminException(Exception):
    """Exceção lançada quando o usuário não é administrador"""
    pass

class InvalidDataException(Exception):
    """Exceção lançada quando os dados são inválidos"""
    pass


class LimiteEnviosException(Exception):
    """Exceção lançada quando o limite de envios é atingido"""
    pass


class UserWithoutContatosException(Exception):
    """Exceção lançada quando o usuário não possui contatos"""
    pass


class EmailSenderException(Exception):
    """Exceção lançada quando o email não é enviado"""
    pass


class UserWithoutPlanException(Exception):
    """Exceção lançada quando o usuário não possui um plano ativo"""
    pass

class UserWithoutContatosException(Exception):
    """Exceção lançada quando o usuário não possui contatos"""
    pass

class PlanPurchaseInterestNotFoundException(Exception):
    """Exceção lançada quando o interesse não é encontrado"""
    pass


class NpsQuestionsException(Exception):
    """Exceção lançada quando a pesquisa não possui pelo menos 5 perguntas do tipo NPS"""
    pass


class InvalidQuestionTypeException(Exception):
    """Exceção lançada quando o tipo de questão é inválido"""
    pass


class EmailAlreadyAnsweredException(Exception):
    """Exceção lançada quando o email já respondeu a pesquisa"""
    pass


class InvalidEmailException(Exception):
    """Exceção lançada quando o email é inválido"""
    pass


class InvalidEmailException(Exception):
    """Exceção lançada quando o email é inválido"""
    pass



class UserAlreadyHasInterestException(Exception):
    """Exceção lançada quando o usuário já possui um interesse"""
    pass


class UserAlreadyHasPlanException(Exception):
    """Exceção lançada quando o usuário já possui um plano"""
    pass
