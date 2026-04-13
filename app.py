import os
import io
import csv
import re
import base64
import secrets
import hmac
import functools
try:
    import stripe as _stripe_lib
except ImportError:
    _stripe_lib = None
from bson import ObjectId
from flask import Flask, request, jsonify, send_from_directory, redirect, Response
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

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 Mo max

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
ACTIVITY_STORE = []   # Activity log in-memory

# Admin tokens & password
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_TOKENS   = {}  # token -> expiry (simple in-memory store)

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

# ================= ROUTES =================================================================
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

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
        items = list(db.products.find(filt, {'_id':0, 'image_b64':0}).skip((page-1)*limit).limit(limit))
        return jsonify({"items": items, "total": total, "db": True})
    # fallback statique
    items = PRODUCTS_STORE
    if cat: items = [p for p in items if p.get('category')==cat]
    if q:   items = [p for p in items if q in p.get('name','').lower() or q in p.get('brand','').lower()]
    page_items = [{k:v for k,v in p.items() if k != 'image_b64'} for p in items[(page-1)*limit:page*limit]]
    return jsonify({"items": page_items, "total": len(items), "db": False})


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


# ──────────────────── UPLOADS ──────────────────────────────────────

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


def _save_b64_image(b64_data):
    """Decode a data-URI base64 image string, save to uploads/, return the URL path."""
    match = re.match(r'data:image/([\w+]+);base64,(.*)', b64_data, re.DOTALL)
    if not match:
        return ''
    ext = match.group(1).lower()
    if ext == 'jpeg':
        ext = 'jpg'
    elif ext == 'svg+xml':
        ext = 'svg'
    if ext not in ('jpg', 'png', 'gif', 'webp', 'svg'):
        return ''
    raw = base64.b64decode(match.group(2))
    fname = secrets.token_hex(12) + '.' + ext
    fpath = os.path.join(UPLOAD_FOLDER, fname)
    with open(fpath, 'wb') as f:
        f.write(raw)
    return f'/uploads/{fname}'


def _process_product_image(data):
    """If data contains image_b64, save it and set image field. Remove image_b64 before DB storage."""
    b64 = data.pop('image_b64', '')
    if b64:
        url = _save_b64_image(b64)
        if url:
            data['image'] = url
    return data


# ================= MIGRATION: convertir image_b64 existants =================
if db is not None:
    _b64_products = list(db.products.find({"image_b64": {"$ne": ""}, "image": {"$in": ["", None]}}, {"_id": 1, "image_b64": 1}))
    for _p in _b64_products:
        _url = _save_b64_image(_p.get('image_b64', ''))
        if _url:
            db.products.update_one({"_id": _p["_id"]}, {"$set": {"image": _url}, "$unset": {"image_b64": ""}})
    if _b64_products:
        print(f"Migration : {len(_b64_products)} image(s) b64 converties en fichiers")
    db.products.update_many({}, {"$unset": {"image_b64": ""}})


# ──────────────────── ADMIN AUTH ───────────────────────────────────

def require_admin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if not token or token not in ADMIN_TOKENS:
            return jsonify({"error": "Non autorisé"}), 403
        return f(*args, **kwargs)
    return wrapper


def _log_activity(atype, desc, user='admin'):
    entry = {"type": atype, "desc": desc, "user": user, "timestamp": datetime.now().isoformat()}
    if db is not None:
        db.activity.insert_one(entry)
    else:
        ACTIVITY_STORE.insert(0, entry)


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    pwd = data.get('password', '')
    if not hmac.compare_digest(pwd, ADMIN_PASSWORD):
        return jsonify({"error": "Mot de passe incorrect"}), 401
    token = secrets.token_hex(32)
    ADMIN_TOKENS[token] = True
    _log_activity('auth', 'Connexion admin')
    return jsonify({"token": token})


@app.route('/api/admin/logout', methods=['POST'])
@require_admin
def admin_logout():
    token = request.headers.get('X-Admin-Token', '')
    ADMIN_TOKENS.pop(token, None)
    return jsonify({"ok": True})


