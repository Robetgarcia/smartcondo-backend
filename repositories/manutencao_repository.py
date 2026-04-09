"""
Repository para operações de Manutenção
"""
from typing import Optional, List
from repositories.base_repository import BaseRepository
from models.manutencao import Manutencao


class ManutencaoRepository(BaseRepository):
    table_name = "Registro_Manutencao"

    @classmethod
    def _row_to_obj(cls, row) -> Manutencao:
        return Manutencao(
            id=row[0], condominio_id=row[1], nome_manutencao=row[2],
            tipo_manutencao=row[3], data_solicitacao=row[4], custo_estimado=row[5],
            prestador_servico=row[6], obrigacoes_condominio=row[7], grau_urgencia=row[8],
            status=row[9], solicitante_id=row[10], solicitante=row[11]
        )

    _SELECT = """
        SELECT id, condominio_id, nome_manutencao, tipo_manutencao,
               data_solicitacao, custo_estimado, prestador_servico,
               obrigacoes_condominio, grau_urgencia, status,
               solicitante_id, solicitante
        FROM Registro_Manutencao
    """

    @classmethod
    def get_by_id(cls, manut_id: int) -> Optional[Manutencao]:
        result = cls.execute_query(cls._SELECT + "WHERE id = %s", (manut_id,), fetch_one=True)
        return cls._row_to_obj(result) if result else None

    @classmethod
    def get_by_condominio(cls, cond_id: int, user_id: int) -> List[Manutencao]:
        results = cls.execute_query(
            cls._SELECT + "WHERE condominio_id = %s AND solicitante_id = %s ORDER BY data_solicitacao DESC",
            (cond_id, user_id), fetch_all=True
        )
        return [cls._row_to_obj(r) for r in results]

    @classmethod
    def get_all_by_user(cls, user_id: int) -> List[Manutencao]:
        results = cls.execute_query(
            cls._SELECT + "WHERE solicitante_id = %s ORDER BY data_solicitacao DESC",
            (user_id,), fetch_all=True
        )
        return [cls._row_to_obj(r) for r in results]

    @classmethod
    def create(cls, cond_id, nome, tipo, data_solicitacao, status, user_id,
               custo=None, prestador=None, descricao=None, urgencia=None) -> int:
        query = """
            INSERT INTO Registro_Manutencao
            (condominio_id, nome_manutencao, tipo_manutencao, data_solicitacao,
             custo_estimado, prestador_servico, obrigacoes_condominio,
             grau_urgencia, status, solicitante_id, solicitante)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """
        result = cls.execute_query(
            query,
            (cond_id, nome, tipo, data_solicitacao, custo, prestador,
             descricao, urgencia, status, user_id, f"Usuário {user_id}"),
            fetch_one=True, commit=True
        )
        return result[0] if result else None

    @classmethod
    def update_status(cls, manut_id: int, new_status: str) -> bool:
        rows = cls.execute_query(
            "UPDATE Registro_Manutencao SET status = %s WHERE id = %s",
            (new_status, manut_id), commit=True
        )
        return rows > 0

    @classmethod
    def get_statistics(cls, user_id: int) -> dict:
        query = """
            SELECT COUNT(*),
                   COUNT(CASE WHEN status='Pendente'     THEN 1 END),
                   COUNT(CASE WHEN status='Em Andamento' THEN 1 END),
                   COUNT(CASE WHEN status='Concluída'    THEN 1 END),
                   COUNT(CASE WHEN grau_urgencia IN ('Alta','Crítica') THEN 1 END),
                   SUM(COALESCE(custo_estimado, 0))
            FROM Registro_Manutencao WHERE solicitante_id = %s
        """
        result = cls.execute_query(query, (user_id,), fetch_one=True)
        if result:
            return {
                'total': result[0] or 0, 'pendentes': result[1] or 0,
                'em_andamento': result[2] or 0, 'concluidas': result[3] or 0,
                'urgentes': result[4] or 0, 'custo_total': float(result[5] or 0)
            }
        return {'total': 0, 'pendentes': 0, 'em_andamento': 0,
                'concluidas': 0, 'urgentes': 0, 'custo_total': 0.0}

    @classmethod
    def get_recent(cls, user_id: int, limit: int = 5) -> List[Manutencao]:
        results = cls.execute_query(
            cls._SELECT + "WHERE solicitante_id = %s ORDER BY data_solicitacao DESC LIMIT %s",
            (user_id, limit), fetch_all=True
        )
        return [cls._row_to_obj(r) for r in results]
