"""
Rotas de Residências e Moradores
CORRIGIDO - Todas as rotas de gerenciamento de moradores
"""
from flask import Blueprint, request, jsonify
from services.residencia_service import ResidenciaService
from repositories.condominio_repository import CondominioRepository
from config.database import db

residencia_bp = Blueprint('residencias', __name__)


# ── Diagnóstico ───────────────────────────────────────────────────────────────

@residencia_bp.route('/diagnostico/residencias', methods=['GET'])
def diagnostico():
    """
    Rota de diagnóstico — verifica se a tabela Residencias existe
    e quantos registros tem. Acesse no navegador para debugar.
    """
    try:
        with db.get_cursor() as cursor:
            # Verifica se a tabela existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'residencias'
                )
            """)
            tabela_existe = cursor.fetchone()[0]

        if not tabela_existe:
            return jsonify({
                "tabela_existe": False,
                "erro": "A tabela 'Residencias' NAO existe no banco. Execute o SQL de migração no Neon.",
                "sql": (
                    "CREATE TABLE Residencias ("
                    "id SERIAL PRIMARY KEY, "
                    "cliente_id INT NOT NULL REFERENCES Cliente(id) ON DELETE CASCADE, "
                    "condominio_id INT NOT NULL REFERENCES Condominios(id) ON DELETE CASCADE, "
                    "bloco VARCHAR(20), "
                    "numero_unidade VARCHAR(20) NOT NULL, "
                    "data_entrada DATE NOT NULL DEFAULT CURRENT_DATE, "
                    "ativo BOOLEAN NOT NULL DEFAULT TRUE, "
                    "UNIQUE (cliente_id, condominio_id));"
                )
            }), 200

        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Residencias")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM Residencias WHERE ativo = TRUE")
            ativos = cursor.fetchone()[0]

            cursor.execute("""
                SELECT r.id, c.nome_completo, cond.nome_condominio,
                       r.numero_unidade, r.bloco, r.ativo
                FROM Residencias r
                JOIN Cliente c ON c.id = r.cliente_id
                JOIN Condominios cond ON cond.id = r.condominio_id
                ORDER BY r.id DESC LIMIT 10
            """)
            registros = [
                {
                    "id": row[0],
                    "morador": row[1],
                    "condominio": row[2],
                    "unidade": row[3],
                    "bloco": row[4],
                    "ativo": row[5]
                }
                for row in cursor.fetchall()
            ]

        return jsonify({
            "tabela_existe": True,
            "total_registros": total,
            "registros_ativos": ativos,
            "ultimos_10": registros
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ── Vincular por nome+CNPJ (fluxo do morador) ────────────────────────────────

@residencia_bp.route('/residencias', methods=['POST'])
def vincular_morador():
    """
    Morador vincula-se ao condomínio informando nome + CNPJ
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Body JSON ausente"}), 400

    for campo in ['cliente_id', 'condominio_nome', 'condominio_cnpj', 'numero_unidade']:
        if not data.get(campo):
            return jsonify({"success": False,
                            "error": f"Campo '{campo}' é obrigatório"}), 400

    res_id, error = ResidenciaService.vincular_por_nome_cnpj(
        cliente_id=int(data['cliente_id']),
        condominio_nome=data['condominio_nome'],
        condominio_cnpj=data['condominio_cnpj'],
        numero_unidade=data['numero_unidade'],
        bloco=data.get('bloco')
    )

    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "data": {"residencia_id": res_id}}), 201


# ── Vincular por ID (fluxo do síndico) ───────────────────────────────────────

