"""
Rotas de Condomínio e Usuário
"""
from flask import Blueprint, request, jsonify
from services.condominio_service import CondominioService
from repositories.user_repository import UserRepository
from core.formatters import Formatter

condominio_bp = Blueprint('condominios', __name__)


@condominio_bp.route('/usuarios/<int:user_id>', methods=['GET'])
def get_usuario(user_id):
    user = UserRepository.get_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404
    return jsonify({"success": True, "data": user.to_dict()}), 200


@condominio_bp.route('/condominios', methods=['GET'])
def listar_condominios():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    condominios = CondominioService.get_user_condominios(user_id)
    data = []
    for c in condominios:
        d = c.to_dict()
        try:
            d['cnpj_formatado'] = Formatter.format_cnpj(c.cnpj)
        except Exception:
            d['cnpj_formatado'] = c.cnpj
        if d.get('data_fundacao'):
            d['data_fundacao'] = d['data_fundacao'].isoformat()
        data.append(d)
    return jsonify({"success": True, "data": data}), 200


@condominio_bp.route('/condominios', methods=['POST'])
def criar_condominio():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    for campo in ['nome', 'endereco', 'cnpj', 'tipo', 'blocos', 'unidades', 'data_fundacao', 'user_id']:
        if data.get(campo) is None:
            return jsonify({"success": False, "error": f"Campo '{campo}' é obrigatório"}), 400
    cond_id, error = CondominioService.create_condominio(
        nome=data['nome'], endereco=data['endereco'], cnpj=data['cnpj'],
        tipo=data['tipo'], blocos=str(data['blocos']), unidades=str(data['unidades']),
        data_fundacao=data['data_fundacao'], user_id=int(data['user_id'])
    )
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "data": {"id": cond_id}}), 201


@condominio_bp.route('/condominios/statistics', methods=['GET'])
def estatisticas_condominios():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    return jsonify({"success": True, "data": CondominioService.get_statistics(user_id)}), 200


@condominio_bp.route('/condominios/login', methods=['POST'])
def login_condominio():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    nome    = data.get('nome', '').strip()
    cnpj    = data.get('cnpj', '').strip()
    user_id = data.get('user_id')
    if not nome or not cnpj or not user_id:
        return jsonify({"success": False, "error": "nome, cnpj e user_id são obrigatórios"}), 400
    cond_id, error = CondominioService.login_condominio(nome, cnpj, int(user_id))
    if error:
        return jsonify({"success": False, "error": error}), 404
    return jsonify({"success": True, "data": {"id": cond_id}}), 200


@condominio_bp.route('/condominios/<int:cond_id>/hide', methods=['PATCH'])
def ocultar_condominio(cond_id):
    data    = request.get_json()
    user_id = data.get('user_id') if data else None
    if not user_id:
        return jsonify({"success": False, "error": "user_id é obrigatório"}), 400
    success, error = CondominioService.hide_condominio(cond_id, int(user_id))
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Condomínio ocultado"}), 200


@condominio_bp.route('/condominios/<int:cond_id>', methods=['DELETE'])
def deletar_condominio(cond_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    success, error = CondominioService.delete_condominio(cond_id, user_id)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Condomínio deletado permanentemente"}), 200
