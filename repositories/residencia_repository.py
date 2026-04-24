"""
Repository para Residencias
Vincula moradores a condomínios com bloco e número de unidade.
"""
from typing import Optional, List
from repositories.base_repository import BaseRepository


class ResidenciaRepository(BaseRepository):
    table_name = "Residencias"

    @classmethod
    def get_by_condominio(cls, cond_id: int) -> List[dict]:
        """
        Retorna todos os moradores ativos de um condomínio,
        com dados do cliente e da residência.
        """
        query = """
            SELECT
                c.id, c.nome_completo, c.email, c.cpf,
                c.telefone, c.tipo_cliente,
                r.bloco, r.numero_unidade, r.data_entrada, r.id AS res_id
            FROM Residencias r
            INNER JOIN Cliente c ON c.id = r.cliente_id
            WHERE r.condominio_id = %s AND r.ativo = TRUE
            ORDER BY r.bloco NULLS FIRST, r.numero_unidade
        """
        results = cls.execute_query(query, (cond_id,), fetch_all=True)
        moradores = []
        for row in results:
            moradores.append({
                'id':             row[0],
                'nome_completo':  row[1],
                'email':          row[2],
                'cpf':            row[3],
                'telefone':       row[4],
                'tipo_cliente':   row[5],
                'bloco':          row[6],
                'numero_unidade': row[7],
                'data_entrada':   row[8].isoformat() if row[8] else None,
                'residencia_id':  row[9],
            })
        return moradores

    @classmethod
    def get_by_cliente(cls, cliente_id: int) -> Optional[dict]:
        """Retorna a residência ativa de um cliente (se tiver)."""
        query = """
            SELECT r.id, r.condominio_id, r.bloco, r.numero_unidade,
                   r.data_entrada, c.nome_condominio
            FROM Residencias r
            INNER JOIN Condominios c ON c.id = r.condominio_id
            WHERE r.cliente_id = %s AND r.ativo = TRUE
            LIMIT 1
        """
        row = cls.execute_query(query, (cliente_id,), fetch_one=True)
        if not row:
            return None
        return {
            'id':             row[0],
            'condominio_id':  row[1],
            'bloco':          row[2],
            'numero_unidade': row[3],
            'data_entrada':   row[4].isoformat() if row[4] else None,
            'nome_condominio': row[5],
        }

    @classmethod
    def criar(cls, cliente_id: int, condominio_id: int,
              numero_unidade: str, bloco: str = None,
              data_entrada: str = None) -> int:
        """Cria vínculo morador → condomínio."""
        query = """
            INSERT INTO Residencias
                (cliente_id, condominio_id, bloco, numero_unidade, data_entrada)
            VALUES (%s, %s, %s, %s, COALESCE(%s::DATE, CURRENT_DATE))
            ON CONFLICT (cliente_id, condominio_id)
            DO UPDATE SET
                bloco = EXCLUDED.bloco,
                numero_unidade = EXCLUDED.numero_unidade,
                ativo = TRUE
            RETURNING id
        """
        result = cls.execute_query(
            query,
            (cliente_id, condominio_id, bloco, numero_unidade, data_entrada),
            fetch_one=True, commit=True
        )
        return result[0] if result else None

    @classmethod
    def inativar(cls, residencia_id: int) -> bool:
        """Inativa (sem deletar) o vínculo."""
        rows = cls.execute_query(
            "UPDATE Residencias SET ativo = FALSE WHERE id = %s",
            (residencia_id,), commit=True
        )
        return rows > 0

    @classmethod
    def ja_cadastrado(cls, cliente_id: int, condominio_id: int) -> bool:
        """Verifica se o morador já está vinculado ao condomínio."""
        result = cls.execute_query(
            "SELECT EXISTS(SELECT 1 FROM Residencias WHERE cliente_id=%s AND condominio_id=%s AND ativo=TRUE)",
            (cliente_id, condominio_id), fetch_one=True
        )
        return result[0] if result else False
