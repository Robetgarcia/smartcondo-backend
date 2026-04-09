"""
Validadores centralizados
"""
import re
from datetime import datetime
from core.exceptions import ValidationError
from config.settings import PASSWORD_MIN_LENGTH, CPF_LENGTH, TELEFONE_LENGTH, CNPJ_LENGTH


class Validator:

    @staticmethod
    def validate_email(email: str) -> str:
        email = email.strip()
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Email inválido")
        return email

    @staticmethod
    def validate_cpf(cpf: str) -> str:
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != CPF_LENGTH:
            raise ValidationError(f"CPF deve ter exatamente {CPF_LENGTH} dígitos")
        return cpf

    @staticmethod
    def validate_cnpj(cnpj: str) -> str:
        cnpj = re.sub(r'\D', '', cnpj)
        if len(cnpj) != CNPJ_LENGTH:
            raise ValidationError(f"CNPJ deve ter exatamente {CNPJ_LENGTH} dígitos")
        return cnpj

    @staticmethod
    def validate_telefone(telefone: str) -> str:
        telefone = re.sub(r'\D', '', telefone)
        if len(telefone) != TELEFONE_LENGTH:
            raise ValidationError(f"Telefone deve ter {TELEFONE_LENGTH} dígitos (DDD + número)")
        return telefone

    @staticmethod
    def validate_password(password: str) -> str:
        if len(password) < PASSWORD_MIN_LENGTH:
            raise ValidationError(f"Senha deve ter no mínimo {PASSWORD_MIN_LENGTH} caracteres")
        return password

    @staticmethod
    def validate_date(date_str: str, format: str = "%d/%m/%Y") -> datetime:
        try:
            return datetime.strptime(date_str, format)
        except ValueError:
            raise ValidationError(f"Data inválida. Use o formato {format}")

    @staticmethod
    def validate_not_empty(value: str, field_name: str = "Campo") -> str:
        value = value.strip()
        if not value:
            raise ValidationError(f"{field_name} é obrigatório")
        return value

    @staticmethod
    def validate_positive_number(value: str, field_name: str = "Valor") -> float:
        try:
            num = float(value.replace(',', '.'))
            if num < 0:
                raise ValueError
            return num
        except ValueError:
            raise ValidationError(f"{field_name} deve ser um número positivo")

    @staticmethod
    def validate_positive_integer(value: str, field_name: str = "Valor") -> int:
        try:
            num = int(value)
            if num <= 0:
                raise ValueError
            return num
        except ValueError:
            raise ValidationError(f"{field_name} deve ser um número inteiro positivo")
