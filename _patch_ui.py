"""
Patch script - UI/UX upgrade:
  Phase 1: Images Unsplash aléatoires
  Phase 2: Pagination 24/page
  Phase 3: Spinner transition
  Phase 4: Drawer détail + volume
  Phase 5: Checkout 4 étapes + livraison
  Phase 6: Stripe frontend
  Phase 7: Facture PDF jsPDF
"""
import re, shutil, sys

shutil.copy('index.html', 'index.html.bak3')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

patches_ok = []
patches_fail = []

def patch(name, old, new):
    global html
    if old in html:
        html = html.replace(old, new, 1)
        patches_ok.append(name)
    else:
        patches_fail.append(name)

# ─────────────────────────────────────────────────
# P1: CSS additions (spinner, drawer, checkout steps)
# ─────────────────────────────────────────────────
patch('CSS_spinner_drawer_checkout',
    '        html.sepia .logo-img { filter: sepia(1) saturate(1.4) brightness(.85); }\n    </style>',
    '''        html.sepia .logo-img { filter: sepia(1) saturate(1.4) brightness(.85); }
        /* ── Spinner ── */
        #page-spinner{position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:9999;display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .2s}
        #page-spinner.active{opacity:1;pointer-events:all}
        .spinner-ring{width:54px;height:54px;border:4px solid rgba(147,51,234,.2);border-top-color:#9333ea;border-radius:50%;animation:jp-spin .8s linear infinite}
        @keyframes jp-spin{to{transform:rotate(360deg)}}
        /* ── Drawer produit ── */
        #product-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:1000;opacity:0;pointer-events:none;transition:opacity .3s}
        #product-backdrop.open{opacity:1;pointer-events:all}
        #product-drawer{position:fixed;top:0;right:0;height:100vh;width:100%;max-width:480px;z-index:1001;transform:translateX(100%);transition:transform .35s cubic-bezier(.4,0,.2,1);overflow-y:auto;box-shadow:-8px 0 40px rgba(0,0,0,.5)}
        #product-drawer.open{transform:translateX(0)}
        /* ── Checkout ── */
        .step-dot{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;transition:all .3s;flex-shrink:0}
        .step-dot.active{background:#9333ea;color:#fff;box-shadow:0 0 0 4px rgba(147,51,234,.25)}
        .step-dot.done{background:#10b981;color:#fff}
        .step-dot.pending{background:#374151;color:#6b7280}
        .checkout-panel{animation:fadeIn .3s ease}
        .delivery-card,.payment-card{border:2px solid #374151;border-radius:16px;padding:16px;cursor:pointer;transition:all .2s}
        .delivery-card:hover,.payment-card:hover{border-color:#7e22ce}
        .delivery-card.selected,.payment-card.selected{border-color:#9333ea;background:rgba(147,51,234,.1)}
        #stripe-card-element{background:rgba(255,255,255,.05);border:1px solid #374151;border-radius:12px;padding:16px;min-height:48px}
        /* ── Vol buttons ── */
        .vol-btn{flex:1;display:flex;flex-direction:column;align-items:center;padding:10px 6px;border-radius:12px;border:2px solid #374151;font-weight:700;font-size:13px;cursor:pointer;transition:all .2s;background:transparent}
        .vol-btn:hover{border-color:#7e22ce}
    </style>''')

# ─────────────────────────────────────────────────
# P2: Add Stripe.js + jsPDF CDN before </head>
# ─────────────────────────────────────────────────
patch('CDN_stripe_jspdf',
    '</head>',
    '''    <script src="https://js.stripe.com/v3/"></script>
    <script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>
</head>''')

