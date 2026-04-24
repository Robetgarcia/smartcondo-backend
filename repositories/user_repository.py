"""
Repository para operações de Usuário
"""
from typing import Optional
from repositories.base_repository import BaseRepository
from models.user import User
from core.exceptions import DuplicateError


class UserRepository(BaseRepository):
    table_name = "Cliente"

    @classmethod
    def find_by_email(cls, email: str) -> Optional[tuple]:
        return cls.execute_query(
            "SELECT id, senha FROM Cliente WHERE email = %s",
            (email.lower(),), fetch_one=True
        )

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional[User]:
        result = cls.execute_query(
            "SELECT id, nome_completo, email, data_nascimento, cpf, telefone, tipo_cliente FROM Cliente WHERE id = %s",
            (user_id,), fetch_one=True
        )
        if result:
            return User(id=result[0], nome_completo=result[1], email=result[2],
                        data_nascimento=result[3], cpf=result[4],
                        telefone=result[5], tipo_cliente=result[6])
        return None

    @classmethod
    def email_exists(cls, email: str) -> bool:
        result = cls.execute_query(
            "SELECT EXISTS(SELECT 1 FROM Cliente WHERE email = %s)",
            (email.lower(),), fetch_one=True
        )
        return result[0] if result else False

    @classmethod
    def cpf_exists(cls, cpf: str) -> bool:
        result = cls.execute_query(
            "SELECT EXISTS(SELECT 1 FROM Cliente WHERE cpf = %s)",
            (cpf,), fetch_one=True
        )
        return result[0] if result else False

    @classmethod
    def create(cls, nome, email, senha_hash, cpf, telefone, tipo, data_nascimento=None) -> int:
        if cls.email_exists(email):
            raise DuplicateError("Email já cadastrado")
        if cls.cpf_exists(cpf):
            raise DuplicateError("CPF já cadastrado")
        result = cls.execute_query(
            "INSERT INTO Cliente (nome_completo,email,senha,data_nascimento,telefone,tipo_cliente,cpf) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (nome, email.lower(), senha_hash, data_nascimento, telefone, tipo, cpf),
            fetch_one=True, commit=True
        )
        return result[0] if result else None

    @classmethod
    def update_password(cls, user_id: int, new_password_hash: str) -> bool:
        rows = cls.execute_query(
            "UPDATE Cliente SET senha = %s WHERE id = %s",
            (new_password_hash, user_id), commit=True
        )
        return rows > 0


    @classmethod
    def get_by_condominio(cls, cond_id: int) -> list:
        """
        Retorna todos os usuarios (moradores) vinculados a um condominio
        via tabela Planos. Inclui nome, email, telefone, tipo e plano.
        """
        query = """
            SELECT DISTINCT
                c.id, c.nome_completo, c.email, c.cpf,
                c.telefone, c.tipo_cliente, c.data_nascimento,
                p.tipo_plano, p.valor, p.data_inicio
            FROM Cliente c
            INNER JOIN Planos p ON p.cliente_id = c.id
            WHERE p.condominio_id = %s
            ORDER BY c.nome_completo
        """
        results = cls.execute_query(query, (cond_id,), fetch_all=True)
        moradores = []
        for row in results:
            moradores.append({
                'id':            row[0],
                'nome_completo': row[1],
                'email':         row[2],
                'cpf':           row[3],
                'telefone':      row[4],
                'tipo_cliente':  row[5],
                'data_nascimento': row[6].isoformat() if row[6] else None,
                'tipo_plano':    row[7],
                'valor_plano':   float(row[8]) if row[8] else None,
                'data_inicio':   row[9].isoformat() if row[9] else None,
            })
        return moradores

    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        queries = [
            ("DELETE FROM Planos WHERE cliente_id = %s", (user_id,)),
            ("DELETE FROM Registro_Manutencao WHERE solicitante_id = %s", (user_id,)),
            ("DELETE FROM Condominios WHERE responsavel_manutencao = %s", (user_id,)),
            ("DELETE FROM Cliente WHERE id = %s", (user_id,))
        ]
        try:
            for query, params in queries:
                cls.execute_query(query, params, commit=True)
            return True
        except Exception as e:
            print(f"Erro ao deletar usuário: {e}")
            return False