@residencia_bp.route('/residencias/por-id', methods=['POST'])
def vincular_por_id():
    """
    Síndico vincula morador diretamente pelo ID do condomínio
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Body JSON ausente'}), 400

    for campo in ['cliente_id', 'condominio_id', 'numero_unidade']:
        if not data.get(campo):
            return jsonify({'success': False,
                            'error': f"Campo '{campo}' é obrigatório"}), 400

    print(f"[DEBUG VINCULAR] Recebido: {data}")

    res_id, error = ResidenciaService.vincular_por_id(
        cliente_id=int(data['cliente_id']),
        condominio_id=int(data['condominio_id']),
        numero_unidade=data['numero_unidade'],
        bloco=data.get('bloco')
    )

    print(f"[DEBUG VINCULAR] Resultado: res_id={res_id}, error={error}")

    if error:
        return jsonify({'success': False, 'error': error}), 400
    return jsonify({'success': True, 'data': {'residencia_id': res_id}}), 201


# ── Buscar usuário por email ──────────────────────────────────────────────────

@residencia_bp.route('/usuarios/buscar', methods=['GET'])
def buscar_usuario():
    """
    Busca usuário por email para o síndico poder adicionar como morador
    """
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'error': 'Email é obrigatório'}), 400

    user = ResidenciaService.buscar_usuario_por_email(email)
    if not user:
        return jsonify({'success': False,
                        'error': 'Nenhum usuário encontrado com este email'}), 404
    return jsonify({'success': True, 'data': user}), 200


# ── Listar moradores de um condomínio ─────────────────────────────────────────

@residencia_bp.route('/condominios/<int:cond_id>/moradores', methods=['GET'])
def listar_moradores(cond_id):
    """
    Lista todos os moradores ativos de um condomínio
    CORRIGIDO - Agora com verificação de ownership
    """
    user_id = request.args.get('user_id', type=int)
    
    print(f"[DEBUG LISTAGEM] === INÍCIO ===")
    print(f"[DEBUG LISTAGEM] cond_id={cond_id}, user_id={user_id}")
    
    if not user_id:
        print("[DEBUG LISTAGEM] ERRO: user_id ausente")
        return jsonify({"success": False, "error": "Parâmetro 'user_id' é obrigatório"}), 400

    # Verifica se o usuário tem acesso ao condomínio
    ownership = CondominioRepository.verify_ownership(cond_id, user_id)
    print(f"[DEBUG LISTAGEM] verify_ownership = {ownership}")
    
    if not ownership:
        print("[DEBUG LISTAGEM] ERRO: Acesso negado")
        return jsonify({"success": False, "error": "Acesso negado"}), 403

    try:
        moradores = ResidenciaService.get_moradores_condominio(cond_id)
        print(f"[DEBUG LISTAGEM] Moradores retornados: {len(moradores)}")
        
        if moradores:
            print(f"[DEBUG LISTAGEM] Primeiro morador: {moradores[0]}")
        else:
            print("[DEBUG LISTAGEM] Nenhum morador retornado")
        
        print(f"[DEBUG LISTAGEM] === FIM ===\n")
        
        return jsonify({
            "success": True,
            "data": moradores,
            "total": len(moradores)
        }), 200
    except Exception as e:
        print(f"[DEBUG LISTAGEM] EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ── Onde o cliente mora ───────────────────────────────────────────────────────

@residencia_bp.route('/residencias/cliente/<int:cliente_id>', methods=['GET'])
def get_residencia_cliente(cliente_id):
    """
    Retorna informações de onde o cliente mora
    """
    residencia = ResidenciaService.get_residencia_cliente(cliente_id)
    if not residencia:
        return jsonify({"success": False,
                        "error": "Nenhuma residência cadastrada"}), 404
    return jsonify({"success": True, "data": residencia}), 200


# ── Remover vínculo ───────────────────────────────────────────────────────────

@residencia_bp.route('/residencias/<int:res_id>', methods=['DELETE'])
def remover_morador(res_id):
    """
    Remove (inativa) vínculo de um morador com o condomínio
    """
    print(f"[DEBUG REMOVER] residencia_id={res_id}")
    
    success, error = ResidenciaService.remover_morador(res_id)
    
    print(f"[DEBUG REMOVER] Resultado: success={success}, error={error}")
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "message": "Morador removido"}), 200