# ─────────────────────────────────────────────────
# P3: Add checkout view between cart and admin
# ─────────────────────────────────────────────────
patch('HTML_checkout_view',
    '            <div id="cart-container"></div>\n        </div>\n\n        <!-- Admin View -->',
    '''            <div id="cart-container"></div>
        </div>

        <!-- Checkout View -->
        <div id="view-checkout" class="view-section dark:bg-neutral-950 bg-neutral-50 min-h-screen">
            <div class="max-w-3xl mx-auto px-4 py-8">
                <button onclick="checkoutPrev()" class="mb-6 text-neutral-500 hover:text-primary-500 flex items-center transition font-bold text-sm">
                    <i class="ph ph-arrow-left mr-2"></i><span id="co-back-label">Retour au panier</span>
                </button>
                <!-- Step indicator -->
                <div class="flex items-center justify-center mb-3">
                    <div class="step-dot active" id="step-dot-1">1</div>
                    <div class="flex-1 h-0.5 mx-2 bg-neutral-700 transition-all duration-300" id="step-line-1"></div>
                    <div class="step-dot pending" id="step-dot-2">2</div>
                    <div class="flex-1 h-0.5 mx-2 bg-neutral-700 transition-all duration-300" id="step-line-2"></div>
                    <div class="step-dot pending" id="step-dot-3">3</div>
                    <div class="flex-1 h-0.5 mx-2 bg-neutral-700 transition-all duration-300" id="step-line-3"></div>
                    <div class="step-dot pending" id="step-dot-4">✓</div>
                </div>
                <div class="flex justify-between text-xs dark:text-neutral-500 text-neutral-400 mb-8 px-1">
                    <span>Coordonnées</span><span>Livraison</span><span>Paiement</span><span>Confirmation</span>
                </div>
                <!-- Step 1: Client info -->
                <div id="checkout-step-1" class="checkout-panel">
                    <div class="dark:bg-neutral-900 bg-white rounded-2xl p-6 shadow-sm border dark:border-neutral-800 border-neutral-200">
                        <h2 class="text-xl font-serif font-bold dark:text-white text-neutral-900 mb-6 flex items-center gap-2">
                            <i class="ph ph-user text-primary-500 text-2xl"></i>Vos Coordonnées
                        </h2>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div><label class="block text-sm font-medium dark:text-neutral-300 text-neutral-700 mb-1">Prénom *</label>
                            <input id="co-firstName" type="text" placeholder="Mohamed" class="w-full px-4 py-3 rounded-xl border dark:border-neutral-700 border-neutral-300 dark:bg-neutral-950 bg-neutral-50 dark:text-white text-neutral-900 focus:ring-2 focus:ring-primary-500 outline-none"></div>
                            <div><label class="block text-sm font-medium dark:text-neutral-300 text-neutral-700 mb-1">Nom *</label>
                            <input id="co-lastName" type="text" placeholder="Alaoui" class="w-full px-4 py-3 rounded-xl border dark:border-neutral-700 border-neutral-300 dark:bg-neutral-950 bg-neutral-50 dark:text-white text-neutral-900 focus:ring-2 focus:ring-primary-500 outline-none"></div>
                            <div><label class="block text-sm font-medium dark:text-neutral-300 text-neutral-700 mb-1">Téléphone *</label>
                            <input id="co-phone" type="tel" placeholder="+212 6XX XXX XXX" class="w-full px-4 py-3 rounded-xl border dark:border-neutral-700 border-neutral-300 dark:bg-neutral-950 bg-neutral-50 dark:text-white text-neutral-900 focus:ring-2 focus:ring-primary-500 outline-none"></div>
                            <div><label class="block text-sm font-medium dark:text-neutral-300 text-neutral-700 mb-1">Ville *</label>
                            <select id="co-city" class="w-full px-4 py-3 rounded-xl border dark:border-neutral-700 border-neutral-300 dark:bg-neutral-950 bg-neutral-50 dark:text-white text-neutral-900 focus:ring-2 focus:ring-primary-500 outline-none">
                                <option value="">Choisir une ville...</option>
                                <option>Casablanca</option><option>Rabat</option><option>Fès</option>
                                <option>Marrakech</option><option>Tanger</option><option>Agadir</option>
                                <option>Meknès</option><option>Oujda</option><option>Kénitra</option><option>Autre</option>
                            </select></div>
                            <div class="sm:col-span-2"><label class="block text-sm font-medium dark:text-neutral-300 text-neutral-700 mb-1">Adresse de livraison *</label>
                            <input id="co-address" type="text" placeholder="N° rue, quartier, immeuble..." class="w-full px-4 py-3 rounded-xl border dark:border-neutral-700 border-neutral-300 dark:bg-neutral-950 bg-neutral-50 dark:text-white text-neutral-900 focus:ring-2 focus:ring-primary-500 outline-none"></div>
                        </div>
                    </div>
                    <div class="mt-6 flex justify-end">
                        <button onclick="checkoutNext()" class="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-full transition flex items-center gap-2 shadow-lg">
                            Livraison <i class="ph ph-arrow-right"></i>
                        </button>
                    </div>
                </div>
                <!-- Step 2: Delivery -->
                <div id="checkout-step-2" class="checkout-panel hidden">
                    <div class="dark:bg-neutral-900 bg-white rounded-2xl p-6 shadow-sm border dark:border-neutral-800 border-neutral-200">
                        <h2 class="text-xl font-serif font-bold dark:text-white text-neutral-900 mb-6 flex items-center gap-2">
                            <i class="ph ph-truck text-primary-500 text-2xl"></i>Options de Livraison
                        </h2>
                        <div class="space-y-4">
                            <div id="del-express" class="delivery-card" onclick="selectDelivery('express')">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3"><span class="text-3xl">⚡</span>
                                        <div><p class="font-bold dark:text-white text-neutral-900">Casablanca Express</p>
                                        <p class="text-sm dark:text-neutral-400 text-neutral-600">Livraison en 24 heures</p></div>
                                    </div><span class="font-bold text-gold-400 text-xl">30 MAD</span>
                                </div>
                            </div>
                            <div id="del-national" class="delivery-card" onclick="selectDelivery('national')">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3"><span class="text-3xl">📦</span>
                                        <div><p class="font-bold dark:text-white text-neutral-900">Maroc National</p>
                                        <p class="text-sm dark:text-neutral-400 text-neutral-600">2 à 3 jours ouvrables</p></div>
                                    </div><span class="font-bold text-gold-400 text-xl">50 MAD</span>
                                </div>
                            </div>
                            <div id="del-pickup" class="delivery-card" onclick="selectDelivery('pickup')">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3"><span class="text-3xl">🏪</span>
                                        <div><p class="font-bold dark:text-white text-neutral-900">Retrait Gratuit</p>
                                        <p class="text-sm dark:text-neutral-400 text-neutral-600">Ain Chock, Casablanca</p></div>
                                    </div><span class="font-bold text-emerald-400 text-xl">Gratuit</span>
                                </div>
                            </div>
                        </div>
                        <div class="mt-6 p-4 bg-primary-600/10 rounded-xl border border-primary-800/30 flex justify-between items-center">
                            <span class="dark:text-neutral-400 text-neutral-600 text-sm">Total avec livraison</span>
                            <span id="co-delivery-total" class="font-bold text-xl text-gold-400">— MAD</span>
                        </div>
                    </div>
                    <div class="mt-6 flex justify-between">
                        <button onclick="checkoutPrev()" class="px-6 py-3 border dark:border-neutral-700 border-neutral-300 dark:text-neutral-300 text-neutral-700 font-bold rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-800 flex items-center gap-2 transition">
                            <i class="ph ph-arrow-left"></i>Retour
                        </button>
                        <button onclick="checkoutNext()" class="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-full transition flex items-center gap-2 shadow-lg">
                            Paiement <i class="ph ph-arrow-right"></i>
                        </button>
                    </div>
                </div>
                <!-- Step 3: Payment -->
                <div id="checkout-step-3" class="checkout-panel hidden">
                    <div class="dark:bg-neutral-900 bg-white rounded-2xl p-6 shadow-sm border dark:border-neutral-800 border-neutral-200">
                        <h2 class="text-xl font-serif font-bold dark:text-white text-neutral-900 mb-6 flex items-center gap-2">
                            <i class="ph ph-credit-card text-primary-500 text-2xl"></i>Mode de Paiement
                        </h2>
                        <div class="space-y-4">
                            <div id="pay-stripe" class="payment-card" onclick="selectPayment('stripe')">
                                <div class="flex items-center gap-3">
                                    <i class="ph ph-credit-card text-3xl text-primary-400"></i>
                                    <div><p class="font-bold dark:text-white text-neutral-900">Carte Bancaire (Stripe)</p>
                                    <p class="text-sm dark:text-neutral-400 text-neutral-600">Paiement sécurisé — Visa, Mastercard</p></div>
                                </div>
                            </div>
                            <div id="stripe-fields" class="hidden px-4 pb-2 space-y-2">
                                <label class="block text-sm font-medium dark:text-neutral-300 text-neutral-700">Numéro de carte</label>
                                <div id="stripe-card-element"></div>
                                <p class="text-xs dark:text-neutral-500 text-neutral-400">🔒 Paiement sécurisé par Stripe · Carte test : <span class="font-mono">4242 4242 4242 4242</span></p>
                            </div>
                            <div id="pay-cod" class="payment-card" onclick="selectPayment('cod')">
                                <div class="flex items-center gap-3">
                                    <i class="ph ph-money text-3xl text-emerald-400"></i>
                                    <div><p class="font-bold dark:text-white text-neutral-900">Paiement à la Livraison</p>
                                    <p class="text-sm dark:text-neutral-400 text-neutral-600">Payez en espèces à la réception — الدفع عند الاستلام</p></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-6 flex justify-between">
                        <button onclick="checkoutPrev()" class="px-6 py-3 border dark:border-neutral-700 border-neutral-300 dark:text-neutral-300 text-neutral-700 font-bold rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-800 flex items-center gap-2 transition">
                            <i class="ph ph-arrow-left"></i>Retour
                        </button>
                        <button onclick="checkoutNext()" class="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-full transition flex items-center gap-2 shadow-lg">
                            Confirmer <i class="ph ph-check-circle text-xl"></i>
                        </button>
                    </div>
                </div>
                <!-- Step 4: Confirmation (rendered dynamically) -->
                <div id="checkout-step-4" class="checkout-panel hidden"></div>
            </div>
        </div>

        <!-- Admin View -->''')

