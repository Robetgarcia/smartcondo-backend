"""
Repository base com métodos comuns
"""
from abc import ABC
from config.database import db
from core.exceptions import DatabaseError


class BaseRepository(ABC):
    table_name = None

    @classmethod
    def execute_query(cls, query: str, params: tuple = None,
                      fetch_one=False, fetch_all=False, commit=False):
        try:
            with db.get_cursor(commit=commit) as cursor:
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                elif commit:
                    return cursor.rowcount
                return None
        except Exception as e:
            raise DatabaseError(f"Erro ao executar query: {e}")

    @classmethod
    def find_by_id(cls, id: int):
        query = f"SELECT * FROM {cls.table_name} WHERE id = %s"
        return cls.execute_query(query, (id,), fetch_one=True)

    @classmethod
    def find_all(cls):
        query = f"SELECT * FROM {cls.table_name}"
        return cls.execute_query(query, fetch_all=True)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = f"DELETE FROM {cls.table_name} WHERE id = %s"
        rows = cls.execute_query(query, (id,), commit=True)
        return rows > 0

    @classmethod
    def exists(cls, id: int) -> bool:
        query = f"SELECT EXISTS(SELECT 1 FROM {cls.table_name} WHERE id = %s)"
        result = cls.execute_query(query, (id,), fetch_one=True)
        return result[0] if result else False
