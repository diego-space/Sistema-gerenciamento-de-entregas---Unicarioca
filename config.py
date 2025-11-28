import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Configurações gerais da aplicação Flask."""

    # 🔐 Chave secreta usada para sessões e cookies
    SECRET_KEY = os.getenv("SECRET_KEY", "chave_padrao_mude_para_producao")

    # ----------------------
    # 🗄️ BANCO DE DADOS (somente MySQL)
    # ----------------------
    #
    # O .env DEVE conter algo assim:
    # DATABASE_URL=mysql+pymysql://root:SENHA@localhost:3306/sistema_portaria
    #
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError(
            "❌ ERRO: A variável DATABASE_URL não está definida no .env.\n"
            "Exemplo válido:\n"
            "DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/sistema_portaria"
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----------------------
    # ⚙️ DEPURAÇÃO
    # ----------------------
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # ----------------------
    # 🔔 API DE WHATSAPP
    # ----------------------
    WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
    WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
    WHATSAPP_INSTANCE = os.getenv("WHATSAPP_INSTANCE")