# ─────────────────────────────────────────────────
# P4: Spinner + Drawer HTML before <!-- Scripts -->
# ─────────────────────────────────────────────────
patch('HTML_spinner_drawer',
    '    <!-- Scripts -->',
    '''    <!-- Page Spinner -->
    <div id="page-spinner"><div class="spinner-ring"></div></div>
    <!-- Product Backdrop -->
    <div id="product-backdrop" onclick="closeProduct()"></div>
    <!-- Product Drawer -->
    <div id="product-drawer"></div>

    <!-- Scripts -->''')

# ─────────────────────────────────────────────────
# P5: Add UNSPLASH_POOL + productImageUrl before generateProductCardHTML
# ─────────────────────────────────────────────────
patch('JS_unsplash_pool',
    '        function brandInitials(brand) {',
    '''        // ── Unsplash photo pool (parfums) ──────────────────────────
        const UNSPLASH_POOL = [
            "1503921151906-3d8a62cb9614","1541643600914-78b084683702",
            "1594035910387-fea47794261f","1615397347318-620251781297",
            "1587017539504-67cfbaf6b20b","1557660570-9a3ce3f73d21",
            "1592842039956-c63b30c18bde","1590736969955-71cc94f3e8bb",
            "1599305148791-b41ba1eea3eb","1558618666-fcd25c85cd64",
            "1524638431109-93d95c968f03","1516979187895-2e265e9c0b5d",
            "1610461888750-10bfc601b4a6","1548693086-28b1faad7e64",
            "1619994501688-2de1a40d4a38","1629218527337-f8a9eb6e7aad",
            "1563170351-be9e0be2a4ea","1603204577878-baf7bbf8869b",
            "1616949755610-8c9bbc08f138","1547793548-c01a42f36a25"
        ];
        function productImageUrl(ref) {
            const hash = (ref||'').split('').reduce((a,c)=>a+c.charCodeAt(0),0);
            const id = UNSPLASH_POOL[hash % UNSPLASH_POOL.length];
            return `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=400&q=75`;
        }

        // ── Pagination ──────────────────────────────────────────────
        const PAGE_SIZE = 24;
        let currentPage = 1;

        function brandInitials(brand) {''')

# ─────────────────────────────────────────────────
# P6: Update generateProductCardHTML - Unsplash + drawer + 2 buttons
# ─────────────────────────────────────────────────
patch('JS_generateProductCard',
    '''        function generateProductCardHTML(p) {
            const placeholder = brandPlaceholder(p.brand || '', p.reference || '');
            const imgSrc = p.image || placeholder;
            return `<div class="rounded-2xl overflow-hidden shadow-md border border-primary-900/30 dark:border-primary-800/20 hover:shadow-primary-600/20 hover:shadow-lg transition-all group" style="background:linear-gradient(135deg,#1e1052 0%,#2d1b6b 50%,#3b0764 100%)">
                <div class="relative h-44 overflow-hidden bg-purple-950/50">
                    <img src="${imgSrc}" alt="${p.name}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                         onerror="this.src=\'${placeholder}\'">
                    ${p.isBestseller ? '<span class="absolute top-2 left-2 bg-gold-500 text-black text-[10px] font-bold px-2 py-0.5 rounded-full">⭐ TOP</span>' : ''}
                    <span class="absolute top-2 right-2 ${(p.stock||0)>0 ? 'bg-emerald-500/80' : 'bg-red-500/80'} text-white text-[9px] font-bold px-2 py-0.5 rounded-full">${(p.stock||0)>0 ? 'Dispo' : 'Rupture'}</span>
                </div>
                <div class="p-4">
                    <div class="flex justify-between items-start mb-1">
                        <span class="text-[10px] text-primary-300 font-mono font-bold">#${p.reference||\'\'}</span>
                        <span class="font-bold text-lg text-gold-400">${p.price||150} MAD</span>
                    </div>
                    <h4 class="font-serif text-white text-base leading-tight mb-1">${p.name}</h4>
                    <p class="text-[11px] text-primary-300/70 uppercase tracking-wider mb-3">${p.brand||\'\'}</p>
                    <button onclick="addToCart(\'${p.id||p.reference||\'\'}')" class="w-full bg-primary-600 hover:bg-primary-500 text-white font-bold py-2 rounded-xl transition text-sm">
                        <i class="ph ph-shopping-cart mr-1"></i>Ajouter au Panier
                    </button>
                </div>
            </div>`;
        }''',
    '''        function generateProductCardHTML(p) {
            const placeholder = brandPlaceholder(p.brand || '', p.reference || '');
            const imgSrc = p.image || productImageUrl(p.reference || p.id || '');
            const pid = p.id || p.reference || '';
            return `<div class="rounded-2xl overflow-hidden shadow-md border border-primary-900/30 dark:border-primary-800/20 hover:shadow-primary-600/30 hover:shadow-xl transition-all group cursor-pointer" style="background:linear-gradient(135deg,#1e1052 0%,#2d1b6b 50%,#3b0764 100%)" onclick="openProduct(\'${pid}\')">
                <div class="relative h-48 overflow-hidden bg-purple-950/50">
                    <img src="${imgSrc}" alt="${p.name}" class="w-full h-full object-cover group-hover:scale-108 transition-transform duration-500"
                         onerror="this.src=\'${placeholder}\'">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    ${p.isBestseller ? '<span class="absolute top-2 left-2 bg-gold-500 text-black text-[10px] font-bold px-2 py-0.5 rounded-full">⭐ TOP</span>' : ''}
                    <span class="absolute top-2 right-2 ${(p.stock||0)>0 ? 'bg-emerald-500/80' : 'bg-red-500/80'} text-white text-[9px] font-bold px-2 py-0.5 rounded-full">${(p.stock||0)>0 ? 'Dispo' : 'Rupture'}</span>
                    <div class="absolute bottom-2 left-0 right-0 flex justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <span class="text-white text-xs bg-black/60 px-3 py-1 rounded-full"><i class="ph ph-eye mr-1"></i>Voir détails</span>
                    </div>
                </div>
                <div class="p-4">
                    <div class="flex justify-between items-start mb-1">
                        <span class="text-[10px] text-primary-300 font-mono font-bold">#${p.reference||\'\'}</span>
                        <span class="font-bold text-lg text-gold-400">${p.price||150} MAD</span>
                    </div>
                    <h4 class="font-serif text-white text-base leading-tight mb-1">${p.name}</h4>
                    <p class="text-[11px] text-primary-300/70 uppercase tracking-wider mb-3">${p.brand||\'\'}</p>
                    <div class="flex gap-2">
                        <button onclick="event.stopPropagation();addToCart(\'${pid}\')" class="flex-1 bg-primary-600 hover:bg-primary-500 text-white font-bold py-2 rounded-xl transition text-sm flex items-center justify-center gap-1">
                            <i class="ph ph-shopping-cart"></i>Panier
                        </button>
                        <button onclick="event.stopPropagation();openProduct(\'${pid}\')" class="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition border border-white/10">
                            <i class="ph ph-eye text-sm"></i>
                        </button>
                    </div>
                </div>
            </div>`;
        }''')

