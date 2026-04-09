"""
Modelo de Condomínio
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Condominio:
    id: Optional[int]
    nome_condominio: str
    endereco: str
    cnpj: str
    tipo_condominio: str
    quantidade_blocos: int
    quantidade_unidades: int
    responsavel_manutencao: int
    data_fundacao: Optional[date] = None
    area_total: Optional[float] = None
    oculto: bool = False

    @property
    def tipo_emoji(self) -> str:
        emojis = {'comercial': '🏢', 'residencial': '🏘️', 'misto': '🏗️'}
        return emojis.get(self.tipo_condominio.lower(), '🏢')

    @property
    def nome_curto(self) -> str:
        if len(self.nome_condominio) > 30:
            return self.nome_condominio[:27] + "..."
        return self.nome_condominio

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome_condominio': self.nome_condominio,
            'endereco': self.endereco,
            'cnpj': self.cnpj,
            'tipo_condominio': self.tipo_condominio,
            'quantidade_blocos': self.quantidade_blocos,
            'quantidade_unidades': self.quantidade_unidades,
            'data_fundacao': self.data_fundacao,
            'area_total': self.area_total,
            'responsavel_manutencao': self.responsavel_manutencao,
            'oculto': self.oculto
        }
