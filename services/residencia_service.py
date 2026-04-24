"""
Service de Residências
Gerencia o vínculo morador ↔ condomínio.
"""
from typing import Optional, Tuple, List
from repositories.residencia_repository import ResidenciaRepository
from repositories.condominio_repository import CondominioRepository
from core.validators import Validator
from core.exceptions import ValidationError, DuplicateError


class ResidenciaService:

    @staticmethod
    def vincular_morador(cliente_id: int, condominio_nome: str,
                         condominio_cnpj: str, numero_unidade: str,
                         bloco: str = None) -> Tuple[Optional[int], Optional[str]]:
        """
        Vincula um morador a um condomínio pelo nome + CNPJ.
        O morador informa onde mora durante ou após o cadastro.
        """
        try:
            nome_val = Validator.validate_not_empty(condominio_nome, "Nome do condomínio")
            cnpj_val = Validator.validate_cnpj(condominio_cnpj)
            unid_val = Validator.validate_not_empty(numero_unidade, "Número da unidade")

            # Busca o condomínio pelo nome + CNPJ (não precisa ser o responsável)
            query = """
                SELECT id FROM Condominios
                WHERE nome_condominio = %s AND cnpj = %s
                  AND COALESCE(oculto, FALSE) = FALSE
            """
            from config.database import db
            with db.get_cursor() as cursor:
                cursor.execute(query, (nome_val, cnpj_val))
                row = cursor.fetchone()

            if not row:
                return None, "Condomínio não encontrado. Verifique o nome e CNPJ."

            cond_id = row[0]

            if ResidenciaRepository.ja_cadastrado(cliente_id, cond_id):
                return None, "Você já está cadastrado neste condomínio."

            res_id = ResidenciaRepository.criar(
                cliente_id=cliente_id,
                condominio_id=cond_id,
                numero_unidade=unid_val,
                bloco=bloco.strip() if bloco else None
            )
            return res_id, None

        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao vincular: {e}"

    @staticmethod
    def get_moradores_condominio(cond_id: int) -> List[dict]:
        """Retorna lista de moradores de um condomínio."""
        return ResidenciaRepository.get_by_condominio(cond_id)

    @staticmethod
    def get_residencia_cliente(cliente_id: int) -> Optional[dict]:
        """Retorna onde o cliente mora (se tiver cadastrado)."""
        return ResidenciaRepository.get_by_cliente(cliente_id)

    @staticmethod
    def remover_morador(residencia_id: int) -> Tuple[bool, Optional[str]]:
        """Remove (inativa) vínculo de um morador."""
        try:
            if ResidenciaRepository.inativar(residencia_id):
                return True, None
            return False, "Registro não encontrado"
        except Exception as e:
            return False, f"Erro: {e}"