# ─────────────────────────────────────────────────
# P7: Update renderStore with pagination
# ─────────────────────────────────────────────────
patch('JS_renderStore',
    '''        function renderStore() {
            let filtered = products;
            if(currentCategory !== 'Tous') filtered = filtered.filter(p => p.category === currentCategory);
            if(searchQuery) filtered = filtered.filter(p => p.name.toLowerCase().includes(searchQuery));
            document.getElementById('product-grid').innerHTML = filtered.map(p => generateProductCardHTML(p)).join('');
            document.getElementById('top-ventes-grid').innerHTML = bestSellers.map(p => generateProductCardHTML(p)).join('');
        }''',
    '''        function renderStore() {
            let filtered = products;
            if(currentCategory !== 'Tous') filtered = filtered.filter(p => p.category === currentCategory);
            if(searchQuery) filtered = filtered.filter(p =>
                p.name.toLowerCase().includes(searchQuery) ||
                (p.brand||'').toLowerCase().includes(searchQuery)
            );
            const visible = filtered.slice(0, currentPage * PAGE_SIZE);
            const remaining = filtered.length - visible.length;
            document.getElementById('product-grid').innerHTML = visible.map(p => generateProductCardHTML(p)).join('');
            document.getElementById('top-ventes-grid').innerHTML = bestSellers.map(p => generateProductCardHTML(p)).join('');
            document.getElementById('no-results').classList.toggle('hidden', filtered.length > 0);
            // Load-more button
            let moreBtn = document.getElementById('load-more-btn');
            if (!moreBtn) {
                moreBtn = document.createElement('div');
                moreBtn.id = 'load-more-btn';
                moreBtn.className = 'text-center mt-10';
                document.getElementById('product-grid').insertAdjacentElement('afterend', moreBtn);
            }
            if (remaining > 0) {
                moreBtn.innerHTML = `<button onclick="loadMoreProducts()" class="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-full transition shadow-lg inline-flex items-center gap-2"><i class="ph ph-arrow-down"></i>Voir ${Math.min(remaining, PAGE_SIZE)} produits de plus <span class="text-primary-300 text-sm">(${filtered.length - visible.length} restants)</span></button>`;
            } else {
                moreBtn.innerHTML = filtered.length > PAGE_SIZE ? `<p class="text-neutral-500 text-sm">${filtered.length} parfums affichés</p>` : '';
            }
        }
        function loadMoreProducts() {
            currentPage++;
            renderStore();
            document.getElementById('product-grid').lastElementChild?.scrollIntoView({behavior:'smooth', block:'nearest'});
        }''')

# ─────────────────────────────────────────────────
# P8: Update setCategory + handleSearch to reset page
# ─────────────────────────────────────────────────
patch('JS_setCategory_reset',
    "        function setCategory(cat) { currentCategory = cat; renderStore(); document.querySelectorAll('.cat-tab').forEach(el => el.classList.remove('bg-primary-600', 'text-white')); document.getElementById(`tab-${cat}`).classList.add('bg-primary-600', 'text-white'); }",
    "        function setCategory(cat) { currentCategory = cat; currentPage = 1; renderStore(); document.querySelectorAll('.cat-tab').forEach(el => el.classList.remove('bg-primary-600', 'text-white')); document.getElementById(`tab-${cat}`).classList.add('bg-primary-600', 'text-white'); }")

patch('JS_handleSearch_reset',
    "        function handleSearch() { searchQuery = document.getElementById('search-input').value.toLowerCase(); renderStore(); }",
    "        function handleSearch() { searchQuery = document.getElementById('search-input').value.toLowerCase(); currentPage = 1; renderStore(); }")

# ─────────────────────────────────────────────────
# P9: Update switchView with spinner
# ─────────────────────────────────────────────────
patch('JS_switchView_spinner',
    "        function switchView(id) { document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active')); document.getElementById(`view-${id}`).classList.add('active'); if(id === 'cart') renderCart(); }",
    '''        function showSpinner() { document.getElementById('page-spinner').classList.add('active'); }
        function hideSpinner() { document.getElementById('page-spinner').classList.remove('active'); }
        function switchView(id) {
            showSpinner();
            setTimeout(() => {
                document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
                const target = document.getElementById(`view-${id}`);
                if (target) target.classList.add('active');
                if (id === 'cart') renderCart();
                if (id === 'checkout') renderCheckoutStep();
                hideSpinner();
                window.scrollTo({top: 0, behavior: 'smooth'});
            }, 180);
        }''')

# ─────────────────────────────────────────────────
# P10: Fix addToCart toast mojibake
# ─────────────────────────────────────────────────
patch('JS_addToCart_toast',
    "function addToCart(id) { const p = products.find(x => x.id === id); const ex = cart.find(x => x.id === id); if(ex) ex.quantity++; else cart.push({...p, quantity: 1}); updateBadge(); showToast('AjoutÃ©'); }",
    "function addToCart(id) { const p = products.find(x => x.id === id || x.reference === id); if(!p) return; const ex = cart.find(x => x.id === id); if(ex) ex.quantity++; else cart.push({...p, id, quantity: 1}); updateBadge(); showToast(p.name + ' ajouté !'); }")

