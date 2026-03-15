# 2>NUL & @cls & @echo off & cd /d "%~dp0" & echo Lancement de la creation du projet Jamali Parfum... & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Command -ScriptBlock ([ScriptBlock]::Create((Get-Content -LiteralPath '%~nx0' -Raw)))" & echo. & pause & exit /b

Write-Host "Création de .env..." -ForegroundColor Yellow
$envContent = @'
# Configuration du Serveur
PORT=5000
FLASK_ENV=development

# Base de données MongoDB (Cloud MongoDB Atlas ou Local)
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/jamali_db?retryWrites=true&w=majority

# API Google Gemini (Pour le Chatbot)
GEMINI_API_KEY=votre_cle_api_gemini_ici

# API Twilio (Pour l'envoi de messages WhatsApp)
TWILIO_ACCOUNT_SID=votre_twilio_sid
TWILIO_AUTH_TOKEN=votre_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
ADMIN_WHATSAPP_NUMBER=whatsapp:+212700762849

# Configuration Email (Ex: Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
ADMIN_EMAIL=admin@jamaliparfum.com
'@
Set-Content -Path ".\.env" -Value $envContent -Encoding UTF8

Write-Host "Création de requirements.txt..." -ForegroundColor Yellow
$reqContent = @'
Flask==3.0.0
flask-cors==4.0.0
pymongo==4.6.1
google-generativeai==0.3.1
twilio==8.11.0
python-dotenv==1.0.0
'@
Set-Content -Path ".\requirements.txt" -Value $reqContent -Encoding UTF8

Write-Host "Création de app.py..." -ForegroundColor Yellow
$appContent = @'
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
        print("✅ Connecté à MongoDB")
except Exception as e:
    print(f"❌ Erreur MongoDB : {e}")

if GEMINI_API_KEY and "votre_cle" not in GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    system_prompt = """
    Tu es l'assistant virtuel officiel de 'Jamali Parfum', une boutique de parfums de luxe au Maroc (Casablanca).
    Tu dois être chaleureux, professionnel et vendeur.
    Nos parfums coûtent 150 MAD l'unité. La livraison est disponible partout au Maroc sous 24h/48h avec paiement à la livraison (Cash on Delivery).
    Réponds toujours en Français, mais n'hésite pas à inclure des expressions polies en Darija marocaine (ex: Salam, Merhaba, Bghiti chi haja).
    Reste concis (2-3 phrases maximum).
    """
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025', system_instruction=system_prompt)
    print("✅ API Google Gemini configurée")
else:
    model = None

if TWILIO_ACCOUNT_SID and "votre_twilio" not in TWILIO_ACCOUNT_SID:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print("✅ Twilio configuré")
else:
    twilio_client = None

# ================= ROUTES =================
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Serveur Jamali Parfum en ligne 🟢"})

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
            return jsonify({"reply": "Désolé, problème technique. Contactez-nous sur WhatsApp."}), 500
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
    msg_body = f"🔥 NOUVELLE COMMANDE JAMALI PARFUM 🔥\nID: {order_id}\n\nArticles:\n{items_text}\n\nTOTAL: {total} MAD"

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

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'@
Set-Content -Path ".\app.py" -Value $appContent -Encoding UTF8

