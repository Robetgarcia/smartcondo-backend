"""
Formatadores de dados
"""
from datetime import datetime, date


class Formatter:

    @staticmethod
    def format_cpf(cpf: str) -> str:
        cpf = cpf.replace('.', '').replace('-', '')
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

    @staticmethod
    def format_telefone(telefone: str) -> str:
        telefone = telefone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"

    @staticmethod
    def format_currency(value: float) -> str:
        formatted = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"R$ {formatted}"

    @staticmethod
    def format_date(date_obj: date, format: str = "%d/%m/%Y") -> str:
        if date_obj is None:
            return "Não informado"
        return date_obj.strftime(format)

    @staticmethod
    def format_datetime(datetime_obj: datetime, format: str = "%d/%m/%Y %H:%M") -> str:
        if datetime_obj is None:
            return "Não informado"
        return datetime_obj.strftime(format)

    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        if text is None or len(text) <= max_length:
            return text or ""
        return text[:max_length - len(suffix)] + suffix