# ─────────────────────────────────────────────────
# P11: Update renderCart - replace WhatsApp only button with Commander
# ─────────────────────────────────────────────────
patch('JS_renderCart_checkout',
    '''`</ul><div class="mt-6 flex justify-between items-center"><span class="font-bold text-2xl">Total: ${total} MAD</span><button onclick="checkoutWhatsApp()" class="bg-[#25D366] text-white px-6 py-3 rounded-full font-bold">Commander via WhatsApp</button></div>`;''',
    '''`</ul>
            <div class="mt-6 pt-4 border-t dark:border-neutral-800 flex flex-col sm:flex-row justify-between items-center gap-4">
                <div>
                    <p class="text-sm dark:text-neutral-400 text-neutral-600">${cart.reduce((s,i)=>s+i.quantity,0)} article(s)</p>
                    <span class="font-bold text-2xl dark:text-white">Total: ${total} MAD</span>
                </div>
                <div class="flex gap-3 flex-wrap justify-center">
                    <a href="https://wa.me/${adminPhone}?text=${encodeURIComponent('Bonjour Jamali Parfum, je souhaite commander : ' + cart.map(i=>i.quantity+'x '+i.name).join(', ') + ' — Total: '+total+' MAD')}" target="_blank" class="flex items-center gap-2 bg-[#25D366] text-white px-5 py-3 rounded-full font-bold text-sm">
                        <i class="ph-fill ph-whatsapp-logo text-xl"></i>WhatsApp
                    </a>
                    <button onclick="goToCheckout()" class="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-3 rounded-full font-bold text-sm transition shadow-lg">
                        <i class="ph ph-shopping-bag-open text-xl"></i>Commander
                    </button>
                </div>
            </div>`;''')