@app.route('/api/admin/change-password', methods=['POST'])
@require_admin
def admin_change_password():
    data = request.json or {}
    new_pwd = data.get('new_password', '').strip()
    if len(new_pwd) < 4:
        return jsonify({"error": "Mot de passe trop court (min 4 caractères)"}), 400
    global ADMIN_PASSWORD
    ADMIN_PASSWORD = new_pwd
    _log_activity('auth', 'Mot de passe modifié')
    return jsonify({"ok": True})


# ──────────────────── ADMIN STATS ──────────────────────────────────

@app.route('/api/admin/stats')
@require_admin
def admin_stats():
    if db is not None:
        total_products = db.products.count_documents({})
        total_orders = db.orders.count_documents({})
        revenue = sum(o.get('total', 0) for o in db.orders.find({}, {'total': 1}))
        pending = db.orders.count_documents({"status": {"$in": ["Nouvelle", "En cours"]}})
    else:
        total_products = len(PRODUCTS_STORE)
        total_orders = len(ORDERS_STORE)
        revenue = sum(o.get('total', 0) for o in ORDERS_STORE)
        pending = sum(1 for o in ORDERS_STORE if o.get('status') in ('Nouvelle', 'En cours'))
    return jsonify({
        "total_products": total_products,
        "total_orders": total_orders,
        "revenue": revenue,
        "pending_orders": pending
    })


# ──────────────────── ADMIN PRODUCTS ───────────────────────────────

@app.route('/api/admin/products')
@require_admin
def admin_products():
    page  = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    q     = request.args.get('q', '').strip().lower()
    if db is not None:
        filt = {}
        if q:
            filt['$or'] = [
                {'name': {'$regex': q, '$options': 'i'}},
                {'brand': {'$regex': q, '$options': 'i'}},
                {'reference': {'$regex': q, '$options': 'i'}}
            ]
        total = db.products.count_documents(filt)
        items = list(db.products.find(filt).skip((page-1)*limit).limit(limit))
        for item in items:
            item['_id'] = str(item['_id'])
        return jsonify({"items": items, "total": total})
    # fallback
    items = PRODUCTS_STORE
    if q:
        items = [p for p in items if q in p.get('name','').lower() or q in p.get('brand','').lower() or q in p.get('reference','').lower()]
    total = len(items)
    return jsonify({"items": items[(page-1)*limit:page*limit], "total": total})


@app.route('/api/admin/products', methods=['POST'])
@require_admin
def admin_create_product():
    data = request.json or {}
    data = _process_product_image(data)
    if db is not None:
        result = db.products.insert_one(data)
        data['_id'] = str(result.inserted_id)
    else:
        data['_id'] = secrets.token_hex(6)
        PRODUCTS_STORE.append(data)
    _log_activity('product', f"Produit ajouté : {data.get('name', '?')}")
    return jsonify(data), 201


@app.route('/api/admin/products/<product_id>', methods=['PUT'])
@require_admin
def admin_update_product(product_id):
    data = request.json or {}
    data.pop('_id', None)
    data = _process_product_image(data)
    if db is not None:
        try:
            db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})
        except Exception:
            db.products.update_one({"_id": product_id}, {"$set": data})
    else:
        for i, p in enumerate(PRODUCTS_STORE):
            if p.get('_id') == product_id:
                PRODUCTS_STORE[i].update(data)
                break
    _log_activity('product', f"Produit modifié : {data.get('name', product_id)}")
    return jsonify({"ok": True})


@app.route('/api/admin/products/<product_id>', methods=['DELETE'])
@require_admin
def admin_delete_product(product_id):
    if db is not None:
        try:
            db.products.delete_one({"_id": ObjectId(product_id)})
        except Exception:
            db.products.delete_one({"_id": product_id})
    else:
        PRODUCTS_STORE[:] = [p for p in PRODUCTS_STORE if p.get('_id') != product_id]
    _log_activity('product', f"Produit supprimé : {product_id}")
    return jsonify({"ok": True})


