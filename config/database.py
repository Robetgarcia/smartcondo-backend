"""
Gerenciador de conexões com PostgreSQL usando Connection Pool
Compatível com Neon (requer SSL)
"""
import psycopg2
from psycopg2 import pool, Error
from contextlib import contextmanager


class DatabaseManager:
    """Singleton para gerenciar pool de conexões"""

    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is None:
            self._initialize_pool()

    def _initialize_pool(self):
        try:
            from config.settings import DATABASE
            # Neon exige sslmode=require — sem isso a conexão é recusada
            self._pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                sslmode='require',
                **DATABASE
            )
            print("✅ Pool de conexões criado com sucesso")
        except Error as e:
            raise Exception(f"Erro ao criar pool de conexões: {e}")

    def get_connection(self):
        try:
            return self._pool.getconn()
        except Error as e:
            raise Exception(f"Erro ao obter conexão: {e}")

    def return_connection(self, conn):
        try:
            self._pool.putconn(conn)
        except Error as e:
            print(f"⚠️ Erro ao devolver conexão: {e}")

    def close_all_connections(self):
        if self._pool:
            self._pool.closeall()
            print("✅ Todas as conexões fechadas")

    @contextmanager
    def get_cursor(self, commit=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Error as e:
            conn.rollback()
            raise Exception(f"Erro no banco de dados: {e}")
        finally:
            cursor.close()
            self.return_connection(conn)


db = DatabaseManager()
