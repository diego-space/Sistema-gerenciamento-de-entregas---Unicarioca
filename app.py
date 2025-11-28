import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_login import LoginManager
from config import Config



# Inicializa extensões
from models import db
login_manager = LoginManager()

def create_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    print("🟢 SID carregado:", os.getenv("TWILIO_ACCOUNT_SID"))
    print("🟢 TOKEN carregado:", os.getenv("TWILIO_AUTH_TOKEN"))


    # Inicializa banco e login
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Importa models
    from models import Funcionario, Inquilino, Entrega, Ecommerce, set_login_manager

    set_login_manager(login_manager)
    # ---- USER LOADER (obrigatório!) ----
    # USER LOADER fica aqui (único lugar!)
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return Funcionario.query.get(int(user_id))
        except:
            return None
    # ------------------------------------
    # Importa routes
    from routes import init_routes
    init_routes(app)


    return app


# -------------------- EXECUÇÃO --------------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])