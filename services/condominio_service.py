"""
Service de Condomínio
"""
from typing import Optional, Tuple, List
from repositories.condominio_repository import CondominioRepository
from models.condominio import Condominio
from core.validators import Validator
from core.exceptions import ValidationError, DuplicateError


class CondominioService:
    TIPOS_VALIDOS = ["Comercial", "Residencial", "Misto"]

    @staticmethod
    def create_condominio(nome, endereco, cnpj, tipo, blocos, unidades,
                          data_fundacao, user_id) -> Tuple[Optional[int], Optional[str]]:
        try:
            nome     = Validator.validate_not_empty(nome, "Nome do condomínio")
            endereco = Validator.validate_not_empty(endereco, "Endereço")
            cnpj     = Validator.validate_cnpj(cnpj)
            if tipo not in CondominioService.TIPOS_VALIDOS:
                return None, f"Tipo inválido. Use: {', '.join(CondominioService.TIPOS_VALIDOS)}"
            blocos_int   = Validator.validate_positive_integer(str(blocos), "Blocos")
            unidades_int = Validator.validate_positive_integer(str(unidades), "Unidades")
            data_obj     = Validator.validate_date(data_fundacao, "%Y-%m-%d")
            cond_id = CondominioRepository.create(
                nome=nome, endereco=endereco, cnpj=cnpj, tipo=tipo,
                blocos=blocos_int, unidades=unidades_int,
                data_fundacao=data_obj.date(), user_id=user_id
            )
            return cond_id, None
        except ValidationError as e:
            return None, str(e)
        except DuplicateError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao cadastrar: {e}"

    @staticmethod
    def get_user_condominios(user_id: int) -> List[Condominio]:
        return CondominioRepository.get_by_user(user_id)

    @staticmethod
    def get_condominio(cond_id: int, user_id: int) -> Tuple[Optional[Condominio], Optional[str]]:
        try:
            if not CondominioRepository.verify_ownership(cond_id, user_id):
                return None, "Você não tem acesso a este condomínio"
            cond = CondominioRepository.get_by_id(cond_id)
            if not cond:
                return None, "Condomínio não encontrado"
            return cond, None
        except Exception as e:
            return None, f"Erro: {e}"

    @staticmethod
    def login_condominio(nome: str, cnpj: str, user_id: int) -> Tuple[Optional[int], Optional[str]]:
        try:
            nome = Validator.validate_not_empty(nome, "Nome")
            cnpj = Validator.validate_cnpj(cnpj)
            cond_id = CondominioRepository.find_by_name_and_cnpj(nome, cnpj, user_id)
            if cond_id:
                return cond_id, None
            return None, "Condomínio não encontrado ou você não é o responsável"
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro: {e}"

    @staticmethod
    def hide_condominio(cond_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        try:
            if not CondominioRepository.verify_ownership(cond_id, user_id):
                return False, "Você não tem permissão para ocultar este condomínio"
            if CondominioRepository.hide_condominio(cond_id):
                return True, None
            return False, "Erro ao ocultar condomínio"
        except Exception as e:
            return False, f"Erro: {e}"

    @staticmethod
    def delete_condominio(cond_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        try:
            if not CondominioRepository.verify_ownership(cond_id, user_id):
                return False, "Você não tem permissão para deletar este condomínio"
            if CondominioRepository.delete_with_relations(cond_id):
                return True, None
            return False, "Erro ao deletar condomínio"
        except Exception as e:
            return False, f"Erro: {e}"

    @staticmethod
    def get_statistics(user_id: int) -> dict:
        return CondominioRepository.get_statistics(user_id)
