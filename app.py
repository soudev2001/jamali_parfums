import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__, static_folder=".")
CORS(app, supports_credentials=True)

# ================= CONFIGURATION =================
MONGO_URI      = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SMTP_SERVER    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", 587))
SMTP_USER      = os.getenv("SMTP_USERNAME")
SMTP_PASS      = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin2026")
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Simple in-memory token store (reset on container restart)
_admin_tokens: set = set()

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
        "Reponds toujours en Francais, inclus des expressions en Darija marocaine (Salam, Merhaba, Bghiti chi haja). "
        "Reste concis (2-3 phrases maximum)."
    )
    model = genai.GenerativeModel(
        "gemini-2.5-flash-preview-09-2025",
        system_instruction=system_prompt
    )
    print("[OK] Google Gemini configure")

# ================= AUTH MIDDLEWARE =================
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if not token or token not in _admin_tokens:
            return jsonify({"error": "Non autorise"}), 401
        return f(*args, **kwargs)
    return decorated

# ================= HELPERS =================
def doc_to_dict(doc):
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc

def send_order_email(subject, body_text, body_html=None):
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

# ================= STATIC FILES =================
@app.route("/", methods=["GET"])
def home():
    return send_from_directory(".", "index.html")

@app.route("/admin", methods=["GET"])
def admin_page():
    return send_from_directory(".", "admin.html")

# ================= PUBLIC API =================
@app.route("/api/products", methods=["GET"])
def get_public_products():
    """Catalogue public — utilisé par le storefront."""
    if db is None:
        return jsonify([])
    docs = list(db.products.find({"available": {"$ne": False}}).sort("createdAt", 1))
    return jsonify([doc_to_dict(p) for p in docs])

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "db": db is not None, "ai": model is not None})

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
        result = db.orders.insert_one({
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
    txt_body = f"NOUVELLE COMMANDE JAMALI PARFUM\nID: {order_id}\n\nArticles:\n{lines}\n\nTOTAL: {total} MAD"
    html_rows = "".join(
        f"<li>{i.get('quantity')}x <b>{i.get('name')}</b> (Ref: {i.get('reference')})</li>"
        for i in cart
    )
    html_body = f"""<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
      <h2 style="color:#d97706;border-bottom:2px solid #d97706;padding-bottom:8px">Nouvelle commande &mdash; Jamali Parfum</h2>
      <p><b>ID Commande :</b> <code>{order_id}</code></p>
      <ul style="line-height:1.8">{html_rows}</ul>
      <p style="font-size:1.3em;background:#fef3c7;padding:12px;border-radius:6px"><b>TOTAL : {total} MAD</b></p>
    </div>"""
    send_order_email("Nouvelle commande Jamali Parfum !", txt_body, html_body)
    return jsonify({"success": True, "message": "Commande traitee.", "order_id": order_id})

# ================= ADMIN AUTH =================
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    pwd  = data.get("password", "")
    if pwd == ADMIN_PASSWORD:
        token = secrets.token_urlsafe(32)
        _admin_tokens.add(token)
        return jsonify({"token": token, "ok": True})
    return jsonify({"error": "Mot de passe incorrect"}), 401

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    token = request.headers.get("X-Admin-Token", "")
    _admin_tokens.discard(token)
    return jsonify({"ok": True})

@app.route("/api/admin/change-password", methods=["POST"])
@admin_required
def change_password():
    global ADMIN_PASSWORD
    data    = request.get_json(silent=True) or {}
    new_pwd = data.get("new_password", "")
    if len(new_pwd) < 6:
        return jsonify({"error": "Mot de passe trop court (min 6 caracteres)"}), 400
    ADMIN_PASSWORD = new_pwd
    # Persist to .env
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            content = f.read()
        lines = content.splitlines()
        found = False
        for i, line in enumerate(lines):
            if line.startswith("ADMIN_PASSWORD="):
                lines[i] = f"ADMIN_PASSWORD={new_pwd}"
                found = True
        if not found:
            lines.append(f"ADMIN_PASSWORD={new_pwd}")
        with open(env_path, "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as e:
        print(f"[WARN] Cannot update .env: {e}")
    return jsonify({"ok": True})

# ================= ADMIN STATS =================
@app.route("/api/admin/stats", methods=["GET"])
@admin_required
def get_stats():
    if db is None:
        return jsonify({"products": 0, "orders": 0, "revenue": 0, "new_orders": 0})
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total"}}}]
    rev_result = list(db.orders.aggregate(pipeline))
    revenue = rev_result[0]["total"] if rev_result else 0
    return jsonify({
        "products":   db.products.count_documents({}),
        "orders":     db.orders.count_documents({}),
        "revenue":    revenue,
        "new_orders": db.orders.count_documents({"status": "Nouvelle"})
    })

# ================= ADMIN PRODUCTS CRUD =================
@app.route("/api/admin/products", methods=["GET"])
@admin_required
def get_products():
    if db is None:
        return jsonify([])
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    q     = request.args.get("q", "")
    filt  = {}
    if q:
        filt = {"$or": [
            {"name":      {"$regex": q, "$options": "i"}},
            {"brand":     {"$regex": q, "$options": "i"}},
            {"reference": {"$regex": q, "$options": "i"}},
        ]}
    total = db.products.count_documents(filt)
    docs  = list(db.products.find(filt).skip((page-1)*limit).limit(limit))
    return jsonify({"products": [doc_to_dict(p) for p in docs], "total": total, "page": page})

@app.route("/api/admin/products", methods=["POST"])
@admin_required
def create_product():
    if db is None:
        return jsonify({"error": "DB not connected"}), 503
    data = request.get_json(silent=True) or {}
    for field in ["reference", "name", "category", "price"]:
        if not data.get(field):
            return jsonify({"error": f"Champ requis: {field}"}), 400
    data.setdefault("stock",       0)
    data.setdefault("available",   True)
    data.setdefault("tags",        [])
    data.setdefault("type",        "EDP")
    data.setdefault("volume",      "50ml")
    data.setdefault("image",       "")
    data.setdefault("brand",       "")
    data.setdefault("isBestseller", False)
    data["createdAt"] = datetime.utcnow()
    data.pop("_id", None)
    result = db.products.insert_one(data)
    return jsonify({"ok": True, "_id": str(result.inserted_id)}), 201

@app.route("/api/admin/products/<product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    if db is None:
        return jsonify({"error": "DB not connected"}), 503
    data = request.get_json(silent=True) or {}
    data.pop("_id", None)
    data["updatedAt"] = datetime.utcnow()
    try:
        result = db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "Produit non trouve"}), 404
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/admin/products/<product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    if db is None:
        return jsonify({"error": "DB not connected"}), 503
    try:
        result = db.products.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Produit non trouve"}), 404
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ================= ADMIN ORDERS =================
@app.route("/api/admin/orders", methods=["GET"])
@admin_required
def get_orders():
    if db is None:
        return jsonify([])
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    docs  = list(db.orders.find().sort("date", -1).skip((page-1)*limit).limit(limit))
    return jsonify([doc_to_dict(o) for o in docs])

@app.route("/api/admin/orders/<order_id>", methods=["PUT"])
@admin_required
def update_order(order_id):
    if db is None:
        return jsonify({"error": "DB not connected"}), 503
    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status requis"}), 400
    try:
        result = db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updatedAt": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Commande non trouvee"}), 404
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