# ─────────────────────────────────────────────────
# P12: Replace checkoutWhatsApp + add all new JS
# ─────────────────────────────────────────────────
NEW_JS = r'''        // ── Checkout ──────────────────────────────────────────────────────
        let checkoutStep = 1;
        let checkoutData = {};
        const DELIVERY_OPTIONS = [
            { id:'express', label:'Casablanca Express', desc:'24h', price:30 },
            { id:'national', label:'Maroc National',    desc:'2-3j', price:50 },
            { id:'pickup',   label:'Retrait Gratuit',   desc:'Ain Chock', price:0 }
        ];

        function goToCheckout() {
            if (!cart.length) return;
            checkoutStep = 1;
            checkoutData = {};
            switchView('checkout');
        }
        function renderCheckoutStep() {
            for (let i = 1; i <= 4; i++) {
                const dot = document.getElementById('step-dot-' + i);
                if (!dot) continue;
                dot.className = 'step-dot ' + (i < checkoutStep ? 'done' : i === checkoutStep ? 'active' : 'pending');
                const line = document.getElementById('step-line-' + i);
                if (line) line.className = 'flex-1 h-0.5 mx-2 transition-all duration-300 ' + (i < checkoutStep ? 'bg-emerald-500' : 'bg-neutral-700');
            }
            document.querySelectorAll('.checkout-panel').forEach(el => el.classList.add('hidden'));
            const panel = document.getElementById('checkout-step-' + checkoutStep);
            if (panel) panel.classList.remove('hidden');
            const backLabel = document.getElementById('co-back-label');
            if (backLabel) backLabel.textContent = checkoutStep === 1 ? 'Retour au panier' : 'Étape précédente';
            if (checkoutStep === 3) setTimeout(mountStripe, 120);
            if (checkoutStep === 4) renderConfirmation();
        }
        function checkoutNext() {
            if (checkoutStep === 1) {
                const fields = ['co-firstName','co-lastName','co-phone','co-address','co-city'];
                for (const id of fields) {
                    if (!document.getElementById(id)?.value?.trim()) { showToast('Veuillez remplir tous les champs'); return; }
                }
                checkoutData.client = {
                    firstName: document.getElementById('co-firstName').value.trim(),
                    lastName:  document.getElementById('co-lastName').value.trim(),
                    phone:     document.getElementById('co-phone').value.trim(),
                    address:   document.getElementById('co-address').value.trim(),
                    city:      document.getElementById('co-city').value.trim()
                };
            } else if (checkoutStep === 2) {
                if (!checkoutData.delivery) { showToast('Choisissez une option de livraison'); return; }
            } else if (checkoutStep === 3) {
                if (!checkoutData.payment) { showToast('Choisissez un mode de paiement'); return; }
                if (checkoutData.payment === 'stripe') { confirmStripePayment(); return; }
                // COD: place order then confirm
                placeOrder().then(() => { checkoutStep = 4; renderCheckoutStep(); });
                return;
            }
            checkoutStep++;
            renderCheckoutStep();
        }
        function checkoutPrev() {
            if (checkoutStep > 1) { checkoutStep--; renderCheckoutStep(); }
            else switchView('cart');
        }
        function selectDelivery(id) {
            const opt = DELIVERY_OPTIONS.find(o => o.id === id);
            checkoutData.delivery = opt;
            document.querySelectorAll('.delivery-card').forEach(c => c.classList.remove('selected'));
            document.getElementById('del-' + id)?.classList.add('selected');
            const base = cart.reduce((s,i) => s + (i.price * i.quantity), 0);
            const el = document.getElementById('co-delivery-total');
            if (el) el.textContent = (base + (opt?.price||0)) + ' MAD';
        }
        function selectPayment(method) {
            checkoutData.payment = method;
            document.querySelectorAll('.payment-card').forEach(c => c.classList.remove('selected'));
            document.getElementById('pay-' + method)?.classList.add('selected');
            document.getElementById('stripe-fields').classList.toggle('hidden', method !== 'stripe');
        }

        // ── Stripe ────────────────────────────────────────────────────
        let _stripe = null, _stripeElements = null, _stripeCard = null;
        async function initStripe() {
            if (_stripe) return;
            try {
                const r = await fetch('/api/stripe-key');
                if (!r.ok) return;
                const { publishable_key } = await r.json();
                if (!publishable_key || publishable_key.startsWith('pk_test_replace')) return;
                _stripe = Stripe(publishable_key);
                _stripeElements = _stripe.elements();
            } catch(e) { console.log('Stripe not configured'); }
        }
        function mountStripe() {
            initStripe().then(() => {
                if (!_stripe || !_stripeElements) return;
                if (_stripeCard) { _stripeCard.destroy(); _stripeCard = null; }
                const container = document.getElementById('stripe-card-element');
                if (!container) return;
                _stripeCard = _stripeElements.create('card', {
                    style: { base: { color:'#e5e7eb', fontFamily:'Georgia,serif', fontSize:'15px', '::placeholder':{color:'#6b7280'} } }
                });
                _stripeCard.mount('#stripe-card-element');
            });
        }
        async function confirmStripePayment() {
            if (!_stripe || !_stripeCard) {
                showToast('Stripe non configuré — utilisez le paiement à la livraison');
                return;
            }
            showSpinner();
            try {
                const total = cart.reduce((s,i) => s + (i.price * i.quantity), 0) + (checkoutData.delivery?.price || 0);
                const r = await fetch('/api/create-payment-intent', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({ amount: total, currency: 'eur' })
                });
                const { client_secret, error: apiError } = await r.json();
                if (apiError) { hideSpinner(); showToast('Erreur : ' + apiError); return; }
                const result = await _stripe.confirmCardPayment(client_secret, {
                    payment_method: { card: _stripeCard, billing_details: {
                        name: (checkoutData.client?.firstName||'') + ' ' + (checkoutData.client?.lastName||'')
                    }}
                });
                hideSpinner();
                if (result.error) { showToast(result.error.message); return; }
                checkoutData.paymentIntent = result.paymentIntent;
                checkoutData.paymentStatus = 'paid';
                await placeOrder();
                checkoutStep = 4;
                renderCheckoutStep();
            } catch(e) { hideSpinner(); showToast('Erreur de paiement'); }
        }
        async function placeOrder() {
            const total = cart.reduce((s,i) => s + (i.price * i.quantity), 0) + (checkoutData.delivery?.price || 0);
            checkoutData.total = total;
            checkoutData.items = [...cart];
            checkoutData.orderRef = 'JML-' + Date.now().toString(36).toUpperCase().slice(-6);
            try {
                await fetch('/api/order', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({
                        cart, total,
                        client: checkoutData.client,
                        delivery: checkoutData.delivery,
                        payment: checkoutData.payment,
                        orderRef: checkoutData.orderRef
                    })
                });
            } catch(e) {}
        }
        function renderConfirmation() {
            const panel = document.getElementById('checkout-step-4');
            if (!panel) return;
            const total = cart.reduce((s,i) => s + (i.price * i.quantity), 0) + (checkoutData.delivery?.price || 0);
            const waMsg = encodeURIComponent('Commande Jamali Parfum confirmée. Réf: ' + (checkoutData.orderRef || ''));
            panel.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <i class="ph ph-check-circle text-5xl text-emerald-400"></i>
                    </div>
                    <h2 class="text-2xl font-serif font-bold dark:text-white text-neutral-900 mb-2">Commande confirmée !</h2>
                    <p class="text-primary-400 font-mono font-bold text-lg mb-1">${checkoutData.orderRef || ''}</p>
                    <p class="dark:text-neutral-400 text-neutral-600 mb-8">Merci ${checkoutData.client?.firstName||''}, votre commande est bien enregistrée.</p>
                    <div class="dark:bg-neutral-900 bg-neutral-100 rounded-2xl p-5 mb-6 text-left border dark:border-neutral-800 border-neutral-200">
                        <h3 class="font-bold dark:text-white text-neutral-900 mb-3">Récapitulatif de commande</h3>
                        ${cart.map(i=>`<div class="flex justify-between text-sm py-1.5 border-b dark:border-neutral-800 border-neutral-200">
                            <span class="dark:text-neutral-300 text-neutral-700">${i.quantity}× ${i.name}${i.volume?' ('+i.volume+')':''}</span>
                            <span class="text-gold-500 font-bold">${i.price*i.quantity} MAD</span>
                        </div>`).join('')}
                        <div class="flex justify-between text-sm py-1.5 dark:text-neutral-400 text-neutral-600">
                            <span>Livraison (${checkoutData.delivery?.label||''})</span>
                            <span>${checkoutData.delivery?.price===0?'Gratuit':(checkoutData.delivery?.price||0)+' MAD'}</span>
                        </div>
                        <div class="flex justify-between font-bold text-xl pt-3 dark:text-white text-neutral-900">
                            <span>Total TTC</span><span class="text-gold-400">${total} MAD</span>
                        </div>
                    </div>
                    <div class="flex flex-col sm:flex-row gap-3 justify-center">
                        <button onclick="generateInvoicePDF()" class="flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-full transition shadow-lg">
                            <i class="ph ph-file-pdf text-xl"></i>Télécharger la Facture PDF
                        </button>
                        <a href="https://wa.me/${adminPhone}?text=${waMsg}" target="_blank" class="flex items-center justify-center gap-2 px-6 py-3 bg-[#25D366] text-white font-bold rounded-full transition">
                            <i class="ph-fill ph-whatsapp-logo text-xl"></i>Confirmer WhatsApp
                        </a>
                    </div>
                    <button onclick="cart=[];updateBadge();switchView('store');" class="mt-5 text-sm dark:text-neutral-500 text-neutral-400 underline">Retourner au catalogue</button>
                </div>`;
        }

        // ── Product Drawer ─────────────────────────────────────────────
        let drawerProduct = null;
        let selectedVolume = '30ml';
        function getVolumePrice(base, vol) {
            if (vol === '50ml')  return (base||150) + 10;
            if (vol === '100ml') return (base||150) + 30;
            return (base||150);
        }
        function openProduct(id) {
            const p = products.find(x => x.id === id || x.reference === id);
            if (!p) return;
            drawerProduct = p; selectedVolume = '30ml';
            const placeholder = brandPlaceholder(p.brand||'', p.reference||'');
            const imgSrc = p.image || productImageUrl(p.reference || p.id || '');
            const pid = p.id || p.reference || '';
            const drawer = document.getElementById('product-drawer');
            drawer.innerHTML = `
                <div class="dark:bg-neutral-900 bg-white min-h-full flex flex-col">
                    <div class="relative h-72 overflow-hidden flex-shrink-0">
                        <img src="${imgSrc}" alt="${p.name}" class="w-full h-full object-cover" onerror="this.src='${placeholder}'">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
                        <button onclick="closeProduct()" class="absolute top-4 right-4 w-10 h-10 bg-black/60 hover:bg-black/90 text-white rounded-full flex items-center justify-center transition z-10">
                            <i class="ph ph-x text-xl"></i>
                        </button>
                        ${p.isBestseller ? '<span class="absolute top-4 left-4 bg-gold-500 text-black text-xs font-bold px-3 py-1 rounded-full">⭐ TOP VENTE</span>' : ''}
                    </div>
                    <div class="p-6 flex-1 flex flex-col">
                        <span class="text-xs font-mono text-primary-400 mb-1">#${p.reference||''}</span>
                        <h2 class="text-2xl font-serif font-bold dark:text-white text-neutral-900 mb-1">${p.name}</h2>
                        <p class="text-sm text-primary-400 uppercase tracking-widest mb-3">${p.brand||''}</p>
                        <div class="flex flex-wrap gap-2 mb-5">
                            <span class="text-xs px-3 py-1 rounded-full font-bold ${(p.stock||0)>0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
                                ${(p.stock||0)>0 ? '✓ En stock' : '✗ Rupture'}
                            </span>
                            <span class="text-xs px-3 py-1 rounded-full bg-primary-600/20 text-primary-300">${p.category||''}</span>
                        </div>
                        <p class="text-sm font-bold dark:text-neutral-300 text-neutral-700 mb-3">Choisir le volume :</p>
                        <div class="flex gap-3 mb-5">
                            ${[['30ml',0],['50ml',10],['100ml',30]].map(([v,e]) => `
                            <button id="vol-${v}" onclick="selectVolume('${v}','${pid}')" class="vol-btn dark:text-white text-neutral-900 ${v==='30ml'?'ring-2 ring-primary-500 border-primary-600 bg-primary-600/10':'border-neutral-700'}">
                                <span>${v}</span><span class="text-xs text-gold-400 mt-1">${(p.price||150)+e} MAD</span>
                            </button>`).join('')}
                        </div>
                        <div class="flex justify-between items-center p-4 bg-primary-600/10 rounded-2xl border border-primary-800/30 mb-5">
                            <span class="dark:text-neutral-300 text-neutral-700 text-sm">Prix sélectionné</span>
                            <span id="drawer-price" class="text-2xl font-bold text-gold-400">${p.price||150} MAD</span>
                        </div>
                        <button onclick="addToCartFromDrawer()" class="w-full bg-primary-600 hover:bg-primary-500 text-white font-bold py-4 rounded-2xl transition flex items-center justify-center gap-2 text-base mt-auto">
                            <i class="ph ph-shopping-cart text-xl"></i>Ajouter au Panier
                        </button>
                        <p class="text-center text-xs dark:text-neutral-500 text-neutral-400 mt-3">🇲🇦 Livraison partout au Maroc · الدفع عند الاستلام</p>
                    </div>
                </div>`;
            document.getElementById('product-backdrop').classList.add('open');
            drawer.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
        function closeProduct() {
            document.getElementById('product-backdrop').classList.remove('open');
            document.getElementById('product-drawer').classList.remove('open');
            document.body.style.overflow = '';
            drawerProduct = null;
        }
        function selectVolume(vol, pid) {
            selectedVolume = vol;
            document.querySelectorAll('.vol-btn').forEach(b => {
                b.classList.remove('ring-2','ring-primary-500','border-primary-600','bg-primary-600/10');
                b.classList.add('border-neutral-700');
            });
            const active = document.getElementById('vol-' + vol);
            if (active) {
                active.classList.add('ring-2','ring-primary-500','border-primary-600','bg-primary-600/10');
                active.classList.remove('border-neutral-700');
            }
            if (drawerProduct) {
                const price = getVolumePrice(drawerProduct.price, vol);
                const el = document.getElementById('drawer-price');
                if (el) el.textContent = price + ' MAD';
            }
        }
        function addToCartFromDrawer() {
            if (!drawerProduct) return;
            const price = getVolumePrice(drawerProduct.price, selectedVolume);
            const itemId = (drawerProduct.id || drawerProduct.reference) + '_' + selectedVolume;
            const ex = cart.find(x => x.id === itemId);
            if (ex) ex.quantity++;
            else cart.push({...drawerProduct, id: itemId, price, volume: selectedVolume, quantity: 1});
            updateBadge();
            showToast(drawerProduct.name + ' (' + selectedVolume + ') ajouté !');
            closeProduct();
        }

        // ── Facture PDF (jsPDF) ────────────────────────────────────────
        function generateInvoicePDF() {
            if (!window.jspdf) { showToast('PDF non disponible (bibliothèque non chargée)'); return; }
            const { jsPDF } = window.jspdf;
            const legal = JSON.parse(localStorage.getItem('jp_legal') || '{}');
            const ref = checkoutData.orderRef || ('FAC-' + new Date().toISOString().slice(0,10).replace(/-/g,'') + '-' + Math.floor(Math.random()*9000+1000));
            const subtotal = cart.reduce((s,i) => s + (i.price * i.quantity), 0);
            const deliveryFee = checkoutData.delivery?.price || 0;
            const total = subtotal + deliveryFee;
            const doc = new jsPDF();
            const purple = [147, 51, 234], gold = [245, 158, 11], dark = [20, 20, 40];
            // Header
            doc.setFillColor(...purple);
            doc.rect(0, 0, 210, 42, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(30); doc.setFont('helvetica', 'bold');
            doc.text('JAMALI', 18, 22);
            doc.setFontSize(10); doc.setFont('helvetica', 'normal');
            doc.text('عطور | Parfums d\'exception — Maroc', 18, 32);
            doc.setFontSize(20); doc.setFont('helvetica', 'bold');
            doc.text('FACTURE', 192, 18, { align: 'right' });
            doc.setFontSize(9); doc.setFont('helvetica', 'normal');
            doc.text(ref, 192, 27, { align: 'right' });
            doc.text('Date : ' + new Date().toLocaleDateString('fr-FR'), 192, 34, { align: 'right' });
            // Client box
            doc.setTextColor(...dark);
            doc.setFillColor(245, 245, 255);
            doc.roundedRect(14, 50, 86, 42, 3, 3, 'F');
            doc.setFont('helvetica', 'bold'); doc.setFontSize(9);
            doc.text('FACTURER À :', 19, 58);
            doc.setFont('helvetica', 'normal');
            const c = checkoutData.client || {};
            doc.text((c.firstName||'') + ' ' + (c.lastName||''), 19, 64);
            doc.text('Tél : ' + (c.phone||''), 19, 70);
            doc.text(c.address||'', 19, 76);
            doc.text(c.city||'Maroc', 19, 82);
            // Company box
            doc.setFillColor(245, 245, 255);
            doc.roundedRect(110, 50, 86, 42, 3, 3, 'F');
            doc.setFont('helvetica', 'bold');
            doc.text(legal.name || 'JAMALI PARFUM', 115, 58);
            doc.setFont('helvetica', 'normal');
            doc.text(legal.address || 'Ain Chock, Casablanca', 115, 64);
            doc.text('Tél : ' + (legal.phone || '+212 700 76 28 49'), 115, 70);
            if (legal.ice) doc.text('ICE : ' + legal.ice, 115, 76);
            if (legal.rc)  doc.text('RC : '  + legal.rc,  115, 82);
            // Table header
            const ty = 102;
            doc.setFillColor(...purple);
            doc.rect(14, ty, 182, 8, 'F');
            doc.setTextColor(255, 255, 255); doc.setFont('helvetica', 'bold'); doc.setFontSize(9);
            doc.text('Réf.',     18,  ty+5.5);
            doc.text('Désignation', 38, ty+5.5);
            doc.text('Vol.',    118, ty+5.5);
            doc.text('Qté',    138, ty+5.5);
            doc.text('P.U.',   153, ty+5.5);
            doc.text('Total',  175, ty+5.5);
            doc.setTextColor(...dark); doc.setFont('helvetica', 'normal');
            let y = ty + 12;
            cart.forEach((item, idx) => {
                if (idx % 2 === 0) { doc.setFillColor(248,248,255); doc.rect(14, y-5, 182, 8, 'F'); }
                doc.text((item.reference||item.id||'').substring(0,8), 18, y);
                doc.text(item.name.substring(0,33), 38, y);
                doc.text(item.volume||'30ml', 118, y);
                doc.text(String(item.quantity), 140, y);
                doc.text(item.price+' MAD', 150, y);
                doc.text((item.price*item.quantity)+' MAD', 170, y);
                y += 9;
            });
            // Totals
            y += 8;
            doc.setFillColor(245,245,255);
            doc.roundedRect(120, y, 76, 34, 3, 3, 'F');
            doc.setFontSize(10); doc.setFont('helvetica', 'normal');
            doc.text('Sous-total :', 125, y+9);
            doc.text(subtotal+' MAD', 192, y+9, {align:'right'});
            doc.text('Livraison (' + (checkoutData.delivery?.label||'') + ') :', 125, y+18);
            doc.text(deliveryFee===0?'Gratuit':deliveryFee+' MAD', 192, y+18, {align:'right'});
            doc.setLineWidth(0.5); doc.setDrawColor(...purple);
            doc.line(122, y+21, 194, y+21);
            doc.setFont('helvetica','bold'); doc.setFontSize(13); doc.setTextColor(...purple);
            doc.text('TOTAL TTC :', 125, y+30);
            doc.text(total+' MAD', 192, y+30, {align:'right'});
            // Payment
            y += 44;
            doc.setFont('helvetica','normal'); doc.setFontSize(9); doc.setTextColor(...dark);
            const payLabel = checkoutData.payment==='stripe' ? 'Paiement en ligne (Stripe)' : 'Paiement à la livraison (COD)';
            doc.text('Mode de paiement : ' + payLabel, 14, y);
            if (checkoutData.paymentIntent) doc.text('Réf. Stripe : ' + checkoutData.paymentIntent.id, 14, y+7);
            // Footer
            doc.setFillColor(237, 233, 254);
            doc.rect(0, 275, 210, 22, 'F');
            doc.setFontSize(8); doc.setTextColor(100, 80, 140);
            doc.text('Jamali Parfum · Ain Chock, Casablanca, Maroc · +212 700 76 28 49 · عطور جمالي', 105, 282, {align:'center'});
            if (legal.ice) doc.text('ICE: '+legal.ice+(legal.if?' | IF: '+legal.if:'')+(legal.rc?' | RC: '+legal.rc:''), 105, 289, {align:'center'});
            doc.text('Merci pour votre confiance ! — شكراً لثقتكم بنا', 105, 295, {align:'center'});
            doc.save('Facture-' + ref + '.pdf');
        }

        window.onload = init;
'''

