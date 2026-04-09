"""
Modelo de Manutenção
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Manutencao:
    id: Optional[int]
    condominio_id: int
    nome_manutencao: str
    tipo_manutencao: str
    data_solicitacao: date
    status: str
    solicitante_id: int
    custo_estimado: Optional[float] = None
    prestador_servico: Optional[str] = None
    obrigacoes_condominio: Optional[str] = None
    grau_urgencia: Optional[str] = None
    solicitante: Optional[str] = None

    @property
    def status_cor(self) -> str:
        cores = {'pendente': '#FF9800', 'em andamento': '#2196F3', 'concluída': '#4CAF50'}
        return cores.get(self.status.lower(), '#9E9E9E')

    @property
    def urgencia_cor(self) -> str:
        cores = {'baixa': '#4CAF50', 'média': '#FF9800', 'alta': '#FF5722', 'crítica': '#F44336'}
        return cores.get(self.grau_urgencia.lower() if self.grau_urgencia else 'média', '#9E9E9E')

    @property
    def is_urgente(self) -> bool:
        return self.grau_urgencia and self.grau_urgencia.lower() in ['alta', 'crítica']

    @property
    def descricao_resumida(self) -> str:
        if not self.obrigacoes_condominio:
            return "Sem descrição"
        if len(self.obrigacoes_condominio) > 100:
            return self.obrigacoes_condominio[:97] + "..."
        return self.obrigacoes_condominio

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'condominio_id': self.condominio_id,
            'nome_manutencao': self.nome_manutencao,
            'tipo_manutencao': self.tipo_manutencao,
            'data_solicitacao': self.data_solicitacao,
            'custo_estimado': self.custo_estimado,
            'prestador_servico': self.prestador_servico,
            'obrigacoes_condominio': self.obrigacoes_condominio,
            'grau_urgencia': self.grau_urgencia,
            'status': self.status,
            'solicitante_id': self.solicitante_id,
            'solicitante': self.solicitante
        }
