"""
Service de Autenticação
"""
import bcrypt
from typing import Optional, Tuple
from repositories.user_repository import UserRepository
from core.validators import Validator
from core.formatters import Formatter
from core.exceptions import ValidationError, DuplicateError


class AuthService:

    @staticmethod
    def login(email: str, senha: str) -> Tuple[Optional[int], Optional[str]]:
        try:
            email = Validator.validate_email(email)
            user = UserRepository.find_by_email(email)
            if not user:
                return None, "Email não encontrado"
            user_id, senha_hash = user
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                return user_id, None
            return None, "Senha incorreta"
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao fazer login: {e}"

    @staticmethod
    def register(nome, email, senha, confirmar_senha, cpf, telefone,
                 tipo, data_nascimento=None) -> Tuple[Optional[int], Optional[str]]:
        try:
            nome  = Validator.validate_not_empty(nome, "Nome completo")
            email = Validator.validate_email(email)
            senha = Validator.validate_password(senha)
            if senha != confirmar_senha:
                return None, "As senhas não coincidem"
            cpf      = Validator.validate_cpf(cpf)
            telefone = Validator.validate_telefone(telefone)
            cpf_fmt  = Formatter.format_cpf(cpf)
            tel_fmt  = Formatter.format_telefone(telefone)
            data_nasc = None
            if data_nascimento:
                data_nasc = Validator.validate_date(data_nascimento).date()
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_id = UserRepository.create(
                nome=nome, email=email, senha_hash=senha_hash,
                cpf=cpf_fmt, telefone=tel_fmt, tipo=tipo, data_nascimento=data_nasc
            )
            return user_id, None
        except ValidationError as e:
            return None, str(e)
        except DuplicateError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao cadastrar: {e}"

    @staticmethod
    def change_password(user_id: int, nova_senha: str, confirmar_senha: str) -> Tuple[bool, Optional[str]]:
        try:
            nova_senha = Validator.validate_password(nova_senha)
            if nova_senha != confirmar_senha:
                return False, "As senhas não coincidem"
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if UserRepository.update_password(user_id, senha_hash):
                return True, None
            return False, "Erro ao atualizar senha"
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro: {e}"

    @staticmethod
    def reset_password(email: str, nova_senha: str, confirmar_senha: str) -> Tuple[bool, Optional[str]]:
        try:
            email = Validator.validate_email(email)
            user  = UserRepository.find_by_email(email)
            if not user:
                return False, "Email não encontrado"
            return AuthService.change_password(user[0], nova_senha, confirmar_senha)
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro: {e}"
