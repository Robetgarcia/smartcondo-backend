"""
Rotas de Residências
POST /residencias              — vincula morador ao condomínio
GET  /residencias/cliente/<id> — onde o cliente mora
GET  /condominios/<id>/moradores — moradores de um condomínio (já existia, agora usa Residencias)
DELETE /residencias/<id>       — remove vínculo
"""
from flask import Blueprint, request, jsonify
from services.residencia_service import ResidenciaService

residencia_bp = Blueprint('residencias', __name__)


@residencia_bp.route('/residencias', methods=['POST'])
def vincular_morador():
    """
    Vincula morador a um condomínio.
    Body: {
        "cliente_id", "condominio_nome", "condominio_cnpj",
        "numero_unidade", "bloco" (opcional)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400

    for campo in ['cliente_id', 'condominio_nome', 'condominio_cnpj', 'numero_unidade']:
        if not data.get(campo):
            return jsonify({"success": False,
                            "error": f"Campo '{campo}' é obrigatório"}), 400

    res_id, error = ResidenciaService.vincular_morador(
        cliente_id=int(data['cliente_id']),
        condominio_nome=data['condominio_nome'],
        condominio_cnpj=data['condominio_cnpj'],
        numero_unidade=data['numero_unidade'],
        bloco=data.get('bloco')
    )

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({"success": True, "data": {"residencia_id": res_id}}), 201


@residencia_bp.route('/residencias/cliente/<int:cliente_id>', methods=['GET'])
def get_residencia_cliente(cliente_id):
    """Retorna onde o cliente mora."""
    residencia = ResidenciaService.get_residencia_cliente(cliente_id)
    if not residencia:
        return jsonify({"success": False,
                        "error": "Nenhuma residência cadastrada"}), 404
    return jsonify({"success": True, "data": residencia}), 200


@residencia_bp.route('/condominios/<int:cond_id>/moradores', methods=['GET'])
def listar_moradores(cond_id):
    """
    Lista moradores de um condomínio via tabela Residencias.
    Query: ?user_id=X
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"success": False,
                        "error": "Parâmetro 'user_id' é obrigatório"}), 400

    moradores = ResidenciaService.get_moradores_condominio(cond_id)
    return jsonify({
        "success": True,
        "data":    moradores,
        "total":   len(moradores)
    }), 200




@residencia_bp.route('/usuarios/buscar', methods=['GET'])
def buscar_usuario():
    """
    Busca usuário por email para o síndico localizar o morador.
    Query: ?email=fulano@email.com
    """
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'error': 'Email é obrigatório'}), 400

    user = ResidenciaService.buscar_usuario_por_email(email)
    if not user:
        return jsonify({'success': False,
                        'error': 'Nenhum usuário encontrado com este email'}), 404
    return jsonify({'success': True, 'data': user}), 200


@residencia_bp.route('/residencias/por-id', methods=['POST'])
def vincular_por_id():
    """
    Síndico adiciona morador diretamente pelo ID do condomínio.
    Body: { "cliente_id", "condominio_id", "numero_unidade", "bloco"(opt) }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Body JSON ausente'}), 400

    for campo in ['cliente_id', 'condominio_id', 'numero_unidade']:
        if not data.get(campo):
            return jsonify({'success': False,
                            'error': f"Campo '{campo}' é obrigatório"}), 400

    res_id, error = ResidenciaService.vincular_por_id(
        cliente_id=int(data['cliente_id']),
        condominio_id=int(data['condominio_id']),
        numero_unidade=data['numero_unidade'],
        bloco=data.get('bloco')
    )

    if error:
        return jsonify({'success': False, 'error': error}), 400
    return jsonify({'success': True, 'data': {'residencia_id': res_id}}), 201

@residencia_bp.route('/residencias/<int:res_id>', methods=['DELETE'])
def remover_morador(res_id):
    """Remove (inativa) vínculo de um morador."""
    success, error = ResidenciaService.remover_morador(res_id)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True,
                    "message": "Morador removido do condomínio"}), 200
