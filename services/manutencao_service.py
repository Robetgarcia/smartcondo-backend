"""
Service de Manutenção
"""
from typing import Optional, Tuple, List
from repositories.manutencao_repository import ManutencaoRepository
from repositories.condominio_repository import CondominioRepository
from models.manutencao import Manutencao
from core.validators import Validator
from core.exceptions import ValidationError


class ManutencaoService:
    TIPOS_VALIDOS    = ["Preventiva", "Corretiva", "Obrigatória"]
    STATUS_VALIDOS   = ["Pendente", "Em Andamento", "Concluída"]
    URGENCIAS_VALIDAS = ["Baixa", "Média", "Alta", "Crítica"]

    @staticmethod
    def create_manutencao(cond_id, user_id, nome, tipo, data_solicitacao, status,
                          custo=None, prestador=None, descricao=None,
                          urgencia=None) -> Tuple[Optional[int], Optional[str]]:
        try:
            if not CondominioRepository.verify_ownership(cond_id, user_id):
                return None, "Você não tem acesso a este condomínio"
            nome = Validator.validate_not_empty(nome, "Nome da manutenção")
            if tipo not in ManutencaoService.TIPOS_VALIDOS:
                return None, f"Tipo inválido. Use: {', '.join(ManutencaoService.TIPOS_VALIDOS)}"
            if status not in ManutencaoService.STATUS_VALIDOS:
                return None, f"Status inválido. Use: {', '.join(ManutencaoService.STATUS_VALIDOS)}"
            data_obj   = Validator.validate_date(data_solicitacao, "%d/%m/%Y")
            custo_float = Validator.validate_positive_number(str(custo), "Custo") if custo else None
            if urgencia and urgencia not in ManutencaoService.URGENCIAS_VALIDAS:
                return None, f"Urgência inválida. Use: {', '.join(ManutencaoService.URGENCIAS_VALIDAS)}"
            manut_id = ManutencaoRepository.create(
                cond_id=cond_id, nome=nome, tipo=tipo,
                data_solicitacao=data_obj.date(), status=status, user_id=user_id,
                custo=custo_float,
                prestador=prestador.strip() if prestador else None,
                descricao=descricao.strip() if descricao else None,
                urgencia=urgencia if urgencia else None
            )
            return manut_id, None
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao cadastrar: {e}"

    @staticmethod
    def get_by_condominio(cond_id: int, user_id: int) -> Tuple[List[Manutencao], Optional[str]]:
        try:
            if not CondominioRepository.verify_ownership(cond_id, user_id):
                return [], "Você não tem acesso a este condomínio"
            return ManutencaoRepository.get_by_condominio(cond_id, user_id), None
        except Exception as e:
            return [], f"Erro: {e}"

    @staticmethod
    def get_all_user_manutencoes(user_id: int) -> List[Manutencao]:
        return ManutencaoRepository.get_all_by_user(user_id)

    @staticmethod
    def get_recent(user_id: int, limit: int = 5) -> List[Manutencao]:
        return ManutencaoRepository.get_recent(user_id, limit)

    @staticmethod
    def update_status(manut_id: int, new_status: str) -> Tuple[bool, Optional[str]]:
        try:
            if new_status not in ManutencaoService.STATUS_VALIDOS:
                return False, f"Status inválido. Use: {', '.join(ManutencaoService.STATUS_VALIDOS)}"
            if ManutencaoRepository.update_status(manut_id, new_status):
                return True, None
            return False, "Erro ao atualizar status"
        except Exception as e:
            return False, f"Erro: {e}"

    @staticmethod
    def delete_manutencao(manut_id: int) -> Tuple[bool, Optional[str]]:
        try:
            if ManutencaoRepository.delete(manut_id):
                return True, None
            return False, "Erro ao deletar manutenção"
        except Exception as e:
            return False, f"Erro: {e}"

    @staticmethod
    def get_statistics(user_id: int) -> dict:
        return ManutencaoRepository.get_statistics(user_id)
