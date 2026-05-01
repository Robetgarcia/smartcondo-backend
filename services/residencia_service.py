"""
Service de Residências
"""
from typing import Optional, Tuple, List
from repositories.residencia_repository import ResidenciaRepository
from core.validators import Validator
from core.exceptions import ValidationError


class ResidenciaService:

    @staticmethod
    def vincular_por_nome_cnpj(cliente_id: int, condominio_nome: str,
                                condominio_cnpj: str, numero_unidade: str,
                                bloco: str = None) -> Tuple[Optional[int], Optional[str]]:
        """Vincula morador por nome + CNPJ (fluxo do próprio morador)."""
        try:
            nome_val = Validator.validate_not_empty(condominio_nome, "Nome do condomínio")
            cnpj_val = Validator.validate_cnpj(condominio_cnpj)
            unid_val = Validator.validate_not_empty(numero_unidade, "Número da unidade")

            from config.database import db
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM Condominios
                    WHERE LOWER(nome_condominio) = LOWER(%s)
                      AND cnpj = %s
                      AND COALESCE(oculto, FALSE) = FALSE
                """, (nome_val, cnpj_val))
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

            if not res_id:
                return None, "Erro ao salvar vínculo. Verifique se a tabela Residencias existe no banco."

            return res_id, None

        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao vincular: {str(e)}"

    @staticmethod
    def vincular_por_id(cliente_id: int, condominio_id: int,
                        numero_unidade: str,
                        bloco: str = None) -> Tuple[Optional[int], Optional[str]]:
        """Vincula morador diretamente pelo ID (fluxo do síndico)."""
        try:
            unid_val = Validator.validate_not_empty(numero_unidade, "Número da unidade")

            res_id = ResidenciaRepository.criar(
                cliente_id=cliente_id,
                condominio_id=condominio_id,
                numero_unidade=unid_val,
                bloco=bloco.strip() if bloco else None
            )

            if not res_id:
                return None, "Erro ao salvar. Verifique se a tabela Residencias existe no banco de dados."

            return res_id, None

        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao vincular: {str(e)}"

    @staticmethod
    def get_moradores_condominio(cond_id: int) -> List[dict]:
        """Retorna lista de moradores de um condomínio."""
        return ResidenciaRepository.get_by_condominio(cond_id)

    @staticmethod
    def get_residencia_cliente(cliente_id: int) -> Optional[dict]:
        """Retorna onde o cliente mora."""
        return ResidenciaRepository.get_by_cliente(cliente_id)

    @staticmethod
    def remover_morador(residencia_id: int) -> Tuple[bool, Optional[str]]:
        """Remove (inativa) vínculo de um morador."""
        try:
            if ResidenciaRepository.inativar(residencia_id):
                return True, None
            return False, "Registro não encontrado"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    @staticmethod
    def buscar_usuario_por_email(email: str) -> Optional[dict]:
        """Busca usuário pelo email."""
        try:
            from repositories.user_repository import UserRepository
            result = UserRepository.find_by_email(email)
            if not result:
                return None
            user = UserRepository.get_by_id(result[0])
            return user.to_dict() if user else None
        except Exception:
            return None
