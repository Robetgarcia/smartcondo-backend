"""
Rotas de Autenticação
POST /auth/login
POST /auth/register
POST /auth/reset-password
POST /auth/change-password
"""
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    email = data.get('email', '').strip()
    senha = data.get('senha', '')
    if not email or not senha:
        return jsonify({"success": False, "error": "Email e senha são obrigatórios"}), 400
    user_id, error = AuthService.login(email, senha)
    if error:
        return jsonify({"success": False, "error": error}), 401
    return jsonify({"success": True, "data": {"user_id": user_id}}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    for campo in ['nome', 'email', 'senha', 'confirmar_senha', 'cpf', 'telefone', 'tipo']:
        if not data.get(campo):
            return jsonify({"success": False, "error": f"Campo '{campo}' é obrigatório"}), 400
    user_id, error = AuthService.register(
        nome=data['nome'], email=data['email'], senha=data['senha'],
        confirmar_senha=data['confirmar_senha'], cpf=data['cpf'],
        telefone=data['telefone'], tipo=data['tipo'],
        data_nascimento=data.get('data_nascimento')
    )
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "data": {"user_id": user_id}}), 201


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    email      = data.get('email', '').strip()
    nova_senha = data.get('nova_senha', '')
    confirmar  = data.get('confirmar_senha', '')
    if not email or not nova_senha or not confirmar:
        return jsonify({"success": False, "error": "Todos os campos são obrigatórios"}), 400
    success, error = AuthService.reset_password(email, nova_senha, confirmar)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Senha redefinida com sucesso"}), 200


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400
    user_id    = data.get('user_id')
    nova_senha = data.get('nova_senha', '')
    confirmar  = data.get('confirmar_senha', '')
    if not user_id or not nova_senha or not confirmar:
        return jsonify({"success": False, "error": "Todos os campos são obrigatórios"}), 400
    success, error = AuthService.change_password(int(user_id), nova_senha, confirmar)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Senha alterada com sucesso"}), 200
