"""
Modelo de Usuário
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    nome_completo: str
    email: str
    cpf: str
    telefone: str
    tipo_cliente: str
    data_nascimento: Optional[date] = None
    senha: Optional[str] = None

    def __post_init__(self):
        self.email = self.email.lower().strip()

    @property
    def primeiro_nome(self) -> str:
        return self.nome_completo.split()[0]

    @property
    def is_admin(self) -> bool:
        return self.tipo_cliente.lower() == "administrador"

    @property
    def is_sindico(self) -> bool:
        return self.tipo_cliente.lower() == "sindico"

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'email': self.email,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'tipo_cliente': self.tipo_cliente,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None
        }
