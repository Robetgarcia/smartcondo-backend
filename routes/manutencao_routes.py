"""
Rotas de Manutenção
"""
from flask import Blueprint, request, jsonify
from services.manutencao_service import ManutencaoService
from core.formatters import Formatter

manutencao_bp = Blueprint('manutencoes', __name__)


def _serializar(m) -> dict:
    d = m.to_dict()
    if d.get('data_solicitacao'):
        d['data_solicitacao'] = d['data_solicitacao'].isoformat()
    d['status_cor']      = m.status_cor
    d['urgencia_cor']    = m.urgencia_cor
    d['is_urgente']      = m.is_urgente
    d['custo_formatado'] = Formatter.format_currency(m.custo_estimado) if m.custo_estimado else None
    return d


@manutencao_bp.route('/manutencoes', methods=['GET'])
def listar_manutencoes():
    user_id = request.args.get('user_id', type=int)
    cond_id = request.args.get('cond_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    if cond_id:
        manutencoes, error = ManutencaoService.get_by_condominio(cond_id, user_id)
        if error:
            return jsonify({"success": False, "error": error}), 400
    else:
        manutencoes = ManutencaoService.get_all_user_manutencoes(user_id)
    return jsonify({"success": True, "data": [_serializar(m) for m in manutencoes]}), 200


@manutencao_bp.route('/manutencoes', methods=['POST'])
def criar_manutencao():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    for campo in ['cond_id', 'user_id', 'nome', 'tipo', 'data_solicitacao', 'status']:
        if data.get(campo) is None:
            return jsonify({"success": False, "error": f"Campo '{campo}' é obrigatório"}), 400
    manut_id, error = ManutencaoService.create_manutencao(
        cond_id=int(data['cond_id']), user_id=int(data['user_id']),
        nome=data['nome'], tipo=data['tipo'],
        data_solicitacao=data['data_solicitacao'], status=data['status'],
        custo=str(data['custo']) if data.get('custo') else None,
        prestador=data.get('prestador'), descricao=data.get('descricao'),
        urgencia=data.get('urgencia')
    )
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "data": {"id": manut_id}}), 201


@manutencao_bp.route('/manutencoes/statistics', methods=['GET'])
def estatisticas_manutencoes():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    return jsonify({"success": True, "data": ManutencaoService.get_statistics(user_id)}), 200


@manutencao_bp.route('/manutencoes/recent', methods=['GET'])
def manutencoes_recentes():
    user_id = request.args.get('user_id', type=int)
    limit   = request.args.get('limit', default=5, type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    manutencoes = ManutencaoService.get_recent(user_id, limit)
    return jsonify({"success": True, "data": [_serializar(m) for m in manutencoes]}), 200


@manutencao_bp.route('/manutencoes/<int:manut_id>/status', methods=['PATCH'])
def atualizar_status(manut_id):
    data        = request.get_json()
    novo_status = data.get('status') if data else None
    if not novo_status:
        return jsonify({"success": False, "error": "Campo 'status' é obrigatório"}), 400
    success, error = ManutencaoService.update_status(manut_id, novo_status)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Status atualizado"}), 200


@manutencao_bp.route('/manutencoes/<int:manut_id>', methods=['DELETE'])
def deletar_manutencao(manut_id):
    success, error = ManutencaoService.delete_manutencao(manut_id)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Manutenção deletada"}), 200
