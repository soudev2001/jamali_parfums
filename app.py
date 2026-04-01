import os
import secrets
try:
    import stripe as _stripe_lib
except ImportError:
    _stripe_lib = None
from bson import ObjectId
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from pymongo import MongoClient
import google.generativeai as genai
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement (.env prend toujours la priorité)
load_dotenv(override=True)

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

# Fallback in-memory products store (quand MongoDB est absent)
PRODUCTS_STORE = []
ORDERS_STORE   = []
FAQ_STORE      = []   # FAQ in-memory

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
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin_page():
    return redirect('/')

@app.route('/logo.svg')
def logo():
    return send_from_directory('.', 'logo.svg', mimetype='image/svg+xml')

@app.route('/api/status')
def status():
    return jsonify({
        "status": "Serveur Jamali Parfum en ligne",
        "port": int(os.getenv("PORT", 5001)),
        "db": db is not None
    })

# ─── Public catalogue ────────────────────────────────────────
@app.route('/api/products')
def get_products():
    page  = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 200))
    cat   = request.args.get('category', '')
    q     = request.args.get('q', '').lower()
    if db is not None:
        filt = {}
        if cat:  filt['category'] = cat
        if q:    filt['$or'] = [{'name':{'$regex':q,'$options':'i'}},{'brand':{'$regex':q,'$options':'i'}}]
        total = db.products.count_documents(filt)
        items = list(db.products.find(filt, {'_id':0}).skip((page-1)*limit).limit(limit))
        return jsonify({"items": items, "total": total, "db": True})
    # fallback statique
    items = PRODUCTS_STORE
    if cat: items = [p for p in items if p.get('category')==cat]
    if q:   items = [p for p in items if q in p.get('name','').lower() or q in p.get('brand','').lower()]
    return jsonify({"items": items[(page-1)*limit:page*limit], "total": len(items), "db": False})


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
    data  = request.json
    cart  = data.get('cart', [])
    total = data.get('total', 0)

    order_data = {"items": cart, "total": total, "status": "Nouvelle", "date": datetime.now().isoformat()}
    order_id   = "N/A"

    if db is not None:
        result   = db.orders.insert_one({**order_data, "date": datetime.now()})
        order_id = str(result.inserted_id)
        order_data['_id'] = order_id
    else:
        order_data['_id'] = secrets.token_hex(6)
        ORDERS_STORE.append(order_data)
        order_id = order_data['_id']

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

    return jsonify({"success": True, "message": "Commande traitée.", "order_id": order_id})


@app.route('/api/faq')
def public_faq():
    """FAQ publique pour la boutique."""
    if db is not None:
        items = list(db.faq.find({}, {'_id': 0}).sort('order', 1))
        return jsonify(items)
    return jsonify(sorted(FAQ_STORE, key=lambda x: x.get('order', 0)))


# ──────────────────── STRIPE ROUTES ────────────────────────────

# Configure Stripe secret key on startup
_stripe_secret = os.getenv('STRIPE_SECRET_KEY', '')
if _stripe_lib and _stripe_secret and not _stripe_secret.startswith('sk_test_replace'):
    _stripe_lib.api_key = _stripe_secret

# In-memory legal settings store (persists during server lifetime)
_LEGAL_SETTINGS = {}


@app.route('/api/stripe-key')
def get_stripe_key():
    pk = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_replace_with_your_key')
    return jsonify({'publishable_key': pk})


@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    if not _stripe_lib:
        return jsonify({'error': 'Stripe non installé'}), 503
    secret = os.getenv('STRIPE_SECRET_KEY', '')
    if not secret or secret.startswith('sk_test_replace'):
        return jsonify({'error': 'Clé Stripe non configurée'}), 503
    _stripe_lib.api_key = secret
    data = request.json or {}
    amount_mad = max(10, int(data.get('amount', 150)))
    # Convert MAD to EUR cents (approx 1 MAD ≈ 0.091 EUR, min 50 cents for Stripe)
    amount_cents = max(50, int(amount_mad * 9.1))
    try:
        intent = _stripe_lib.PaymentIntent.create(
            amount=amount_cents,
            currency='eur',
            metadata={'order_mad': str(amount_mad), 'source': 'jamali_parfum'}
        )
        return jsonify({'client_secret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/settings')
def public_settings():
    return jsonify(_LEGAL_SETTINGS)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
