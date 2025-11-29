import os
from flask import current_app
from twilio.rest import Client

def enviar_whatsapp(numero_destino, mensagem):
    """
    Envia uma mensagem de WhatsApp usando a API do Twilio.
    Se falhar, levanta uma exceção capturada nas rotas.
    """
    # Pega as configurações do app (carregadas do config.py)
    try:

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # fallback sandbox

        print("DEBUG: account_sid =", account_sid)
        print("DEBUG: auth_token =", "SET" if auth_token else None)
        print("DEBUG: from_number =", from_number)

        if not account_sid or not auth_token:
            raise RuntimeError("TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN não encontrados no .env")
        

        # Normaliza o número de destino
        n = str(numero_destino).strip()
        # Remove espaços e possíveis caracteres não numéricos (menos +)
        n = n.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if n.startswith("whatsapp:"):
            numero_formatado = n
        else:
            # garante ter +55 no começo
            if n.startswith("+"):
                numero_formatado = "whatsapp:" + n
            elif n.startswith("55"):
                numero_formatado = "whatsapp:+" + n
            else:
                numero_formatado = "whatsapp:+55" + n

        print("DEBUG: numero_formatado =", numero_formatado)

        # Inicializa o cliente Twilio
        client = Client(account_sid, auth_token)

        try:
            msg = client.messages.create(
                from_=from_number,
                to=numero_formatado,
                body=mensagem
            )
            print("✔ Enviado com sucesso! Message SID:", msg.sid)
            return msg.sid
        except Exception as e:
            print("❌ Erro ao enviar mensagem:", repr(e))
            raise

    except Exception as e:
        # Gera log no console para debug
        print(f"❌ Erro ao enviar WhatsApp para {numero_destino}: {e}")
        # Relança o erro para ser tratado na rota
        raise e