# ──────────────────── ADMIN ORDERS ─────────────────────────────────

@app.route('/api/admin/orders')
@require_admin
def admin_orders():
    limit = int(request.args.get('limit', 50))
    if db is not None:
        orders = list(db.orders.find().sort('date', -1).limit(limit))
        for o in orders:
            o['_id'] = str(o['_id'])
            if isinstance(o.get('date'), datetime):
                o['date'] = o['date'].isoformat()
        return jsonify(orders)
    return jsonify(sorted(ORDERS_STORE, key=lambda x: x.get('date', ''), reverse=True)[:limit])


@app.route('/api/admin/orders/<order_id>', methods=['PUT'])
@require_admin
def admin_update_order(order_id):
    data = request.json or {}
    new_status = data.get('status', '')
    if db is not None:
        try:
            db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": new_status}})
        except Exception:
            db.orders.update_one({"_id": order_id}, {"$set": {"status": new_status}})
    else:
        for o in ORDERS_STORE:
            if o.get('_id') == order_id:
                o['status'] = new_status
                break
    _log_activity('order', f"Commande {order_id[:8]}… → {new_status}")
    return jsonify({"ok": True})


# ──────────────────── ADMIN CLIENTS ────────────────────────────────

@app.route('/api/admin/clients')
@require_admin
def admin_clients():
    """Agrège les clients à partir des commandes."""
    if db is not None:
        pipeline = [
            {"$group": {
                "_id": {"name": {"$ifNull": ["$name", "Client"]}, "phone": {"$ifNull": ["$phone", "N/A"]}},
                "orders_count": {"$sum": 1},
                "total_spent": {"$sum": {"$ifNull": ["$total", 0]}},
                "last_order": {"$max": "$date"},
                "city": {"$first": {"$ifNull": ["$city", ""]}},
                "orders": {"$push": {
                    "_id": {"$toString": "$_id"},
                    "total": "$total",
                    "status": "$status",
                    "date": "$date",
                    "items": {"$size": {"$ifNull": ["$items", []]}}
                }}
            }},
            {"$project": {
                "_id": 0,
                "name": "$_id.name",
                "phone": "$_id.phone",
                "orders_count": 1,
                "total_spent": 1,
                "last_order": 1,
                "city": 1,
                "orders": {"$slice": ["$orders", 10]}
            }},
            {"$sort": {"total_spent": -1}}
        ]
        clients = list(db.orders.aggregate(pipeline))
        for c in clients:
            if isinstance(c.get('last_order'), datetime):
                c['last_order'] = c['last_order'].isoformat()
            for o in c.get('orders', []):
                if isinstance(o.get('date'), datetime):
                    o['date'] = o['date'].isoformat()
        return jsonify(clients)
    # fallback
    clients_map = {}
    for o in ORDERS_STORE:
        key = (o.get('name', 'Client'), o.get('phone', 'N/A'))
        if key not in clients_map:
            clients_map[key] = {"name": key[0], "phone": key[1], "orders_count": 0, "total_spent": 0, "city": o.get('city', ''), "orders": [], "last_order": None}
        c = clients_map[key]
        c['orders_count'] += 1
        c['total_spent'] += o.get('total', 0)
        c['last_order'] = o.get('date')
        c['orders'].append({"_id": o.get('_id', ''), "total": o.get('total', 0), "status": o.get('status', ''), "date": o.get('date', ''), "items": len(o.get('items', []))})
    return jsonify(sorted(clients_map.values(), key=lambda x: x['total_spent'], reverse=True))


# ──────────────────── ADMIN ACTIVITY ───────────────────────────────

@app.route('/api/admin/activity')
@require_admin
def admin_activity():
    limit = int(request.args.get('limit', 150))
    if db is not None:
        items = list(db.activity.find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))
        return jsonify(items)
    return jsonify(ACTIVITY_STORE[:limit])


# ──────────────────── ADMIN FAQ ────────────────────────────────────