Write-Host "Création de index.html..." -ForegroundColor Yellow
$htmlContent = @'
<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jamali Parfum | عطور جمالي - Catalogue Officiel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: { amber: { 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 900: '#78350f' }, rose: { 500: '#f43f5e', 600: '#e11d48' }, blue: { 500: '#3b82f6', 600: '#2563eb' } },
                    fontFamily: { serif: ['Georgia', 'serif'], arabic: ['"Amiri"', 'serif'] }
                }
            }
        }
    </script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
        html { scroll-behavior: smooth; }
        .view-section { display: none; animation: fadeIn 0.4s ease-in-out; }
        .view-section.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #171717; }
        ::-webkit-scrollbar-thumb { background: #d97706; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #f59e0b; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        #chat-window.show { display: flex; animation: slideUp 0.3s ease-out forwards; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
    </style>
</head>
<body class="bg-neutral-50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100 transition-colors duration-300 min-h-screen flex flex-col relative">

    <div id="toast" class="fixed bottom-4 left-4 md:left-auto md:right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-2xl transform translate-y-20 opacity-0 transition-all duration-300 z-50 flex items-center">
        <i class="ph ph-check-circle text-xl mr-2"></i><span id="toast-message">Message</span>
    </div>

    <!-- Floating Actions -->
    <div class="fixed bottom-6 right-6 flex flex-col items-end space-y-3 z-40">
        <button onclick="startTour()" class="w-12 h-12 bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 rounded-full shadow-lg flex items-center justify-center hover:bg-amber-500 hover:text-white dark:hover:bg-amber-600 transition-all group relative" title="Relancer la visite">
            <i class="ph-fill ph-play-circle text-2xl group-hover:scale-110 transition-transform"></i>
            <span class="absolute right-14 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">Démo Interactive</span>
        </button>
        <button onclick="toggleChat()" class="w-16 h-16 bg-black dark:bg-amber-600 text-white dark:text-black rounded-full shadow-2xl flex items-center justify-center hover:scale-110 transition-transform relative group">
            <i class="ph-fill ph-chat-teardrop-dots text-3xl"></i>
            <span class="absolute top-0 right-0 w-4 h-4 bg-red-500 border-2 border-white dark:border-neutral-900 rounded-full animate-pulse"></span>
        </button>
    </div>

    <!-- Chat Window -->
    <div id="chat-window" class="fixed bottom-28 right-6 w-[90vw] md:w-80 h-[450px] bg-white dark:bg-neutral-900 rounded-2xl shadow-2xl border border-neutral-200 dark:border-neutral-800 hidden flex-col z-50 overflow-hidden">
        <div class="bg-black dark:bg-neutral-950 text-white p-4 flex justify-between items-center border-b border-neutral-800">
            <div class="flex items-center">
                <div class="w-8 h-8 bg-amber-600 rounded-full flex items-center justify-center mr-3"><i class="ph-fill ph-robot text-xl"></i></div>
                <div><h3 class="font-bold text-sm">Assistant Jamali</h3><p class="text-[10px] text-amber-500 flex items-center"><span class="w-2 h-2 bg-green-500 rounded-full mr-1"></span> En ligne</p></div>
            </div>
            <button onclick="toggleChat()" class="text-neutral-400 hover:text-white transition"><i class="ph ph-x text-xl"></i></button>
        </div>
        <div id="chat-messages" class="flex-1 p-4 overflow-y-auto bg-neutral-50 dark:bg-neutral-900 flex flex-col space-y-3">
            <div class="flex items-start">
                <div class="bg-neutral-200 dark:bg-neutral-800 text-neutral-900 dark:text-white px-4 py-2 rounded-2xl rounded-tl-none text-sm max-w-[85%] shadow-sm">
                    Bonjour ! 👋 Bienvenue chez Jamali Parfum. Comment puis-je vous aider aujourd'hui ?<br><br><span class="font-arabic text-xs" dir="rtl">مرحباً بك في عطور جمالي. كيف يمكنني مساعدتك اليوم؟</span>
                </div>
            </div>
        </div>
        <div class="p-3 bg-white dark:bg-neutral-950 border-t border-neutral-200 dark:border-neutral-800 flex items-center">
            <input type="text" id="chat-input" onkeypress="handleChatKeyPress(event)" placeholder="Votre message..." class="flex-1 bg-neutral-100 dark:bg-neutral-900 text-neutral-900 dark:text-white px-4 py-2 rounded-full text-sm outline-none focus:ring-1 focus:ring-amber-500 transition-shadow">
            <button onclick="sendChatMessage()" class="ml-2 w-10 h-10 bg-amber-600 text-black rounded-full flex items-center justify-center hover:bg-amber-500 transition"><i class="ph-fill ph-paper-plane-right"></i></button>
        </div>
    </div>

    <!-- Tour Overlay -->
    <div id="tour-overlay" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-[60] hidden flex-col items-center justify-center p-4">
        <div class="bg-white dark:bg-neutral-900 rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl relative">
            <div id="tour-content" class="p-8 text-center relative z-10"></div>
            <div id="tour-dots" class="flex justify-center space-x-2 pb-6"></div>
        </div>
        <button onclick="endTour()" class="mt-6 text-white/70 hover:text-white transition underline font-bold text-sm tracking-wider uppercase">Passer l'introduction (Skip)</button>
    </div>

    <div class="bg-amber-600 text-black text-center text-xs sm:text-sm py-2 font-bold flex justify-center items-center space-x-4 px-4 z-30 relative">
        <span>🇲🇦 Livraison partout au Maroc - الدفع عند الاستلام</span>
    </div>

    <!-- Header -->
    <header class="sticky top-0 z-30 bg-white/95 dark:bg-black/95 backdrop-blur-md shadow-sm dark:shadow-neutral-900 border-b border-neutral-200 dark:border-neutral-800 transition-colors">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-20">
                <div class="flex items-center cursor-pointer group" onclick="switchView('store')">
                    <div class="w-10 h-10 bg-gradient-to-br from-amber-400 to-amber-600 rounded-full flex items-center justify-center mr-3 shadow-lg"><span class="font-serif font-bold text-black text-xl">JP</span></div>
                    <div><h1 class="text-2xl font-serif font-bold tracking-widest text-black dark:text-amber-500">JAMALI</h1><p class="text-[10px] tracking-[0.2em] text-neutral-500 uppercase font-arabic">عطور</p></div>
                </div>
                <nav class="hidden md:flex space-x-8 items-center">
                    <a href="#store-catalog" onclick="switchView('store')" class="text-sm font-bold hover:text-amber-600 transition">Catalogue / الكتالوج</a>
                    <a href="#top-ventes" onclick="switchView('store')" class="text-sm font-bold hover:text-amber-600 transition">Top Ventes / المبيعات</a>
                    <a href="#about-us" onclick="switchView('store')" class="text-sm font-bold hover:text-amber-600 transition">À Propos / من نحن</a>
                    <a href="#contact" onclick="switchView('store')" class="text-sm font-bold hover:text-amber-600 transition">Contact / اتصل بنا</a>
                </nav>
                <div class="flex items-center space-x-2 sm:space-x-4">
                    <button onclick="toggleDarkMode()" class="p-2 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors"><i id="theme-icon" class="ph ph-sun text-xl"></i></button>
                    <button id="nav-cart-btn" onclick="switchView('cart')" class="relative flex items-center p-2 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors">
                        <i class="ph ph-shopping-cart text-2xl"></i><span id="cart-badge" class="absolute top-0 right-0 bg-amber-600 text-black text-[10px] font-bold rounded-full h-4 w-4 flex items-center justify-center translate-x-1 -translate-y-1 hidden">0</span>
                    </button>
                    <button onclick="attemptAdminLogin()" class="p-2 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors text-neutral-400 hover:text-amber-500"><i class="ph ph-gear-six text-xl"></i></button>
                </div>
            </div>
        </div>
    </header>

    <main class="flex-grow relative z-10">
        <!-- Store -->
        <div id="view-store" class="view-section active">
            <div class="relative bg-black h-[400px] flex items-center justify-center overflow-hidden">
                <div class="absolute inset-0 opacity-50 dark:opacity-40">
                    <img src="https://images.unsplash.com/photo-1616949755610-8c9bbc08f138?auto=format&fit=crop&q=80&w=2000" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-gradient-to-t from-neutral-50 dark:from-neutral-950 to-transparent"></div>
                </div>
                <div class="relative z-10 text-center px-4 mt-10">
                    <h2 class="text-5xl md:text-7xl font-serif text-white mb-4 drop-shadow-2xl">L'Élégance Absolue</h2>
                    <h3 class="text-3xl md:text-4xl font-arabic text-amber-400 drop-shadow-lg mb-6" dir="rtl">الأناقة المطلقة في كل قطرة</h3>
                    <a href="#store-catalog" class="inline-block bg-amber-600 text-black font-bold uppercase tracking-wider px-8 py-3 rounded-full hover:bg-amber-500 transition shadow-lg">Découvrir | اكتشف</a>
                </div>
            </div>

            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12" id="store-catalog">
                <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 bg-white dark:bg-neutral-900 p-4 rounded-2xl shadow-sm border border-neutral-200 dark:border-neutral-800 sticky top-20 z-20">
                    <div class="relative w-full md:w-1/3">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><i class="ph ph-magnifying-glass text-neutral-400"></i></div>
                        <input type="text" id="search-input" onkeyup="handleSearch()" placeholder="Rechercher un parfum..." class="block w-full pl-10 pr-3 py-2 border border-neutral-300 dark:border-neutral-700 rounded-xl leading-5 bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-white placeholder-neutral-500 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 sm:text-sm">
                    </div>
                    <div class="flex space-x-2 bg-neutral-100 dark:bg-neutral-950 p-1 rounded-xl overflow-x-auto hide-scrollbar w-full md:w-auto">
                        <button onclick="setCategory('Tous')" id="tab-Tous" class="cat-tab px-4 py-2 text-sm font-bold rounded-lg bg-amber-600 text-black shadow">Tous</button>
                        <button onclick="setCategory('Homme')" id="tab-Homme" class="cat-tab px-4 py-2 text-sm font-bold rounded-lg text-neutral-500">Homme</button>
                        <button onclick="setCategory('Femme')" id="tab-Femme" class="cat-tab px-4 py-2 text-sm font-bold rounded-lg text-neutral-500">Femme</button>
                        <button onclick="setCategory('Oriental')" id="tab-Oriental" class="cat-tab px-4 py-2 text-sm font-bold rounded-lg text-neutral-500">Oriental</button>
                    </div>
                </div>

                <div id="top-ventes" class="mb-16">
                    <div class="flex items-center mb-6"><h3 class="text-2xl font-serif font-bold mr-4">Top Ventes <span class="text-amber-600">Jamali</span></h3><div class="h-px bg-neutral-200 dark:bg-neutral-800 flex-1"></div></div>
                    <div id="top-ventes-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"></div>
                </div>

                <div class="flex items-center mb-6" id="catalog-title-container"><h3 class="text-xl font-serif font-bold text-neutral-500 mr-4">Notre Catalogue Complet</h3><div class="h-px bg-neutral-200 dark:bg-neutral-800 flex-1"></div></div>
                <div id="product-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"></div>
                <div id="no-results" class="hidden text-center py-12 text-neutral-500 font-arabic text-lg">Aucun parfum trouvé. لا يوجد عطر بهذا الاسم.</div>
            </div>

            <section id="about-us" class="bg-white dark:bg-neutral-900 py-16 border-t border-neutral-200 dark:border-neutral-800">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                    <div>
                        <h2 class="text-3xl font-serif font-bold mb-4">Qui sommes-nous ?</h2>
                        <h3 class="text-2xl font-arabic text-amber-600 mb-6" dir="rtl">من نحن؟</h3>
                        <p class="text-neutral-600 dark:text-neutral-400 mb-4 leading-relaxed">Jamali Parfum est votre destination numéro un pour les parfums d'exception au Maroc. Nous sélectionnons rigoureusement les meilleures inspirations des grandes marques mondiales et les senteurs orientales les plus pures.</p>
                        <p class="text-neutral-600 dark:text-neutral-400 font-arabic leading-relaxed text-right" dir="rtl">عطور جمالي هي وجهتك الأولى للعطور الاستثنائية في المغرب. نختار بعناية أفضل الإلهامات من العلامات التجارية العالمية الرائدة وأرقى الروائح الشرقية لنقدم لك جودة لا مثيل لها.</p>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <img src="https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&q=80&w=400" class="rounded-2xl shadow-lg w-full h-48 object-cover">
                        <img src="https://images.unsplash.com/photo-1615397347318-620251781297?auto=format&fit=crop&q=80&w=400" class="rounded-2xl shadow-lg w-full h-48 object-cover mt-8">
                    </div>
                </div>
            </section>
        </div>

        <!-- Cart View -->
        <div id="view-cart" class="view-section max-w-4xl mx-auto px-4 py-12">
            <div class="flex items-center justify-between mb-8">
                <button onclick="switchView('store')" class="text-neutral-500 hover:text-black dark:hover:text-white flex items-center transition font-bold"><i class="ph ph-arrow-left mr-2"></i> Continuer les achats</button>
                <div class="text-right"><h2 class="text-3xl font-serif">Panier</h2></div>
            </div>
            <div id="cart-container"></div>
        </div>

        <!-- Admin View -->
        <div id="view-admin" class="view-section max-w-7xl mx-auto px-4 py-12">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 bg-white dark:bg-neutral-900 p-6 rounded-2xl shadow-sm border border-neutral-200 dark:border-neutral-800">
                <div><h2 class="text-2xl font-serif font-bold text-amber-600 flex items-center"><i class="ph-fill ph-shield-check mr-2"></i> CMS Administration</h2></div>
                <div class="flex items-center space-x-4 mt-4 md:mt-0">
                    <div class="flex items-center bg-neutral-100 dark:bg-neutral-950 px-3 py-2 rounded-lg border border-neutral-200 dark:border-neutral-800">
                        <i class="ph ph-whatsapp text-green-500 mr-2"></i><input type="text" id="admin-phone" onchange="savePhone()" class="bg-transparent border-none outline-none w-32 font-mono text-sm font-bold" placeholder="212600000000">
                    </div>
                    <button onclick="logoutAdmin()" class="bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white px-4 py-2 rounded-lg font-bold text-sm transition">Quitter</button>
                </div>
            </div>
            <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-800 shadow-sm overflow-hidden">
                <div class="overflow-x-auto max-h-[600px]"><table class="w-full text-left text-sm"><tbody id="admin-table-body" class="divide-y divide-neutral-200 dark:divide-neutral-800"></tbody></table></div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer id="contact" class="bg-neutral-950 text-neutral-400 pt-16 pb-8 border-t border-amber-900/30 mt-auto relative z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12 text-center md:text-left">
                <div><h2 class="text-2xl font-serif font-bold text-white tracking-widest mb-4">JAMALI</h2><p class="text-sm font-arabic" dir="rtl">المرجع الأول للعطور البديلة والشرقية في المغرب.</p></div>
                <div class="flex flex-col items-center md:items-start"><h3 class="text-white font-bold uppercase tracking-wider mb-4">Contact</h3>
                    <ul class="space-y-3 text-sm">
                        <li><a href="#" class="flex items-center hover:text-white"><i class="ph-fill ph-whatsapp-logo text-green-500 text-xl mr-3"></i><span class="font-mono text-lg font-bold" id="footer-phone">+212 700 76 28 49</span></a></li>
                        <li class="flex items-center"><i class="ph-fill ph-map-pin text-amber-500 text-xl mr-3"></i><span>Ain Chock - Casablanca</span></li>
                    </ul>
                </div>
            </div>
        </div>
    </footer>

    <!-- Scripts -->
    <script>
        const rawDataMen = [{ b: "Chanel", items: ["040-Style Allure", "041-Style Bleu"] }, { b: "Dior", items: ["044-Style Sauvage"] }];
        const rawDataWomen = [{ b: "Yves Saint Laurent", items: ["214-Style Black Opium", "216-Style Libre"] }];
        const rawDataOriental = [{ b: "Oud & Orientaux", items: ["096-Style العود", "089-Style سحر الكلمات"] }];
        const images = ['https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&q=80&w=400'];

        let products = []; let bestSellers = [];
        const mapData = (dataArray, cat) => {
            dataArray.forEach(g => g.items.forEach((item, i) => {
                const s = item.split('-');
                products.push({ id: s[0], reference: s[0], name: s[1].replace('Style ', ''), brand: g.b, category: cat, price: 150, stock: 10, image: images[0], isBestseller: Math.random() > 0.5 });
            }));
        };
        mapData(rawDataMen, 'Homme'); mapData(rawDataWomen, 'Femme'); mapData(rawDataOriental, 'Oriental');
        bestSellers = products.filter(p => p.isBestseller).slice(0, 4);

        let cart = []; let currentCategory = 'Tous'; let searchQuery = ''; let adminPhone = '212700762849'; let isAdmin = false;

        function init() {
            renderStore(); document.getElementById('admin-phone').value = adminPhone;
            document.getElementById('footer-phone').innerText = adminPhone.replace(/(\d{3})(\d{3})(\d{2})(\d{2})/, "+$1 $2 $3 $4");
            if(localStorage.getItem('jamali_tour_done') !== 'true') setTimeout(startTour, 1000);
        }

        function switchView(id) { document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active')); document.getElementById(`view-${id}`).classList.add('active'); if(id === 'cart') renderCart(); }
        function toggleDarkMode() { document.documentElement.classList.toggle('dark'); }
        function showToast(msg) { const t = document.getElementById('toast'); document.getElementById('toast-message').innerText = msg; t.classList.remove('translate-y-20', 'opacity-0'); setTimeout(() => t.classList.add('translate-y-20', 'opacity-0'), 3000); }

        function setCategory(cat) { currentCategory = cat; renderStore(); document.querySelectorAll('.cat-tab').forEach(el => el.classList.remove('bg-amber-600', 'text-black')); document.getElementById(`tab-${cat}`).classList.add('bg-amber-600', 'text-black'); }
        function handleSearch() { searchQuery = document.getElementById('search-input').value.toLowerCase(); renderStore(); }

        function generateProductCardHTML(p) {
            return `<div class="bg-white dark:bg-neutral-900 rounded-2xl p-4 shadow-sm border border-neutral-100 dark:border-neutral-800">
                <img src="${p.image}" class="w-full h-40 object-cover rounded-xl mb-4">
                <div class="flex justify-between items-center mb-2"><span class="text-xs text-amber-500 font-bold">#${p.reference}</span><span class="font-bold">${p.price} MAD</span></div>
                <h4 class="font-serif text-lg">${p.name}</h4><p class="text-[10px] text-neutral-500 uppercase mt-1">${p.brand}</p>
                <button onclick="addToCart('${p.id}')" class="mt-4 w-full bg-amber-600 text-black font-bold py-2 rounded-lg hover:bg-amber-500 transition">Ajouter au Panier</button>
            </div>`;
        }

        function renderStore() {
            let filtered = products;
            if(currentCategory !== 'Tous') filtered = filtered.filter(p => p.category === currentCategory);
            if(searchQuery) filtered = filtered.filter(p => p.name.toLowerCase().includes(searchQuery));
            document.getElementById('product-grid').innerHTML = filtered.map(p => generateProductCardHTML(p)).join('');
            document.getElementById('top-ventes-grid').innerHTML = bestSellers.map(p => generateProductCardHTML(p)).join('');
        }

        function addToCart(id) { const p = products.find(x => x.id === id); const ex = cart.find(x => x.id === id); if(ex) ex.quantity++; else cart.push({...p, quantity: 1}); updateBadge(); showToast('Ajouté'); }
        function removeFromCart(id) { cart = cart.filter(x => x.id !== id); updateBadge(); renderCart(); }
        function updateQty(id, d) { const i = cart.find(x => x.id === id); if(i){ i.quantity+=d; if(i.quantity<=0) removeFromCart(id); else renderCart(); updateBadge(); } }
        function updateBadge() { const b = document.getElementById('cart-badge'); const sum = cart.reduce((s,i)=>s+i.quantity,0); if(sum>0){ b.innerText=sum; b.classList.remove('hidden'); } else b.classList.add('hidden'); }

        function renderCart() {
            const container = document.getElementById('cart-container');
            if(!cart.length) return container.innerHTML = `<p class="text-center py-20 text-neutral-500">Panier vide.</p>`;
            const total = cart.reduce((s,i)=>s+(i.price*i.quantity),0);
            container.innerHTML = `<ul class="divide-y dark:divide-neutral-800">` + cart.map(i => `
                <li class="py-4 flex justify-between items-center">
                    <div><b>${i.name}</b><br><span class="text-xs text-neutral-500">${i.brand}</span></div>
                    <div class="flex items-center space-x-4"><button onclick="updateQty('${i.id}',-1)" class="px-2">-</button><span>${i.quantity}</span><button onclick="updateQty('${i.id}',1)" class="px-2">+</button><button onclick="removeFromCart('${i.id}')" class="text-red-500 ml-4"><i class="ph ph-trash"></i></button></div>
                </li>`).join('') + `</ul><div class="mt-6 flex justify-between items-center"><span class="font-bold text-2xl">Total: ${total} MAD</span><button onclick="checkoutWhatsApp()" class="bg-[#25D366] text-white px-6 py-3 rounded-full font-bold">Commander via WhatsApp</button></div>`;
        }

        async function checkoutWhatsApp() {
            if(!cart.length) return;
            const total = cart.reduce((s,i)=>s+(i.price*i.quantity),0);
            try { await fetch('http://localhost:5000/api/order', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({cart, total}) }); } catch(e){}
            let msg = `Nouvelle commande :\n\n` + cart.map(i => `- ${i.quantity}x ${i.name} (${i.reference})`).join('\n') + `\n\nTotal: ${total} MAD`;
            window.open(`https://wa.me/${adminPhone}?text=${encodeURIComponent(msg)}`, '_blank');
        }

        /* Tour Logic */
        let currentTourStep = 0;
        const tourData = [
            { v: 'store', icon: 'ph-hand-waving', title: 'Bienvenue', text: 'Découvrez notre nouvelle plateforme e-commerce Jamali Parfum.' },
            { v: 'store', icon: 'ph-magnifying-glass', title: 'Recherche', text: 'Utilisez les filtres pour trouver votre parfum.' },
            { v: 'cart', icon: 'ph-shopping-cart', title: 'Panier Facile', text: 'Validez votre commande via WhatsApp.' }
        ];
        function startTour() { currentTourStep=0; document.getElementById('tour-overlay').classList.remove('hidden'); document.getElementById('tour-overlay').classList.add('flex'); renderTourStep(); }
        function renderTourStep() {
            const step = tourData[currentTourStep]; switchView(step.v);
            document.getElementById('tour-content').innerHTML = `
                <div class="w-16 h-16 bg-amber-500/20 text-amber-500 rounded-full flex items-center justify-center mx-auto mb-6"><i class="ph-fill ${step.icon} text-3xl"></i></div>
                <h3 class="text-2xl font-bold mb-4">${step.title}</h3><p class="text-neutral-500 mb-8">${step.text}</p>
                <div class="flex space-x-4"><button onclick="nextTourStep()" class="flex-1 py-3 bg-amber-600 text-black font-bold rounded-xl">${currentTourStep === tourData.length - 1 ? 'Terminer' : 'Suivant'}</button></div>
            `;
        }
        function nextTourStep() { if(currentTourStep < tourData.length-1) { currentTourStep++; renderTourStep(); } else endTour(); }
        function endTour() { document.getElementById('tour-overlay').classList.add('hidden'); document.getElementById('tour-overlay').classList.remove('flex'); localStorage.setItem('jamali_tour_done','true'); switchView('store'); }

        /* Chat Logic */
        let chatOpen = false;
        function toggleChat() { chatOpen=!chatOpen; const w=document.getElementById('chat-window'); if(chatOpen){ w.classList.remove('hidden'); w.classList.add('show'); } else { w.classList.remove('show'); w.classList.add('hidden'); } }
        function handleChatKeyPress(e) { if(e.key === 'Enter') sendChatMessage(); }
        function appendChatMessage(text, isUser=false) {
            const c = document.getElementById('chat-messages'); const d = document.createElement('div');
            d.className = `flex ${isUser ? 'justify-end' : 'items-start'} mt-2`;
            d.innerHTML = `<div class="px-4 py-2 rounded-2xl text-sm max-w-[85%] ${isUser ? 'bg-amber-600 text-white rounded-tr-none' : 'bg-neutral-200 dark:bg-neutral-800 rounded-tl-none'}">${text.replace(/\n/g,'<br>')}</div>`;
            c.appendChild(d); c.scrollTop = c.scrollHeight;
        }
        async function sendChatMessage() {
            const inp = document.getElementById('chat-input'); const txt = inp.value.trim(); if(!txt) return;
            appendChatMessage(txt, true); inp.value = '';

            const c = document.getElementById('chat-messages'); const l = document.createElement('div');
            l.className = "flex items-start mt-2"; l.innerHTML = `<div class="bg-neutral-200 dark:bg-neutral-800 text-neutral-500 px-4 py-2 rounded-2xl rounded-tl-none text-sm animate-pulse">En train d'écrire...</div>`;
            c.appendChild(l); c.scrollTop = c.scrollHeight;

            try {
                const res = await fetch('http://localhost:5000/api/chat', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({message: txt}) });
                c.removeChild(l);
                if(res.ok) { const data = await res.json(); appendChatMessage(data.reply, false); }
                else throw new Error();
            } catch(e) {
                if(c.contains(l)) c.removeChild(l);
                appendChatMessage("Le serveur IA est hors ligne. Vous testez en local sans lancer `python app.py`.", false);
            }
        }

        window.onload = init;
    </script>
</body>
</html>
'@
Set-Content -Path ".\index.html" -Value $htmlContent -Encoding UTF8

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ Toutes les créations sont terminées !" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Pour démarrer le serveur Backend :"
Write-Host "1. Remplissez vos clés dans le fichier .env"
Write-Host "2. Dans ce dossier tapez : pip install -r requirements.txt"
Write-Host "3. Puis tapez : python app.py"
Write-Host ""
Write-Host "Ouvrez le fichier index.html généré dans votre navigateur web."