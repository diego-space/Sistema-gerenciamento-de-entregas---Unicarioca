from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


# Instância única (será inicializada no app.py)
db = SQLAlchemy()


# -------------------- FUNCIONÁRIO --------------------
class Funcionario(UserMixin, db.Model):
    __tablename__ = "cad_funcionario"
    """
    Representa os funcionários do condomínio (porteiros, administradores).
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Funcionario {self.email}>"




# -------------------- INQUILINO --------------------
class Inquilino(db.Model):
    __tablename__ = "cad_inquilino"

    ID_morador = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nome_morador = db.Column(db.String(80))
    Telefone = db.Column(db.String(13))
    Email = db.Column(db.String(80))
    Apartamento = db.Column(db.String(10))
    Bloco = db.Column(db.String(10))

    entregas = db.relationship("Entrega", backref="morador", lazy=True, foreign_keys="Entrega.ID_morador")

    def __repr__(self):
        return f"<Inquilino {self.Nome_morador}>"

# -------------------- ECOMMERCE --------------------

class Ecommerce(db.Model):
    __tablename__ = "cad_ecommerce"

    ID_loja = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nome_loja = db.Column(db.String(50))

    def __repr__(self):
        return f"<Loja {self.Nome_loja}>"



# -------------------- ENTREGA --------------------
class Entrega(db.Model):
    __tablename__ = "cad_entregas"

    ID_entrega = db.Column(db.Integer, primary_key=True, autoincrement=True)

    ID_morador = db.Column(db.Integer, db.ForeignKey("cad_inquilino.ID_morador"))
    Nome_morador = db.Column(db.String(80))
    Codigo_produto = db.Column(db.String(45))
    Observacao = db.Column(db.String(250))
    Quantidade = db.Column(db.Integer)
    Status = db.Column(db.String(45))
    PIN = db.Column(db.String(6))
    Data_recebimento = db.Column(db.DateTime)
    Data_retirada = db.Column(db.DateTime)

    ID_loja = db.Column(db.Integer, db.ForeignKey("cad_ecommerce.ID_loja"))
    Nome_loja = db.Column(db.String(45))

    loja = db.relationship("Ecommerce", backref="entregas", lazy=True)

    def __repr__(self):
        return f"<Entrega {self.ID_entrega}>"
    

# ================================
#  Integração com Flask-Login
# ================================
def set_login_manager(lm):
    """
    Registra o user_loader no LoginManager passado (lm).
    Deve ser chamado a partir do app.py *depois* de lm.init_app(app).
    """
    global login_manager
    login_manager = lm

    # define a função de carregamento do usuário e registra no LoginManager
    def load_user(user_id):
        try:
            return Funcionario.query.get(int(user_id))
        except Exception:
            return None

    # registra explicitamente (evita problemas com decorator/escopo)
    login_manager.user_loader(load_user)
