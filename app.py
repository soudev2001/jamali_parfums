import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# ================= CONFIGURATION =================
MONGO_URI      = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SMTP_SERVER    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", 587))
SMTP_USER      = os.getenv("SMTP_USERNAME")
SMTP_PASS      = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL")

# ================= INITIALISATIONS =================
db = None
try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client.jamali_db
        print("[OK] Connecte a MongoDB")
except Exception as e:
    print(f"[ERR] MongoDB : {e}")

model = None
if GEMINI_API_KEY and "votre_cle" not in GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    system_prompt = (
        "Tu es l'assistant virtuel officiel de 'Jamali Parfum', une boutique de parfums de luxe au Maroc (Casablanca). "
        "Tu dois etre chaleureux, professionnel et vendeur. "
        "Nos parfums coutent 150 MAD l'unite. La livraison est disponible partout au Maroc sous 24h/48h "
        "avec paiement a la livraison (Cash on Delivery). "
        "Reponds toujours en Francais, mais n'hesite pas a inclure des expressions polies en Darija marocaine "
        "(ex: Salam, Merhaba, Bghiti chi haja). Reste concis (2-3 phrases maximum)."
    )
    model = genai.GenerativeModel(
        "gemini-2.5-flash-preview-09-2025",
        system_instruction=system_prompt
    )
    print("[OK] Google Gemini configure")

# ================= HELPERS =================
def send_order_email(subject, body_text, body_html=None):
    """Envoie un email via Gmail SMTP. Silencieux en cas d'erreur."""
    if not (SMTP_USER and SMTP_PASS and ADMIN_EMAIL):
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = SMTP_USER
        msg["To"]      = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("[OK] Email envoye")
    except Exception as e:
        print(f"[ERR] Email : {e}")

# ================= ROUTES =================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Serveur Jamali Parfum en ligne"})

@app.route("/api/chat", methods=["POST"])
def chat_with_gemini():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message vide"}), 400
    if model:
        try:
            response = model.generate_content(user_message)
            return jsonify({"reply": response.text})
        except Exception as e:
            print(f"Erreur Gemini: {e}")
            return jsonify({"reply": "Desole, probleme technique. Contactez-nous sur WhatsApp."}), 500
    return jsonify({"reply": "L'IA est en maintenance."})

@app.route("/api/order", methods=["POST"])
def place_order():
    data  = request.get_json(silent=True) or {}
    cart  = data.get("cart", [])
    total = data.get("total", 0)

    order_id = "N/A"
    if db is not None:
        result   = db.orders.insert_one({
            "items":  cart,
            "total":  total,
            "status": "Nouvelle",
            "date":   datetime.utcnow()
        })
        order_id = str(result.inserted_id)

    lines = "\n".join(
        f"  - {i.get('quantity')}x {i.get('name')} (Ref: {i.get('reference')})"
        for i in cart
    )
    txt_body = (
        f"NOUVELLE COMMANDE JAMALI PARFUM\n"
        f"ID: {order_id}\n\n"
        f"Articles:\n{lines}\n\n"
        f"TOTAL: {total} MAD"
    )
    html_rows = "".join(
        f"<li>{i.get('quantity')}x <b>{i.get('name')}</b> (Ref: {i.get('reference')})</li>"
        for i in cart
    )
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
      <h2 style="color:#d97706;border-bottom:2px solid #d97706;padding-bottom:8px">
        Nouvelle commande &mdash; Jamali Parfum
      </h2>
      <p><b>ID Commande :</b> <code>{order_id}</code></p>
      <ul style="line-height:1.8">{html_rows}</ul>
      <p style="font-size:1.3em;background:#fef3c7;padding:12px;border-radius:6px">
        <b>TOTAL : {total} MAD</b>
      </p>
    </div>
    """
    send_order_email("Nouvelle commande Jamali Parfum !", txt_body, html_body)

    return jsonify({"success": True, "message": "Commande traitee.", "order_id": order_id})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
