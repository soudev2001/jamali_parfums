import os
import secrets
try:
    import stripe as _stripe_lib
except ImportError:
    _stripe_lib = None
from bson import ObjectId
from flask import Flask, request, jsonify, send_from_directory
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
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin2026")

# Token admin en mémoire (réinitialisé à chaque restart)
ADMIN_TOKEN = None

# Fallback in-memory products store (quand MongoDB est absent)
PRODUCTS_STORE = []
ORDERS_STORE   = []
ACTIVITY_LOG   = []   # Journal d'activité in-memory
FAQ_STORE      = []   # FAQ in-memory
MAX_ACTIVITY   = 300  # Garder les N dernières entrées

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
        items = list(db.products.find(filt, {'_id':0}).skip((page-1)*limit).limit(limit))
        return jsonify({"items": items, "total": total, "db": True})
    # fallback statique
    items = PRODUCTS_STORE
    if cat: items = [p for p in items if p.get('category')==cat]
    if q:   items = [p for p in items if q in p.get('name','').lower() or q in p.get('brand','').lower()]
    return jsonify({"items": items[(page-1)*limit:page*limit], "total": len(items), "db": False})

# ─── Helper auth ─────────────────────────────────────────────
def check_admin():
    """Accept both 'Authorization: Bearer <token>' and 'X-Admin-Token: <token>'."""
    auth    = request.headers.get('Authorization', '')
    x_token = request.headers.get('X-Admin-Token', '')
    token   = auth[7:] if auth.startswith('Bearer ') else x_token
    return bool(token and token == ADMIN_TOKEN and ADMIN_TOKEN is not None)

def log_activity(type_, desc, user='admin'):
    """Enregistre une action admin en mémoire."""
    ACTIVITY_LOG.append({
        '_id': secrets.token_hex(6),
        'type': type_,
        'desc': desc,
        'user': user,
        'timestamp': datetime.now().isoformat()
    })
    if len(ACTIVITY_LOG) > MAX_ACTIVITY:
        del ACTIVITY_LOG[0]


