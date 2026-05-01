"""
Repository para operações de Condomínio + Moradores
Versão corrigida e limpa para deploy
"""

from typing import Optional, List
from repositories.base_repository import BaseRepository
from models.condominio import Condominio
from core.exceptions import DuplicateError


class CondominioRepository(BaseRepository):
    table_name = "Condominios"

    # ====================== CONDOMÍNIO ======================

    @classmethod
    def _row_to_obj(cls, row) -> Condominio:
        return Condominio(
            id=row[0],
            nome_condominio=row[1],
            endereco=row[2],
            cnpj=row[3],
            tipo_condominio=row[4],
            quantidade_blocos=row[5],
            quantidade_unidades=row[6],
            data_fundacao=row[7],
            area_total=row[8],
            responsavel_manutencao=row[9],
            oculto=row[10]
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
            WHERE responsavel_manutencao = %s 
              AND COALESCE(oculto, FALSE) = FALSE
            ORDER BY nome_condominio
        """
        results = cls.execute_query(query, (user_id,), fetch_all=True)
        return [cls._row_to_obj(r) for r in results]

    @classmethod
    def verify_ownership(cls, cond_id: int, user_id: int) -> bool:
        """Verifica se o usuário tem permissão no condomínio"""
        query = """
            SELECT EXISTS (
                SELECT 1 
                FROM Condominios c
                WHERE c.id = %s 
                  AND (
                      c.responsavel_manutencao = %s
                      OR EXISTS (
                          SELECT 1 FROM Residencias r 
                          WHERE r.condominio_id = c.id 
                            AND r.cliente_id = %s 
                            AND r.ativo = TRUE
                      )
                  )
            )
        """
        result = cls.execute_query(query, (cond_id, user_id, user_id), fetch_one=True)
        return bool(result[0]) if result else False

    @classmethod
    def cnpj_exists(cls, cnpj: str) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM Condominios WHERE cnpj = %s)"
        result = cls.execute_query(query, (cnpj,), fetch_one=True)
        return result[0] if result else False

    @classmethod
    def find_by_name_and_cnpj(cls, nome: str, cnpj: str, user_id: int) -> Optional[int]:
        query = """
            SELECT id FROM Condominios
            WHERE LOWER(nome_condominio) = LOWER(%s) 
              AND cnpj = %s 
              AND responsavel_manutencao = %s
        """
        result = cls.execute_query(query, (nome, cnpj, user_id), fetch_one=True)
        return result[0] if result else None

    @classmethod
    def get_moradores_by_condominio(cls, cond_id: int) -> List[dict]:
        """Retorna todos os moradores de um condomínio"""
        query = """
            SELECT 
                r.id AS residencia_id,
                c.id AS cliente_id,
                c.nome_completo,
                c.email,
                c.telefone,
                c.tipo_cliente,
                c.cpf,
                r.bloco,
                r.numero_unidade,
                r.data_entrada,
                r.ativo
            FROM Residencias r
            INNER JOIN Cliente c ON c.id = r.cliente_id
            WHERE r.condominio_id = %s 
              AND r.ativo = TRUE
            ORDER BY c.nome_completo ASC
        """
        results = cls.execute_query(query, (cond_id,), fetch_all=True)
        
        return [{
            'residencia_id':   row[0],
            'id':              row[1],
            'nome_completo':   row[2],
            'email':           row[3],
            'telefone':        row[4],
            'tipo_cliente':    row[5],
            'cpf':             row[6],
            'bloco':           row[7],
            'numero_unidade':  row[8],
            'data_entrada':    row[9].isoformat() if row[9] else None,
            'ativo':           row[10]
        } for row in results]

    @classmethod
    def create(cls, nome, endereco, cnpj, tipo, blocos, unidades, 
               data_fundacao, user_id) -> Optional[int]:
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
            query, 
            (nome, endereco, cnpj, tipo, blocos, data_fundacao, unidades, user_id),
            fetch_one=True, 
            commit=True
        )
        return result[0] if result else None

    @classmethod
    def hide_condominio(cls, cond_id: int) -> bool:
        query = "UPDATE Condominios SET oculto = TRUE WHERE id = %s"
        rows = cls.execute_query(query, (cond_id,), commit=True)
        return rows > 0

    @classmethod
    def delete_with_relations(cls, cond_id: int) -> bool:
        queries = [
            ("DELETE FROM Registro_Manutencao WHERE condominio_id = %s", (cond_id,)),
            ("DELETE FROM Planos WHERE condominio_id = %s", (cond_id,)),
            ("DELETE FROM Residencias WHERE condominio_id = %s", (cond_id,)),
            ("DELETE FROM Condominios WHERE id = %s", (cond_id,))
        ]
        try:
            for query, params in queries:
                cls.execute_query(query, params, commit=True)
            return True
        except Exception as e:
            print(f"Erro ao deletar condomínio: {e}")
            return False
