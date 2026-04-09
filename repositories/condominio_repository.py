"""
Repository para operações de Condomínio
"""
from typing import Optional, List
from repositories.base_repository import BaseRepository
from models.condominio import Condominio
from core.exceptions import DuplicateError


class CondominioRepository(BaseRepository):
    table_name = "Condominios"

    @classmethod
    def _row_to_obj(cls, row) -> Condominio:
        return Condominio(
            id=row[0], nome_condominio=row[1], endereco=row[2], cnpj=row[3],
            tipo_condominio=row[4], quantidade_blocos=row[5], quantidade_unidades=row[6],
            data_fundacao=row[7], area_total=row[8], responsavel_manutencao=row[9], oculto=row[10]
        )

    @classmethod
    def get_by_id(cls, cond_id: int) -> Optional[Condominio]:
        query = """
            SELECT id, nome_condominio, endereco, cnpj, tipo_condominio,
                   quantidade_blocos, quantidade_unidades, data_fundacao,
                   area_total, responsavel_manutencao, COALESCE(oculto, FALSE)
            FROM Condominios WHERE id = %s
        """
        result = cls.execute_query(query, (cond_id,), fetch_one=True)
        return cls._row_to_obj(result) if result else None

    @classmethod
    def get_by_user(cls, user_id: int) -> List[Condominio]:
        query = """
            SELECT id, nome_condominio, endereco, cnpj, tipo_condominio,
                   quantidade_blocos, quantidade_unidades, data_fundacao,
                   area_total, responsavel_manutencao, COALESCE(oculto, FALSE)
            FROM Condominios
            WHERE responsavel_manutencao = %s AND COALESCE(oculto, FALSE) = FALSE
            ORDER BY nome_condominio
        """
        results = cls.execute_query(query, (user_id,), fetch_all=True)
        return [cls._row_to_obj(r) for r in results]

    @classmethod
    def cnpj_exists(cls, cnpj: str) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM Condominios WHERE cnpj = %s)"
        result = cls.execute_query(query, (cnpj,), fetch_one=True)
        return result[0] if result else False

    @classmethod
    def verify_ownership(cls, cond_id: int, user_id: int) -> bool:
        query = """
            SELECT EXISTS(SELECT 1 FROM Condominios
            WHERE id = %s AND responsavel_manutencao = %s)
        """
        result = cls.execute_query(query, (cond_id, user_id), fetch_one=True)
        return result[0] if result else False

    @classmethod
    def find_by_name_and_cnpj(cls, nome: str, cnpj: str, user_id: int) -> Optional[int]:
        query = """
            SELECT id FROM Condominios
            WHERE nome_condominio = %s AND cnpj = %s AND responsavel_manutencao = %s
        """
        result = cls.execute_query(query, (nome, cnpj, user_id), fetch_one=True)
        return result[0] if result else None

    @classmethod
    def hide_condominio(cls, cond_id: int) -> bool:
        query = "UPDATE Condominios SET oculto = TRUE WHERE id = %s"
        rows = cls.execute_query(query, (cond_id,), commit=True)
        return rows > 0

    @classmethod
    def create(cls, nome, endereco, cnpj, tipo, blocos, unidades, data_fundacao, user_id) -> int:
        if cls.cnpj_exists(cnpj):
            raise DuplicateError("CNPJ já cadastrado")
        query = """
            INSERT INTO Condominios
            (nome_condominio, endereco, cnpj, tipo_condominio, quantidade_blocos,
             data_fundacao, quantidade_unidades, responsavel_manutencao, oculto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)
            RETURNING id
        """
        result = cls.execute_query(
            query, (nome, endereco, cnpj, tipo, blocos, data_fundacao, unidades, user_id),
            fetch_one=True, commit=True
        )
        return result[0] if result else None

    @classmethod
    def delete_with_relations(cls, cond_id: int) -> bool:
        queries = [
            ("DELETE FROM Registro_Manutencao WHERE condominio_id = %s", (cond_id,)),
            ("DELETE FROM Planos WHERE condominio_id = %s", (cond_id,)),
            ("DELETE FROM Condominios WHERE id = %s", (cond_id,))
        ]
        try:
            for query, params in queries:
                cls.execute_query(query, params, commit=True)
            return True
        except Exception as e:
            print(f"Erro ao deletar condomínio: {e}")
            return False

    @classmethod
    def get_statistics(cls, user_id: int) -> dict:
        query = """
            SELECT COUNT(*),
                   SUM(quantidade_blocos), SUM(quantidade_unidades),
                   COUNT(CASE WHEN tipo_condominio='Residencial' THEN 1 END),
                   COUNT(CASE WHEN tipo_condominio='Comercial'   THEN 1 END),
                   COUNT(CASE WHEN tipo_condominio='Misto'       THEN 1 END)
            FROM Condominios
            WHERE responsavel_manutencao = %s AND COALESCE(oculto, FALSE) = FALSE
        """
        result = cls.execute_query(query, (user_id,), fetch_one=True)
        if result:
            return {
                'total': result[0] or 0, 'total_blocos': result[1] or 0,
                'total_unidades': result[2] or 0, 'residenciais': result[3] or 0,
                'comerciais': result[4] or 0, 'mistos': result[5] or 0
            }
        return {'total': 0, 'total_blocos': 0, 'total_unidades': 0,
                'residenciais': 0, 'comerciais': 0, 'mistos': 0}