# ─── Admin Auth ───────────────────────────────────────────────
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    global ADMIN_TOKEN
    data = request.json or {}
    if data.get('password') == ADMIN_PASSWORD:
        ADMIN_TOKEN = secrets.token_hex(32)
        log_activity('auth', 'Connexion admin réussie')
        return jsonify({"token": ADMIN_TOKEN})
    log_activity('auth', 'Tentative de connexion échouée', 'inconnu')
    return jsonify({"error": "Mot de passe incorrect"}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    global ADMIN_TOKEN
    ADMIN_TOKEN = None
    return jsonify({"ok": True})

@app.route('/api/admin/change-password', methods=['POST'])
def admin_change_password():
    global ADMIN_PASSWORD
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    data = request.json or {}
    pwd  = data.get('new_password','')
    if len(pwd) < 6: return jsonify({"error":"Mot de passe trop court (min 6)"}), 400
    ADMIN_PASSWORD = pwd
    return jsonify({"ok": True})

# ─── Admin Stats ──────────────────────────────────────────────
@app.route('/api/admin/stats')
def admin_stats():
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    if db is not None:
        prod_count  = db.products.count_documents({})
        ord_count   = db.orders.count_documents({})
        new_count   = db.orders.count_documents({"status":"Nouvelle"})
        revenue_cur = list(db.orders.aggregate([{"$group":{"_id":None,"total":{"$sum":"$total"}}}]))
        revenue     = revenue_cur[0]['total'] if revenue_cur else 0
    else:
        prod_count = len(PRODUCTS_STORE)
        ord_count  = len(ORDERS_STORE)
        new_count  = sum(1 for o in ORDERS_STORE if o.get('status')=='Nouvelle')
        revenue    = sum(o.get('total',0) for o in ORDERS_STORE)
    # Alertes stock (stock ≤ 3)
    if db is not None:
        low_stock = db.products.count_documents({'stock': {'$lte': 3, '$gt': -1}})
    else:
        low_stock = sum(1 for p in PRODUCTS_STORE if (p.get('stock') or 0) <= 3)
    return jsonify({
        'products': prod_count, 'orders': ord_count,
        'new_orders': new_count, 'revenue': revenue,
        'low_stock': low_stock, 'ai': model is not None
    })

# ─── Admin Products CRUD ─────────────────────────────────────
@app.route('/api/admin/products')
def admin_list_products():
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    page  = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    q     = request.args.get('q', '').lower()
    if db is not None:
        filt = {}
        if q: filt['$or'] = [{'name':{'$regex':q,'$options':'i'}},{'brand':{'$regex':q,'$options':'i'}},{'reference':{'$regex':q,'$options':'i'}}]
        total = db.products.count_documents(filt)
        items = list(db.products.find(filt).sort('reference',1).skip((page-1)*limit).limit(limit))
        for p in items: p['_id'] = str(p['_id'])
        return jsonify({"items": items, "total": total, "page": page, "pages": max(1,(total+limit-1)//limit)})
    items = PRODUCTS_STORE
    if q: items = [p for p in items if q in p.get('name','').lower() or q in p.get('brand','').lower() or q in p.get('reference','').lower()]
    total  = len(items)
    slice_ = items[(page-1)*limit:page*limit]
    return jsonify({"items": slice_, "total": total, "page": page, "pages": max(1,(total+limit-1)//limit)})

@app.route('/api/admin/products', methods=['POST'])
def admin_create_product():
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    data = request.json or {}
    data.setdefault('createdAt', datetime.now().isoformat())
    data.setdefault('available', True)
    data.setdefault('isBestseller', False)
    data.setdefault('stock', 0)
    data.setdefault('price', 150)
    if db is not None:
        if db.products.find_one({'reference': data.get('reference')}):
            return jsonify({"error": "Référence déjà existante"}), 409
        res = db.products.insert_one(data)
        data['_id'] = str(res.inserted_id)
        log_activity('product', f"Produit créé : {data.get('name','')} ({data.get('reference','')})")
        return jsonify(data), 201
    if any(p.get('reference')==data.get('reference') for p in PRODUCTS_STORE):
        return jsonify({"error": "Référence déjà existante"}), 409
    data['_id'] = secrets.token_hex(8)
    PRODUCTS_STORE.append(data)
    log_activity('product', f"Produit créé : {data.get('name','')} ({data.get('reference','')})")
    return jsonify(data), 201

@app.route('/api/admin/products/<pid>', methods=['PUT'])
def admin_update_product(pid):
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    data = request.json or {}
    data.pop('_id', None)
    if db is not None:
        try:
            oid = ObjectId(pid)
        except Exception:
            return jsonify({"error":"ID invalide"}), 400
        res = db.products.update_one({'_id': oid}, {'$set': data})
        if res.matched_count == 0: return jsonify({"error":"Produit introuvable"}), 404
        updated = db.products.find_one({'_id': oid})
        updated['_id'] = str(updated['_id'])
        return jsonify(updated)
    for i, p in enumerate(PRODUCTS_STORE):
        if p.get('_id') == pid:
            PRODUCTS_STORE[i].update(data)
            return jsonify(PRODUCTS_STORE[i])
    return jsonify({"error":"Produit introuvable"}), 404

@app.route('/api/admin/products/<pid>', methods=['DELETE'])
def admin_delete_product(pid):
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    if db is not None:
        try: oid = ObjectId(pid)
        except Exception: return jsonify({"error":"ID invalide"}), 400
        p = db.products.find_one({'_id': oid})
        res = db.products.delete_one({'_id': oid})
        if res.deleted_count == 0: return jsonify({"error":"Produit introuvable"}), 404
        log_activity('product', f"Produit supprimé : {(p or {}).get('name','?')}")
        return jsonify({"ok": True})
    global PRODUCTS_STORE
    orig = len(PRODUCTS_STORE)
    name = next((p.get('name','?') for p in PRODUCTS_STORE if p.get('_id') == pid), '?')
    PRODUCTS_STORE = [p for p in PRODUCTS_STORE if p.get('_id') != pid]
    if len(PRODUCTS_STORE) == orig: return jsonify({"error":"Produit introuvable"}), 404
    log_activity('product', f'Produit supprimé : {name}')
    return jsonify({"ok": True})

# ─── Admin Orders ─────────────────────────────────────────────
@app.route('/api/admin/orders')
def admin_list_orders():
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    limit = int(request.args.get('limit', 50))
    if db is not None:
        orders = list(db.orders.find().sort('date',-1).limit(limit))
        for o in orders: o['_id'] = str(o['_id'])
        return jsonify(orders)
    return jsonify(sorted(ORDERS_STORE, key=lambda x: x.get('date',''), reverse=True)[:limit])

@app.route('/api/admin/orders/<oid>', methods=['PUT'])
def admin_update_order(oid):
    if not check_admin(): return jsonify({"error":"Non autorisé"}), 403
    data = request.json or {}
    if db is not None:
        try: mongo_id = ObjectId(oid)
        except Exception: return jsonify({"error":"ID invalide"}), 400
        db.orders.update_one({'_id': mongo_id}, {'$set': data})
        if 'status' in data: log_activity('order', f"Commande {oid[-6:].upper()} → {data['status']}")
        return jsonify({"ok": True})
    for o in ORDERS_STORE:
        if o.get('_id') == oid:
            o.update(data)
            if 'status' in data: log_activity('order', f"Commande {oid[-6:].upper()} → {data['status']}")
            return jsonify({"ok": True})
    return jsonify({"error":"Commande introuvable"}), 404

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


# ──────────────────── NOUVELLES ROUTES ADMIN ──────────────────────────────────

@app.route('/api/admin/stock-alerts')
def admin_stock_alerts():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    if db is not None:
        items = list(db.products.find(
            {'stock': {'$lte': 3}},
            {'_id': 0, 'name': 1, 'reference': 1, 'stock': 1, 'category': 1}
        ).sort('stock', 1).limit(20))
    else:
        items = sorted(
            [{'name': p.get('name'), 'reference': p.get('reference'),
              'stock': p.get('stock', 0), 'category': p.get('category')}
             for p in PRODUCTS_STORE if (p.get('stock') or 0) <= 3],
            key=lambda x: x.get('stock', 0)
        )[:20]
    return jsonify(items)


@app.route('/api/admin/clients')
def admin_clients():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    if db is not None:
        orders = list(db.orders.find(
            {}, {'_id': 1, 'client': 1, 'total': 1, 'date': 1, 'items': 1, 'status': 1}
        ).sort('date', -1))
        for o in orders: o['_id'] = str(o['_id'])
    else:
        orders = ORDERS_STORE
    clients = {}
    for o in orders:
        c     = o.get('client') or {}
        phone = (c.get('phone') or o.get('phone') or 'unknown').strip() or 'unknown'
        if phone not in clients:
            name = (c.get('firstName', '') + ' ' + c.get('lastName', '')).strip()
            clients[phone] = {
                'phone': phone,
                'name':  name or c.get('name', '') or '—',
                'city':  c.get('city') or o.get('city') or '—',
                'orders_count': 0, 'total_spent': 0,
                'last_order': None, 'orders': []
            }
        clients[phone]['orders_count'] += 1
        clients[phone]['total_spent']  += float(o.get('total', 0) or 0)
        d = str(o.get('date', ''))
        if not clients[phone]['last_order'] or d > str(clients[phone]['last_order']):
            clients[phone]['last_order'] = d
        clients[phone]['orders'].append({
            '_id': str(o.get('_id', '?')),
            'total': o.get('total', 0),
            'date': o.get('date', ''),
            'status': o.get('status', ''),
            'items': len(o.get('items') or [])
        })
    result = sorted(clients.values(), key=lambda x: x['total_spent'], reverse=True)
    return jsonify(result)


@app.route('/api/admin/activity')
def admin_activity():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    limit  = int(request.args.get('limit', 100))
    type_f = request.args.get('type', '')
    items  = list(reversed(ACTIVITY_LOG))
    if type_f:
        items = [a for a in items if a.get('type') == type_f]
    return jsonify(items[:limit])


@app.route('/api/admin/faq', methods=['GET'])
def admin_list_faq():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    if db is not None:
        items = list(db.faq.find({}).sort('order', 1))
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    return jsonify(sorted(FAQ_STORE, key=lambda x: x.get('order', 0)))


@app.route('/api/admin/faq', methods=['POST'])
def admin_create_faq():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    data = request.json or {}
    data.setdefault('order', len(FAQ_STORE))
    data.setdefault('createdAt', datetime.now().isoformat())
    if db is not None:
        res = db.faq.insert_one(data)
        data['_id'] = str(res.inserted_id)
        log_activity('faq', f"FAQ créée : {str(data.get('question_fr',''))[:50]}")
        return jsonify(data), 201
    data['_id'] = secrets.token_hex(6)
    FAQ_STORE.append(data)
    log_activity('faq', f"FAQ créée : {str(data.get('question_fr',''))[:50]}")
    return jsonify(data), 201


@app.route('/api/admin/faq/<fid>', methods=['PUT'])
def admin_update_faq(fid):
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    data = request.json or {}
    data.pop('_id', None)
    if db is not None:
        try: oid = ObjectId(fid)
        except Exception: return jsonify({'error': 'ID invalide'}), 400
        db.faq.update_one({'_id': oid}, {'$set': data})
        log_activity('faq', f"FAQ modifiée")
        return jsonify({'ok': True})
    for i, f in enumerate(FAQ_STORE):
        if f.get('_id') == fid:
            FAQ_STORE[i].update(data)
            log_activity('faq', f"FAQ modifiée")
            return jsonify(FAQ_STORE[i])
    return jsonify({'error': 'FAQ introuvable'}), 404


@app.route('/api/admin/faq/<fid>', methods=['DELETE'])
def admin_delete_faq(fid):
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    global FAQ_STORE
    if db is not None:
        try: oid = ObjectId(fid)
        except Exception: return jsonify({'error': 'ID invalide'}), 400
        db.faq.delete_one({'_id': oid})
        log_activity('faq', f'FAQ supprimée')
        return jsonify({'ok': True})
    orig = len(FAQ_STORE)
    FAQ_STORE = [f for f in FAQ_STORE if f.get('_id') != fid]
    if len(FAQ_STORE) == orig: return jsonify({'error': 'FAQ introuvable'}), 404
    log_activity('faq', f'FAQ supprimée')
    return jsonify({'ok': True})


@app.route('/api/faq')
def public_faq():
    """FAQ publique pour la boutique."""
    if db is not None:
        items = list(db.faq.find({}, {'_id': 0}).sort('order', 1))
        return jsonify(items)
    return jsonify(sorted(FAQ_STORE, key=lambda x: x.get('order', 0)))


@app.route('/api/admin/upload-image', methods=['POST'])
def admin_upload_image():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    data     = request.json or {}
    data_url = data.get('data_url', '')
    if not data_url.startswith('data:image/'):
        return jsonify({'error': 'Format invalide — attendu data:image/...'}), 400
    if len(data_url) > 3_500_000:
        return jsonify({'error': 'Image trop grande (max ~2.5 Mo)'}), 413
    log_activity('upload', 'Image produit uploadée')
    return jsonify({'url': data_url, 'ok': True})


@app.route('/api/admin/export/orders')
def admin_export_orders():
    if not check_admin(): return jsonify({'error': 'Non autorisé'}), 403
    import io, csv
    if db is not None:
        rows = list(db.orders.find({}).sort('date', -1))
        for r in rows: r['_id'] = str(r['_id'])
    else:
        rows = sorted(ORDERS_STORE, key=lambda x: x.get('date', ''), reverse=True)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Client', 'Téléphone', 'Ville',
                     'Total (MAD)', 'Livraison', 'Paiement', 'Statut', 'Réf. commande'])
    for o in rows:
        c = o.get('client') or {}
        writer.writerow([
            str(o.get('_id', ''))[-8:].upper(),
            str(o.get('date', ''))[:10],
            (c.get('firstName', '') + ' ' + c.get('lastName', '')).strip() or c.get('name', '—') or '—',
            c.get('phone', '—') or '—',
            c.get('city', '—') or '—',
            o.get('total', 0),
            (o.get('delivery') or {}).get('label', '—'),
            o.get('payment', '—'),
            o.get('status', 'Nouvelle'),
            o.get('orderRef', '—')
        ])
    from flask import Response
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': 'attachment; filename=commandes-jamali.csv'}
    )


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


@app.route('/api/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    global _LEGAL_SETTINGS
    if request.method == 'POST':
        if not check_admin():
            return jsonify({'error': 'Non autorisé'}), 403
        _LEGAL_SETTINGS = request.json or {}
        # Also persist in localStorage via client (returned so client can store)
        return jsonify({'ok': True, 'settings': _LEGAL_SETTINGS})
    return jsonify(_LEGAL_SETTINGS)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