patch('JS_checkout_replace',
    '''        async function checkoutWhatsApp() {
            if(!cart.length) return;
            const total = cart.reduce((s,i)=>s+(i.price*i.quantity),0);
            try { await fetch('/api/order', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({cart, total}) }); } catch(e){}
            let msg = `Nouvelle commande :\\n\\n` + cart.map(i => `- ${i.quantity}x ${i.name} (${i.reference})`).join('\\n') + `\\n\\nTotal: ${total} MAD`;
            window.open(`https://wa.me/${adminPhone}?text=${encodeURIComponent(msg)}`, '_blank');
        }

        window.onload = init;''',
    NEW_JS)

# ─────────────────────────────────────────────────
# P13: Update init() to load legal settings + initStripe
# ─────────────────────────────────────────────────
patch('JS_init_legal',
    '''        function init() {
            initTheme();
            // Try to load products from API, fallback to static
            loadProductsFromAPI();
            document.getElementById('admin-phone') && (document.getElementById('admin-phone').value = adminPhone);
            const fp = document.getElementById('footer-phone');
            if (fp) fp.innerText = '+212 700 76 28 49';
        }''',
    '''        function init() {
            initTheme();
            loadProductsFromAPI();
            document.getElementById('admin-phone') && (document.getElementById('admin-phone').value = adminPhone);
            const fp = document.getElementById('footer-phone');
            if (fp) fp.innerText = '+212 700 76 28 49';
            // Load legal settings for PDF
            try { window._legalSettings = JSON.parse(localStorage.getItem('jp_legal') || '{}'); } catch(e) {}
            // Pre-init Stripe in background
            setTimeout(initStripe, 2000);
        }''')

# ─────────────────────────────────────────────────
# Write result
# ─────────────────────────────────────────────────
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nPatches OK  ({len(patches_ok)}/{len(patches_ok)+len(patches_fail)}) :")
for p in patches_ok:   print(f"  ✓ {p}")
if patches_fail:
    print(f"\nPatches FAIL ({len(patches_fail)}) :")
    for p in patches_fail: print(f"  ✗ {p}")

# Verify JS balance
import re as _re
scripts = _re.findall(r'<script>(.*?)</script>', html, _re.DOTALL)
print(f"\nScript blocks: {len(scripts)}")
for i, s in enumerate(scripts):
    o, c = s.count('{'), s.count('}')
    print(f"  Block {i+1}: {{ {o}  }} {c}  →  {'OK' if o==c else 'DÉSIQUILIBRE'}")

print(f"\nFile size: {len(html)} chars")
sys.exit(1 if patches_fail else 0)
