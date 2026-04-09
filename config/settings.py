"""
Configurações centralizadas do backend
"""
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

DATABASE = {
    'host':     config('DB_HOST',     default='localhost'),
    'port':     config('DB_PORT',     default=5432, cast=int),
    'database': config('DB_NAME',     default='BancoSmartCondo'),
    'user':     config('DB_USER',     default='postgres'),
    'password': config('DB_PASSWORD')
}

APP_NAME    = config('APP_NAME',    default='SmartCondo')
APP_VERSION = config('APP_VERSION', default='2.0.0')
DEBUG       = config('DEBUG',       default=False, cast=bool)
SECRET_KEY  = config('SECRET_KEY',  default='change-me-in-production')

PASSWORD_MIN_LENGTH = 6
CPF_LENGTH          = 11
TELEFONE_LENGTH     = 11
CNPJ_LENGTH         = 14