@app.route('/api/admin/faq')
@require_admin
def admin_faq():
    if db is not None:
        items = list(db.faq.find().sort('order', 1))
        for item in items:
            item['_id'] = str(item['_id'])
        return jsonify(items)
    return jsonify(sorted(FAQ_STORE, key=lambda x: x.get('order', 0)))


@app.route('/api/admin/faq', methods=['POST'])
@require_admin
def admin_create_faq():
    data = request.json or {}
    if db is not None:
        result = db.faq.insert_one(data)
        data['_id'] = str(result.inserted_id)
    else:
        data['_id'] = secrets.token_hex(6)
        FAQ_STORE.append(data)
    _log_activity('faq', f"FAQ ajoutée : {data.get('question_fr', '?')[:40]}")
    return jsonify(data), 201


@app.route('/api/admin/faq/<faq_id>', methods=['PUT'])
@require_admin
def admin_update_faq(faq_id):
    data = request.json or {}
    data.pop('_id', None)
    if db is not None:
        try:
            db.faq.update_one({"_id": ObjectId(faq_id)}, {"$set": data})
        except Exception:
            db.faq.update_one({"_id": faq_id}, {"$set": data})
    else:
        for i, f in enumerate(FAQ_STORE):
            if f.get('_id') == faq_id:
                FAQ_STORE[i].update(data)
                break
    _log_activity('faq', 'FAQ mise à jour')
    return jsonify({"ok": True})


@app.route('/api/admin/faq/<faq_id>', methods=['DELETE'])
@require_admin
def admin_delete_faq(faq_id):
    if db is not None:
        try:
            db.faq.delete_one({"_id": ObjectId(faq_id)})
        except Exception:
            db.faq.delete_one({"_id": faq_id})
    else:
        FAQ_STORE[:] = [f for f in FAQ_STORE if f.get('_id') != faq_id]
    _log_activity('faq', 'FAQ supprimée')
    return jsonify({"ok": True})


# ──────────────────── ADMIN STOCK ALERTS ───────────────────────────

@app.route('/api/admin/stock-alerts')
@require_admin
def admin_stock_alerts():
    threshold = 5
    if db is not None:
        items = list(db.products.find({"stock": {"$lte": threshold}}, {"_id": 0, "name": 1, "reference": 1, "stock": 1}).sort("stock", 1))
        return jsonify(items)
    return jsonify(sorted([p for p in PRODUCTS_STORE if p.get('stock', 999) <= threshold], key=lambda x: x.get('stock', 0)))


# ──────────────────── ADMIN SETTINGS ───────────────────────────────

@app.route('/api/admin/settings', methods=['GET', 'POST'])
@require_admin
def admin_settings():
    if request.method == 'POST':
        data = request.json or {}
        _LEGAL_SETTINGS.update(data)
        if db is not None:
            db.settings.update_one({"_id": "legal"}, {"$set": data}, upsert=True)
        return jsonify({"ok": True})
    # GET
    if db is not None:
        doc = db.settings.find_one({"_id": "legal"}, {"_id": 0})
        return jsonify(doc or {})
    return jsonify(_LEGAL_SETTINGS)


# ──────────────────── ADMIN EXPORT ─────────────────────────────────

@app.route('/api/admin/export/orders')
@require_admin
def admin_export_orders():
    if db is not None:
        orders = list(db.orders.find().sort('date', -1))
    else:
        orders = sorted(ORDERS_STORE, key=lambda x: x.get('date', ''), reverse=True)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Client', 'Téléphone', 'Ville', 'Articles', 'Total', 'Statut'])
    for o in orders:
        oid = str(o.get('_id', ''))
        date = o.get('date', '')
        if isinstance(date, datetime):
            date = date.isoformat()
        items_count = len(o.get('items', []))
        writer.writerow([oid, date, o.get('name', ''), o.get('phone', ''), o.get('city', ''), items_count, o.get('total', 0), o.get('status', '')])

    csv_content = output.getvalue()
    return Response(csv_content, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=commandes-jamali.csv"})


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
