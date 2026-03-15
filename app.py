import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import google.generativeai as genai
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# ================= CONFIGURATION =================
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WA_FROM = os.getenv("TWILIO_WHATSAPP_NUMBER")
ADMIN_WA_TO = os.getenv("ADMIN_WHATSAPP_NUMBER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# ================= INITIALISATIONS =================
db = None
try:
    if MONGO_URI and "<username>" not in MONGO_URI:
        client = MongoClient(MONGO_URI)
        db = client.jamali_db
        print("âœ… ConnectÃ© Ã  MongoDB")
except Exception as e:
    print(f"âŒ Erreur MongoDB : {e}")

if GEMINI_API_KEY and "votre_cle" not in GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    system_prompt = """
    Tu es l'assistant virtuel officiel de 'Jamali Parfum', une boutique de parfums de luxe au Maroc (Casablanca).
    Tu dois Ãªtre chaleureux, professionnel et vendeur.
    Nos parfums coÃ»tent 150 MAD l'unitÃ©. La livraison est disponible partout au Maroc sous 24h/48h avec paiement Ã  la livraison (Cash on Delivery).
    RÃ©ponds toujours en FranÃ§ais, mais n'hÃ©site pas Ã  inclure des expressions polies en Darija marocaine (ex: Salam, Merhaba, Bghiti chi haja).
    Reste concis (2-3 phrases maximum).
    """
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025', system_instruction=system_prompt)
    print("âœ… API Google Gemini configurÃ©e")
else:
    model = None

if TWILIO_ACCOUNT_SID and "votre_twilio" not in TWILIO_ACCOUNT_SID:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print("âœ… Twilio configurÃ©")
else:
    twilio_client = None

# ================= ROUTES =================
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Serveur Jamali Parfum en ligne ðŸŸ¢"})

@app.route('/api/chat', methods=['POST'])
def chat_with_gemini():
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({"error": "Message vide"}), 400
    if model:
        try:
            response = model.generate_content(user_message)
            return jsonify({"reply": response.text})
        except Exception as e:
            return jsonify({"reply": "DÃ©solÃ©, problÃ¨me technique. Contactez-nous sur WhatsApp."}), 500
    return jsonify({"reply": "L'IA est en maintenance."})

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.json
    cart = data.get('cart', [])
    total = data.get('total', 0)

    order_data = {"items": cart, "total": total, "status": "Nouvelle", "date": datetime.now()}
    order_id = "N/A"

    if db is not None:
        result = db.orders.insert_one(order_data)
        order_id = str(result.inserted_id)

    items_text = "\n".join([f"- {item['quantity']}x {item['name']} (Ref: {item['reference']})" for item in cart])
    msg_body = f"ðŸ”¥ NOUVELLE COMMANDE JAMALI PARFUM ðŸ”¥\nID: {order_id}\n\nArticles:\n{items_text}\n\nTOTAL: {total} MAD"

    if twilio_client:
        try:
            twilio_client.messages.create(body=msg_body, from_=TWILIO_WA_FROM, to=ADMIN_WA_TO)
        except Exception as e:
            print(f"Erreur Twilio: {e}")

    if SMTP_SERVER and SMTP_USER:
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = ADMIN_EMAIL
            msg['Subject'] = "Nouvelle commande sur Jamali Parfum !"
            msg.attach(MIMEText(msg_body, 'plain'))
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Erreur Email: {e}")

    return jsonify({"success": True, "message": "Commande traitÃ©e.", "order_id": order_id})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
