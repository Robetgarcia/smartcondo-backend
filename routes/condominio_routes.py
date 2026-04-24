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


@condominio_bp.route('/usuarios/<int:user_id>', methods=['DELETE'])
def deletar_usuario(user_id):
    """Deleta conta do usuario e todos os dados relacionados"""
    success = UserRepository.delete_user(user_id)
    if success:
        return jsonify({"success": True, "message": "Conta deletada permanentemente"}), 200
    return jsonify({"success": False, "error": "Erro ao deletar conta"}), 400


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

@condominio_bp.route('/condominios/<int:cond_id>/statistics', methods=['GET'])
def estatisticas_condominio(cond_id):
    """
    Estatisticas de um condominio especifico (manutencoes + info geral).
    Query: ?user_id=X
    """
    from services.manutencao_service import ManutencaoService
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'success': False, 'error': "Parametro 'user_id' e obrigatorio"}), 400

    cond, error = CondominioService.get_condominio(cond_id, user_id)
    if error:
        return jsonify({'success': False, 'error': error}), 403

    manut_stats = ManutencaoService.get_statistics(user_id, cond_id)

    return jsonify({'success': True, 'data': {
        'condominio': {
            'id':   cond.id,
            'nome': cond.nome_condominio,
            'tipo': cond.tipo_condominio,
            'blocos':   cond.quantidade_blocos,
            'unidades': cond.quantidade_unidades,
        },
        'manutencoes': manut_stats
    }}), 200

@condominio_bp.route('/condominios/<int:cond_id>', methods=['DELETE'])
def deletar_condominio(cond_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400
    success, error = CondominioService.delete_condominio(cond_id, user_id)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Condomínio deletado permanentemente"}), 200


# ── Moradores ─────────────────────────────────────────────────────────────────
from core.exceptions import DuplicateError

@condominio_bp.route('/condominios/<int:cond_id>/moradores', methods=['GET'])
def listar_moradores(cond_id):
    """Lista todos os moradores de um condomínio"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "user_id é obrigatório"}), 400
    from repositories.condominio_repository import CondominioRepository
    if not CondominioRepository.verify_ownership(cond_id, user_id):
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    moradores = MoradoresRepository.get_by_condominio(cond_id)
    return jsonify({"success": True, "data": moradores}), 200


@condominio_bp.route('/condominios/<int:cond_id>/moradores/buscar', methods=['GET'])
def buscar_usuario_por_email(cond_id):
    """Busca um usuário por email para adicionar como morador"""
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({"success": False, "error": "email é obrigatório"}), 400
    usuario = MoradoresRepository.buscar_por_email(email)
    if not usuario:
        return jsonify({"success": False, "error": "Nenhum usuário encontrado com este email"}), 404
    return jsonify({"success": True, "data": usuario}), 200


@condominio_bp.route('/condominios/<int:cond_id>/moradores', methods=['POST'])
def adicionar_morador(cond_id):
    """
    Adiciona morador ao condomínio
    Body: { "cliente_id": X, "unidade": "Apto 201", "user_id": Y }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    cliente_id = data.get('cliente_id')
    user_id    = data.get('user_id')
    unidade    = data.get('unidade', '').strip() or None
    if not cliente_id or not user_id:
        return jsonify({"success": False, "error": "cliente_id e user_id são obrigatórios"}), 400
    from repositories.condominio_repository import CondominioRepository
    if not CondominioRepository.verify_ownership(cond_id, int(user_id)):
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    try:
        morador_id = MoradoresRepository.adicionar(cond_id, int(cliente_id), unidade)
        return jsonify({"success": True, "data": {"id": morador_id}}), 201
    except DuplicateError as e:
        return jsonify({"success": False, "error": str(e)}), 409
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro: {e}"}), 400


@condominio_bp.route('/condominios/<int:cond_id>/moradores/<int:morador_id>', methods=['DELETE'])
def remover_morador(cond_id, morador_id):
    """Remove morador do condomínio"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False, "error": "user_id é obrigatório"}), 400
    from repositories.condominio_repository import CondominioRepository
    if not CondominioRepository.verify_ownership(cond_id, user_id):
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    success = MoradoresRepository.remover(morador_id)
    if success:
        return jsonify({"success": True, "message": "Morador removido"}), 200
    return jsonify({"success": False, "error": "Registro não encontrado"}), 404
