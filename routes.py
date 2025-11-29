from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

from models import db, Funcionario, Inquilino, Entrega, Ecommerce
from notifications import enviar_whatsapp


def init_routes(app):
    """
    Inicializa todas as rotas da aplicação Flask.
    """

    # -------------------- ROTA RAIZ --------------------
    @app.route("/")
    def home():
        # Redireciona para a tela de login caso não esteja autenticado
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    # -------------------- LOGIN --------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        Rota de login de funcionários.
        Valida e autentica o usuário com base no e-mail e senha.
        """
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            funcionario = Funcionario.query.filter_by(email=email).first()

            ## DEBUG para validar acesso
            print(">>> EMAIL DIGITADO:", email)
            print(">>> SENHA DIGITADA:", senha)
            print(">>> FUNCIONARIO ENCONTRADO:", funcionario)
            if funcionario:
                print(">>> HASH NO BANCO:", funcionario.senha)
                print(">>> CHECK:", check_password_hash(funcionario.senha, senha))

            if funcionario and check_password_hash(funcionario.senha, senha):
                login_user(funcionario)
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("E-mail ou senha inválidos.", "danger")

        return render_template("login.html")

    # -------------------- LOGOUT --------------------
    @app.route("/logout")
    @login_required
    def logout():
        """
        Faz logout do funcionário e redireciona para a tela de login.
        """
        logout_user()
        flash("Logout realizado com sucesso!", "info")
        return redirect(url_for("login"))

    # -------------------- DASHBOARD --------------------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        """
        Página principal do sistema (painel).
        """
        total_inquilinos = Inquilino.query.count()
        total_entregas = Entrega.query.count()
        return render_template(
            "dashboard.html",
            total_inquilinos=total_inquilinos,
            total_entregas=total_entregas
        )

    # -------------------- CADASTRAR FUNCIONÁRIO --------------------
    @app.route("/registrar-funcionario", methods=["GET", "POST"])
    @login_required
    def registrar_funcionario():
        """
        Cadastra novos funcionários (pode ser restrito ao admin).
        """
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            if Funcionario.query.filter_by(email=email).first():
                flash("Este e-mail já está cadastrado.", "warning")
                return redirect(url_for("registrar_funcionario"))

            novo = Funcionario(email=email, senha=generate_password_hash(senha))
            db.session.add(novo)
            db.session.commit()

            flash("Funcionário cadastrado com sucesso!", "success")
            return redirect(url_for("dashboard"))

        return render_template("registrar_funcionario.html")

    # -------------------- CADASTRO DE INQUILINO --------------------
    @app.route("/inquilino", methods=["GET", "POST"])
    @login_required
    def cadastrar_inquilino():
        """
        Cadastra novos inquilinos com nome, telefone, bloco e apartamento.
        """
        if request.method == "POST":
            Nome_morador = request.form.get("nome")
            telefone_raw = request.form.get("telefone", "").strip()
            Email = request.form.get("email")
            Bloco = request.form.get("bloco")
            Apartamento = request.form.get("apartamento")

            # ----------- TRATAMENTO DO TELEFONE -----------
            # remove caracteres não numéricos
            telefone_numerico = "".join(filter(str.isdigit, telefone_raw))

            # adiciona 55 se não começar com 55
            if not telefone_numerico.startswith("55"):
                telefone_numerico = "55" + telefone_numerico

            Telefone = telefone_numerico
            # ----------------------------------------------

            if not all([Nome_morador, Telefone, Email, Bloco, Apartamento]):
                flash("Preencha todos os campos antes de cadastrar.", "warning")
                return redirect(url_for("cadastrar_inquilino"))

            novo = Inquilino(
                Nome_morador=Nome_morador,
                Telefone=Telefone,
                Email=Email,
                Bloco=Bloco,
                Apartamento=Apartamento
            )
            
            db.session.add(novo)
            db.session.commit()

            flash("Inquilino cadastrado com sucesso!", "success")
            return redirect(url_for("dashboard"))

        return render_template("cadastrar_inquilino.html")

    # -------------------- PESQUISAR INQUILINO --------------------
    @app.route("/pesquisar-inquilino")
    @login_required
    def pesquisar_inquilino():

        bloco = request.args.get("bloco", "")
        apt = request.args.get("apt", "")
        nome = request.args.get("nome_morador", "")

        consulta = Inquilino.query

        if bloco:
            consulta = consulta.filter(Inquilino.Bloco.ilike(f"%{bloco}%"))

        if apt:
            consulta = consulta.filter(Inquilino.Apartamento.ilike(f"%{apt}%"))

        if nome:
            consulta = consulta.filter(Inquilino.Nome_morador.ilike(f"%{nome}%"))

        resultados = consulta.all()

        return render_template(
            "listar_inquilino.html",
            inquilinos=resultados,
            bloco=bloco,
            apt=apt,
            nome_morador=nome
        )
    # -------------------- PESQUISAR ENTREGAS --------------------    
    @app.route("/listar-entregas")
    @login_required
    def pesquisar_entregas():

        pin = request.args.get("pin", "")
        codigo = request.args.get("codigo_produto", "")
        status = request.args.get("status", "")
        nome = request.args.get("nome_morador", "")
        data_receb = request.args.get("data_recebimento", "")

        consulta = Entrega.query  # seu modelo de entregas

        if pin:
            consulta = consulta.filter(Entrega.PIN.ilike(f"%{pin}%"))

        if codigo:
            consulta = consulta.filter(Entrega.Codigo_produto.ilike(f"%{codigo}%"))

        if status:
            consulta = consulta.filter(Entrega.Status.ilike(f"%{status}%"))

        if nome:
            consulta = consulta.filter(Entrega.Nome_morador.ilike(f"%{nome}%"))

        # FILTRO POR DATA — aceita YYYY-MM-DD
        if data_receb:
            try:
                from datetime import datetime
                data_formatada = datetime.strptime(data_receb, "%Y-%m-%d")
                consulta = consulta.filter(
                    db.func.date(Entrega.Data_recebimento) == data_formatada.date()
                )
            except:
                pass

        resultados = consulta.order_by(Entrega.Data_recebimento.desc()).all()

        return render_template(
            "listar_entregas.html",
            entregas=resultados,
            pin=pin,
            codigo_produto=codigo,
            status=status,
            nome_morador=nome,
            data_recebimento=data_receb
        )



    # -------------------- REGISTRO DE ENTREGA --------------------
    @app.route("/entrega", methods=["GET", "POST"])
    @login_required
    def registrar_entrega():

        if request.method == "POST":
            id_morador = request.form.get("inquilino_id")
            codigo_produto = request.form.get("codigo_produto")
            quantidade = request.form.get("quantidade")
            status = request.form.get("status")
            observacao = request.form.get("observacao")
            id_loja = request.form.get("id_loja")

            if not id_morador:
                flash("Selecione um inquilino.", "warning")
                return redirect(url_for("registrar_entrega"))


            # Busca o nome da loja pelo ID
            loja = Ecommerce.query.get(id_loja)
            nome_loja = loja.Nome_loja if loja else None

            # Busca o nome do morador pelo ID
            nome = Inquilino.query.get(id_morador)

            # PIN automático
            pin = str(random.randint(100000, 999999))

            entrega = Entrega(
                ID_morador=id_morador,
                Nome_morador=nome.Nome_morador,
                Codigo_produto=codigo_produto,
                Observacao=observacao,
                Quantidade=quantidade,
                Status=status,
                Data_recebimento=datetime.now(),
                PIN=pin,
                ID_loja=id_loja,
                Nome_loja=nome_loja
            )

            db.session.add(entrega)
            db.session.commit()

            # Dispara WhatsApp
            inquilino = Inquilino.query.get(id_morador)
            msg = f"""
    Olá, *{inquilino.Nome_morador}*! 👋👋 
    Sua encomenda da loja *{nome_loja}* com *{quantidade}* pacote(s) chegou hoje, e já está disponível para retirada na portaria! 😁

    Você possui um prazo de retirada de até *05 dias* ⏳.

    📦 Código do produto: {codigo_produto}
    🔐 PIN para retirada: *{pin}*

    Apresente este *PIN* ao funcionário para liberar sua encomenda! 🔓
            """

            try:
                enviar_whatsapp(inquilino.Telefone, msg)   # <<< AJUSTADO
                flash("Entrega registrada e WhatsApp enviado!", "success")
            except Exception as e:
                flash(f"Entrega registrada, mas erro ao enviar WhatsApp: {e}", "danger")

            return redirect(url_for("dashboard"))

        # ----- FILTROS VIA GET -----
        bloco = request.args.get("bloco", "")
        apartamento = request.args.get("apartamento", "")

        consulta = Inquilino.query

        if bloco:
            consulta = consulta.filter(Inquilino.Bloco.ilike(f"%{bloco}%"))

        if apartamento:
            consulta = consulta.filter(Inquilino.Apartamento.ilike(f"%{apartamento}%"))

        inquilinos = consulta.order_by(Inquilino.Nome_morador).all()
        lojas = Ecommerce.query.order_by(Ecommerce.Nome_loja).all()

        return render_template("registrar_entrega.html", inquilinos=inquilinos, lojas=lojas)
    
    # -------------------- EDITAR ENTREGA --------------------
    @app.route("/editar-entrega/<int:entrega_id>", methods=["GET", "POST"])
    def editar_entrega(entrega_id):
        entrega = Entrega.query.get_or_404(entrega_id)

        if request.method == "POST":
            entrega.Status = request.form.get("status")

            data_retirada_str = request.form.get("data_retirada")
            if data_retirada_str:
                entrega.Data_retirada = datetime.strptime(data_retirada_str, "%Y-%m-%dT%H:%M")

            db.session.commit()
            return redirect(url_for("pesquisar_entregas"))

        return render_template("editar_entrega.html", entrega=entrega)




    # -------------------- ATUALIZAR A BAIXA --------------------
    @app.route("/atualizar-entrega/<int:id>", methods=["POST"])
    @login_required
    def atualizar_entrega(id):
        entrega = Entrega.query.get_or_404(id)

        novo_status = request.form.get("status")
        data_retirada = request.form.get("data_retirada")

        entrega.status = novo_status

        # Se status for retirado → permitir e salvar data
        if novo_status == "Retirado":
            entrega.data_retirada = data_retirada
        else:
            entrega.data_retirada = None  # zera se não for retirado

        db.session.commit()

        flash("Entrega atualizada com sucesso!", "success")
        return redirect("/listar-entregas")




