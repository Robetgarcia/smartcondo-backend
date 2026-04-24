"""
SmartCondo Backend — Ponto de entrada da API Flask

Desenvolvimento:  python run_api.py
Produção:         gunicorn run_api:app
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.condominio_routes import condominio_bp
from routes.manutencao_routes import manutencao_bp
from routes.residencia_routes import residencia_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins="*")   # Em produção: origins=["https://meu-frontend.com"]

    app.register_blueprint(auth_bp)
    app.register_blueprint(condominio_bp)
    app.register_blueprint(manutencao_bp)
    app.register_blueprint(residencia_bp)    # /residencias/*

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "app": "SmartCondo API", "version": "1.0.0"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Rota não encontrada"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Método HTTP não permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Erro interno no servidor"}), 500

    return app


app = create_app()

if __name__ == '__main__':
    print("🚀 SmartCondo API iniciando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
