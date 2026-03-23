"""
Patch admin.html — CMS upgrade:
  - Fix loadProducts (data.products → data.items)
  - CSS: drag-drop, activity, faq, stock-pulse
  - Sidebar: 3 nouveaux onglets (Clients, Activité, FAQ)
  - Mobile nav: tous les onglets
  - Dashboard: carte alertes stock
  - Settings: infos légales + export CSV + statut Stripe
  - 3 nouveaux onglets HTML (Clients, Activité, FAQ)
  - Product modal: drag & drop image + champ description
  - JS: toutes les nouvelles fonctions
"""
import shutil, sys

shutil.copy('admin.html', 'admin.html.bak')

with open('admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

ok, fail = [], []

def patch(name, old, new):
    global html
    if old in html:
        html = html.replace(old, new, 1)
        ok.append(name)
    else:
        fail.append(name)

# ─────────────────────────────────────────────────
# P1 – CSS additions
# ─────────────────────────────────────────────────
patch('CSS_additions',
    '  select.form-input option{background:#1a1a1a}\n</style>',
    '''  select.form-input option{background:#1a1a1a}
  /* ── Image drag & drop ── */
  .img-drop-zone{border:2px dashed #374151;border-radius:16px;padding:20px;text-align:center;cursor:pointer;transition:all .25s;position:relative;min-height:100px}
  .img-drop-zone.dragging{border-color:#9333ea;background:rgba(147,51,234,.07)}
  .img-drop-zone:hover{border-color:#6b7280}
  /* ── Activity timeline ── */
  .activity-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:5px}
  /* ── FAQ items ── */
  .faq-item{border:1px solid #262626;border-radius:16px;padding:16px;background:#111;transition:border-color .2s}
  .faq-item:hover{border-color:#3b0764}
  /* ── Stock pulse ── */
  @keyframes pulse-red{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.4)}50%{box-shadow:0 0 0 6px rgba(239,68,68,0)}}
  .badge-pulse{animation:pulse-red 2s infinite}
  /* ── img tab buttons ── */
  .img-tab-btn{flex:1;padding:6px;font-size:12px;font-weight:700;border-radius:8px;transition:all .2s;background:transparent;color:#6b7280;cursor:pointer}
  .img-tab-btn.active{background:#374151;color:#fff}
</style>''')

# ─────────────────────────────────────────────────
# P2 – Sidebar: add 3 new nav buttons
# ─────────────────────────────────────────────────
patch('Sidebar_new_tabs',
    '''      <button onclick="switchTab('settings')" data-tab="settings" class="nav-btn w-full flex items-center px-3 py-2.5 rounded-xl text-sm font-bold transition text-neutral-400 hover:bg-neutral-800 hover:text-white">
        <i class="ph-fill ph-gear-six text-lg mr-3"></i> Paramètres
      </button>''',
    '''      <button onclick="switchTab('clients')" data-tab="clients" class="nav-btn w-full flex items-center px-3 py-2.5 rounded-xl text-sm font-bold transition text-neutral-400 hover:bg-neutral-800 hover:text-white">
        <i class="ph-fill ph-users text-lg mr-3"></i> Clients
      </button>
      <button onclick="switchTab('activity')" data-tab="activity" class="nav-btn w-full flex items-center px-3 py-2.5 rounded-xl text-sm font-bold transition text-neutral-400 hover:bg-neutral-800 hover:text-white">
        <i class="ph-fill ph-activity text-lg mr-3"></i> Activité
      </button>
      <button onclick="switchTab('faq')" data-tab="faq" class="nav-btn w-full flex items-center px-3 py-2.5 rounded-xl text-sm font-bold transition text-neutral-400 hover:bg-neutral-800 hover:text-white">
        <i class="ph-fill ph-question text-lg mr-3"></i> FAQ
      </button>
      <button onclick="switchTab('settings')" data-tab="settings" class="nav-btn w-full flex items-center px-3 py-2.5 rounded-xl text-sm font-bold transition text-neutral-400 hover:bg-neutral-800 hover:text-white">
        <i class="ph-fill ph-gear-six text-lg mr-3"></i> Paramètres
      </button>''')

# ─────────────────────────────────────────────────
# P3 – Mobile nav: add new tabs, make scrollable
# ─────────────────────────────────────────────────
patch('Mobile_nav',
    '''    <div class="flex space-x-0.5">
      <button onclick="switchTab('dashboard')" data-tab="dashboard" class="mob-tab p-2 text-primary-400"><i class="ph-fill ph-squares-four text-lg"></i></button>
      <button onclick="switchTab('products')"  data-tab="products"  class="mob-tab p-2 text-neutral-400"><i class="ph-fill ph-package text-lg"></i></button>
      <button onclick="switchTab('orders')"    data-tab="orders"    class="mob-tab p-2 text-neutral-400"><i class="ph-fill ph-receipt text-lg"></i></button>
      <button onclick="switchTab('settings')"  data-tab="settings"  class="mob-tab p-2 text-neutral-400"><i class="ph-fill ph-gear-six text-lg"></i></button>
      <button onclick="doLogout()"             class="p-2 text-red-400"><i class="ph ph-sign-out text-lg"></i></button>
    </div>''',
    '''    <div class="flex overflow-x-auto no-scrollbar">
      <button onclick="switchTab('dashboard')" data-tab="dashboard" class="mob-tab flex-shrink-0 p-2 text-primary-400" aria-label="Dashboard"><i class="ph-fill ph-squares-four text-lg"></i></button>
      <button onclick="switchTab('products')"  data-tab="products"  class="mob-tab flex-shrink-0 p-2 text-neutral-400" aria-label="Produits"><i class="ph-fill ph-package text-lg"></i></button>
      <button onclick="switchTab('orders')"    data-tab="orders"    class="mob-tab flex-shrink-0 p-2 text-neutral-400" aria-label="Commandes"><i class="ph-fill ph-receipt text-lg"></i></button>
      <button onclick="switchTab('clients')"   data-tab="clients"   class="mob-tab flex-shrink-0 p-2 text-neutral-400" aria-label="Clients"><i class="ph-fill ph-users text-lg"></i></button>
      <button onclick="switchTab('activity')"  data-tab="activity"  class="mob-tab flex-shrink-0 p-2 text-neutral-400" aria-label="Activité"><i class="ph-fill ph-activity text-lg"></i></button>
      <button onclick="switchTab('faq')"       data-tab="faq"       class="mob-tab flex-shrink-0 p-2 text-neutral-400" aria-label="FAQ"><i class="ph-fill ph-question text-lg"></i></button>
      <button onclick="switchTab('settings')"  data-tab="settings"  class="mob-tab flex-shrink-0 p-2 text-neutral-400" aria-label="Paramètres"><i class="ph-fill ph-gear-six text-lg"></i></button>
      <button onclick="doLogout()"             class="flex-shrink-0 p-2 text-red-400" aria-label="Déconnexion"><i class="ph ph-sign-out text-lg"></i></button>
    </div>''')

# ─────────────────────────────────────────────────
# P4 – Dashboard: stock alerts + auto-refresh stats
# ─────────────────────────────────────────────────
patch('Dashboard_stock_badge',
    '<i class="ph-fill ph-package text-lg mr-3"></i> Produits\n      </button>',
    '<i class="ph-fill ph-package text-lg mr-3"></i> Produits\n        <span id="badge-low-stock" class="ml-auto bg-red-600 text-white text-[10px] px-1.5 py-0.5 rounded-full hidden badge-pulse">!</span>\n      </button>')

patch('Dashboard_stock_section',
    '''      <h3 class="text-lg font-bold text-neutral-300 mb-4 flex items-center gap-2"><i class="ph-fill ph-clock-clockwise text-primary-500"></i> Dernières commandes</h3>
      <div id="dash-orders" class="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
        <div class="p-8 text-center text-neutral-500">Chargement...</div>
      </div>
    </div>''',
    '''      <!-- Stock Alerts -->
      <div class="mb-8 bg-red-500/5 border border-red-500/20 rounded-2xl p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-red-400 flex items-center gap-2">
            <i class="ph-fill ph-warning text-base"></i> Alertes Stock (stock ≤ 3)
          </h3>
          <button onclick="switchTab('products')" class="text-xs text-neutral-500 hover:text-red-400 transition">Voir produits →</button>
        </div>
        <div id="dash-stock-alerts" class="space-y-1 text-sm text-neutral-400">Chargement...</div>
      </div>

      <h3 class="text-lg font-bold text-neutral-300 mb-4 flex items-center gap-2"><i class="ph-fill ph-clock-clockwise text-primary-500"></i> Dernières commandes</h3>
      <div id="dash-orders" class="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
        <div class="p-8 text-center text-neutral-500">Chargement...</div>
      </div>
    </div>''')

# ─────────────────────────────────────────────────
# P5 – Settings tab: add legal info + export + Stripe
# ─────────────────────────────────────────────────
patch('Settings_new_cards',
    '''        <!-- Demo mode -->
        <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
          <h3 class="font-bold text-white mb-2 flex items-center"><i class="ph-fill ph-eye text-amber-500 mr-2"></i> Mode Démo</h3>
          <p class="text-sm text-neutral-400 mb-4">En mode démo, toutes les actions d'écriture sont bloquées. Idéal pour une présentation.</p>
          <button onclick="toggleDemo()" id="demo-btn"
            class="w-full py-2.5 rounded-xl font-bold transition bg-amber-600/20 text-amber-400 border border-amber-600/30 hover:bg-amber-600/30">
            Désactiver le mode démo
          </button>
        </div>

      </div>
    </div>''',
    '''        <!-- Demo mode -->
        <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
          <h3 class="font-bold text-white mb-2 flex items-center"><i class="ph-fill ph-eye text-amber-500 mr-2"></i> Mode Démo</h3>
          <p class="text-sm text-neutral-400 mb-4">En mode démo, toutes les actions d'écriture sont bloquées. Idéal pour une présentation.</p>
          <button onclick="toggleDemo()" id="demo-btn"
            class="w-full py-2.5 rounded-xl font-bold transition bg-amber-600/20 text-amber-400 border border-amber-600/30 hover:bg-amber-600/30">
            Désactiver le mode démo
          </button>
        </div>

        <!-- Legal info -->
        <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 md:col-span-2">
          <h3 class="font-bold text-white mb-4 flex items-center"><i class="ph-fill ph-buildings text-primary-400 mr-2"></i> Informations légales (utilisées dans les factures PDF)</h3>
          <form onsubmit="saveLegalSettings(event)" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div><label class="form-label">Nom de l'entreprise</label>
              <input id="legal-name" type="text" class="form-input" placeholder="Jamali Parfum"></div>
            <div><label class="form-label">Adresse</label>
              <input id="legal-address" type="text" class="form-input" placeholder="Ain Chock, Casablanca"></div>
            <div><label class="form-label">Téléphone</label>
              <input id="legal-phone" type="text" class="form-input" placeholder="+212 700 76 28 49"></div>
            <div><label class="form-label">ICE</label>
              <input id="legal-ice" type="text" class="form-input font-mono" placeholder="000000000000000"></div>
            <div><label class="form-label">RC</label>
              <input id="legal-rc" type="text" class="form-input font-mono" placeholder="12345"></div>
            <div><label class="form-label">IF (Identifiant Fiscal)</label>
              <input id="legal-if" type="text" class="form-input font-mono" placeholder="12345678"></div>
            <div class="sm:col-span-2 lg:col-span-3">
              <button type="submit" class="px-6 py-2.5 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-xl transition">
                <i class="ph ph-floppy-disk mr-1"></i>Enregistrer les informations légales
              </button>
            </div>
          </form>
        </div>

        <!-- Export + Stripe status -->
        <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
          <h3 class="font-bold text-white mb-4 flex items-center"><i class="ph-fill ph-download-simple text-emerald-400 mr-2"></i> Export des données</h3>
          <button onclick="exportOrdersCsv()" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition flex items-center justify-center gap-2">
            <i class="ph ph-file-csv text-lg"></i> Exporter les commandes (CSV)
          </button>
          <p class="text-xs text-neutral-500 mt-2">Télécharge toutes les commandes en CSV compatible Excel.</p>
        </div>

        <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
          <h3 class="font-bold text-white mb-4 flex items-center"><i class="ph-fill ph-credit-card text-blue-400 mr-2"></i> Stripe</h3>
          <div id="stripe-status-display" class="text-sm space-y-2 text-neutral-400">Vérification...</div>
        </div>

      </div>
    </div>''')

# ─────────────────────────────────────────────────
# P6 – Add 3 new tab panes before </main>
# ─────────────────────────────────────────────────
patch('New_tab_panes',
    '  </main>\n</div>\n\n<!-- ═══════════════════════════════════════════════════════\n     PRODUCT MODAL',
    '''  <!-- ───────────── CLIENTS ───────────── -->
  <div id="tab-clients" class="tab-pane fadein">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <h2 class="text-2xl font-bold text-white flex items-center gap-2">
        <i class="ph-fill ph-users text-primary-500"></i> Clients
        <span id="clients-count" class="text-base text-neutral-500 font-normal ml-1"></span>
      </h2>
      <div class="relative">
        <i class="ph ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500"></i>
        <input id="client-search" type="text" oninput="filterClients()" placeholder="Nom, téléphone, ville..."
          class="bg-neutral-900 border border-neutral-800 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white focus:border-primary-500 transition w-full sm:w-64">
      </div>
    </div>
    <div id="clients-list">
      <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Chargement...</div>
    </div>
  </div>

  <!-- ───────────── ACTIVITÉ ───────────── -->
  <div id="tab-activity" class="tab-pane fadein">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <h2 class="text-2xl font-bold text-white flex items-center gap-2">
        <i class="ph-fill ph-activity text-primary-500"></i> Journal d'activité
      </h2>
      <div class="flex gap-2 flex-wrap">
        <button onclick="filterActivity(event,'')" class="act-filter-btn active text-xs px-3 py-1.5 rounded-lg bg-primary-600 text-white font-bold">Tout</button>
        <button onclick="filterActivity(event,'auth')" class="act-filter-btn text-xs px-3 py-1.5 rounded-lg bg-neutral-800 text-neutral-400 font-bold hover:text-white">Auth</button>
        <button onclick="filterActivity(event,'product')" class="act-filter-btn text-xs px-3 py-1.5 rounded-lg bg-neutral-800 text-neutral-400 font-bold hover:text-white">Produits</button>
        <button onclick="filterActivity(event,'order')" class="act-filter-btn text-xs px-3 py-1.5 rounded-lg bg-neutral-800 text-neutral-400 font-bold hover:text-white">Cmdes</button>
        <button onclick="filterActivity(event,'faq')" class="act-filter-btn text-xs px-3 py-1.5 rounded-lg bg-neutral-800 text-neutral-400 font-bold hover:text-white">FAQ</button>
      </div>
    </div>
    <div id="activity-list">
      <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Aucune activité enregistrée (vide au démarrage du serveur).</div>
    </div>
  </div>

  <!-- ───────────── FAQ ───────────── -->
  <div id="tab-faq" class="tab-pane fadein">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-white flex items-center gap-2">
        <i class="ph-fill ph-question text-primary-500"></i> FAQ
        <span class="text-xs text-neutral-500 font-normal">Visible sur la boutique</span>
      </h2>
      <button onclick="openFaqForm(null)" class="flex items-center bg-primary-600 hover:bg-primary-500 text-white font-bold px-4 py-2.5 rounded-xl transition shadow shadow-primary-600/30">
        <i class="ph ph-plus text-lg mr-1.5"></i> Ajouter
      </button>
    </div>
    <!-- Form -->
    <div id="faq-form-box" class="hidden bg-neutral-900 border border-primary-600/30 rounded-2xl p-5 mb-6">
      <h3 id="faq-form-title" class="font-bold text-white mb-4">Nouvelle entrée FAQ</h3>
      <form onsubmit="saveFaq(event)" class="space-y-3">
        <input type="hidden" id="faq-edit-id">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="form-label">Question (FR) *</label>
            <input id="faq-q-fr" required type="text" class="form-input" placeholder="Livrez-vous partout au Maroc ?">
          </div>
          <div>
            <label class="form-label">Question (AR) <span class="font-normal normal-case text-neutral-600">optionnel</span></label>
            <input id="faq-q-ar" type="text" class="form-input text-right" dir="rtl" placeholder="هل توصلون في كل أنحاء المغرب؟">
          </div>
          <div class="sm:col-span-2">
            <label class="form-label">Réponse (FR) *</label>
            <textarea id="faq-a-fr" required rows="2" class="form-input resize-none" placeholder="Oui, nous livrons partout au Maroc sous 2-3 jours..."></textarea>
          </div>
          <div class="sm:col-span-2">
            <label class="form-label">Réponse (AR) <span class="font-normal normal-case text-neutral-600">optionnel</span></label>
            <textarea id="faq-a-ar" rows="2" class="form-input resize-none text-right" dir="rtl" placeholder="نعم، نوصل في كل أنحاء المغرب..."></textarea>
          </div>
        </div>
        <div class="flex gap-3 justify-end">
          <button type="button" onclick="closeFaqForm()" class="px-5 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-bold text-sm transition">Annuler</button>
          <button type="submit" class="px-5 py-2 bg-primary-600 hover:bg-primary-500 text-white font-bold rounded-xl text-sm transition">Enregistrer</button>
        </div>
      </form>
    </div>
    <!-- List -->
    <div id="faq-list" class="space-y-3">
      <div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Chargement...</div>
    </div>
  </div>

  </main>
</div>

<!-- ═══════════════════════════════════════════════════════
     PRODUCT MODAL''')

# ─────────────────────────────────────────────────
# P7 – Product modal: drag & drop image + description
# ─────────────────────────────────────────────────
patch('Modal_image_dragdrop',
    '''      <!-- Image URL -->
      <div>
        <label class="form-label">URL Image</label>
        <div class="flex gap-2">
          <input id="f-image" type="url" class="form-input flex-1" placeholder="https://..." oninput="previewImage()">
          <img id="img-preview" src="" alt="" class="w-12 h-12 rounded-lg object-cover border border-neutral-700 hidden">
        </div>
      </div>

      <!-- Tags -->''',
    '''      <!-- Image upload: drag & drop ou URL -->
      <div>
        <label class="form-label">Image du produit</label>
        <!-- Tabs -->
        <div class="flex bg-neutral-800 rounded-xl p-1 mb-3 gap-1">
          <button type="button" id="img-tab-file" onclick="switchImgTab('file')" class="img-tab-btn active">
            <i class="ph ph-image-square mr-1"></i>Glisser / Fichier
          </button>
          <button type="button" id="img-tab-url" onclick="switchImgTab('url')" class="img-tab-btn">
            <i class="ph ph-link mr-1"></i>URL externe
          </button>
        </div>
        <!-- File panel -->
        <div id="img-panel-file">
          <div id="img-drop-zone" class="img-drop-zone" onclick="triggerFileInput()">
            <img id="img-upload-preview" src="" alt="" class="hidden w-24 h-24 object-cover rounded-xl mx-auto mb-2 border border-neutral-700">
            <div class="img-placeholder">
              <i class="ph ph-upload-simple text-3xl text-neutral-500 mb-2"></i>
              <p class="text-neutral-400 text-sm font-bold">Glissez une image ici ou cliquez</p>
              <p class="text-neutral-600 text-xs mt-1">JPG, PNG, WEBP — 2 Mo max</p>
            </div>
          </div>
          <div class="flex items-center justify-between mt-2">
            <span id="img-size-info" class="text-xs text-neutral-500"></span>
            <button type="button" id="img-remove-btn" onclick="clearImageUpload()" class="hidden text-xs text-red-400 hover:text-red-300 transition">
              <i class="ph ph-x-circle mr-1"></i>Supprimer
            </button>
          </div>
          <input type="hidden" id="f-image">
        </div>
        <!-- URL panel -->
        <div id="img-panel-url" class="hidden">
          <div class="flex gap-2">
            <input id="f-image-url" type="url" class="form-input flex-1" placeholder="https://images.unsplash.com/..." oninput="previewImageUrl()">
            <img id="img-preview" src="" alt="" class="w-12 h-12 rounded-lg object-cover border border-neutral-700 hidden flex-shrink-0">
          </div>
        </div>
        <input type="file" id="f-image-file" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
      </div>

      <!-- Description -->
      <div>
        <label class="form-label">Description <span class="font-normal normal-case text-neutral-600">optionnel</span></label>
        <textarea id="f-description" rows="2" class="form-input resize-none" placeholder="Notes ou description courte du parfum..."></textarea>
      </div>

      <!-- Tags -->''')

# ─────────────────────────────────────────────────
# P8 – Fix loadProducts: data.products → data.items
# ─────────────────────────────────────────────────
patch('loadProducts_items_fix',
    '  productCache = data.products || [];\n  prodTotal    = data.total || 0;',
    '  productCache = data.items || [];\n  prodTotal    = data.total || 0;')

# ─────────────────────────────────────────────────
# P9 – Fix openProductModal to reset image + add description
# ─────────────────────────────────────────────────
patch('openProductModal_reset',
    '''  document.getElementById('edit-id').value       = '';
  document.getElementById('img-preview').classList.add('hidden');
  document.getElementById('form-error').classList.add('hidden');
  document.getElementById('f-available').checked = true;
  document.getElementById('f-bestseller').checked = false;''',
    '''  document.getElementById('edit-id').value       = '';
  if (document.getElementById('img-preview')) document.getElementById('img-preview').classList.add('hidden');
  document.getElementById('form-error').classList.add('hidden');
  document.getElementById('f-available').checked = true;
  document.getElementById('f-bestseller').checked = false;
  clearImageUpload();
  if (document.getElementById('f-image-url')) document.getElementById('f-image-url').value = '';
  if (document.getElementById('f-description')) document.getElementById('f-description').value = '';
  switchImgTab('file');
  setTimeout(initImgDrop, 50);''')

patch('openProductModal_edit_image',
    '''    document.getElementById('f-tags').value        = (p.tags||[]).join(', ');
    document.getElementById('f-available').checked  = p.available !== false;
    document.getElementById('f-bestseller').checked = !!p.isBestseller;
    previewImage();''',
    '''    document.getElementById('f-tags').value        = (p.tags||[]).join(', ');
    document.getElementById('f-available').checked  = p.available !== false;
    document.getElementById('f-bestseller').checked = !!p.isBestseller;
    if (document.getElementById('f-description')) document.getElementById('f-description').value = p.description || '';
    // Load existing image into drop zone
    const existingImg = p.image_b64 || p.image || '';
    if (existingImg) {
      if (existingImg.startsWith('data:')) {
        const prev = document.getElementById('img-upload-preview');
        if (prev) { prev.src = existingImg; prev.classList.remove('hidden'); }
        if (document.getElementById('img-drop-zone')) {
          document.getElementById('img-drop-zone').querySelector('.img-placeholder')?.classList.add('hidden');
        }
        if (document.getElementById('img-remove-btn')) document.getElementById('img-remove-btn').classList.remove('hidden');
        imageB64 = existingImg;
        imgFromDrop = true;
      } else {
        switchImgTab('url');
        if (document.getElementById('f-image-url')) {
          document.getElementById('f-image-url').value = existingImg;
          previewImageUrl();
        }
      }
    }''')

# ─────────────────────────────────────────────────
# P10 – Fix saveProduct to use imageB64 or URL
# ─────────────────────────────────────────────────
patch('saveProduct_image_b64',
    '''  const payload = {
    reference:    document.getElementById('f-reference').value.trim(),
    name:         document.getElementById('f-name').value.trim(),
    brand:        document.getElementById('f-brand').value.trim(),
    category:     document.getElementById('f-category').value,
    price:        parseFloat(document.getElementById('f-price').value) || 150,
    stock:        parseInt(document.getElementById('f-stock').value)   || 0,
    image:        document.getElementById('f-image').value.trim(),
    type:         document.getElementById('f-type').value,
    volume:       document.getElementById('f-volume').value,
    tags:         document.getElementById('f-tags').value.split(',').map(t=>t.trim()).filter(Boolean),
    available:    document.getElementById('f-available').checked,
    isBestseller: document.getElementById('f-bestseller').checked,
  };''',
    '''  const urlImageVal = (document.getElementById('f-image-url')?.value || '').trim();
  const payload = {
    reference:    document.getElementById('f-reference').value.trim(),
    name:         document.getElementById('f-name').value.trim(),
    brand:        document.getElementById('f-brand').value.trim(),
    category:     document.getElementById('f-category').value,
    price:        parseFloat(document.getElementById('f-price').value) || 150,
    stock:        parseInt(document.getElementById('f-stock').value)   || 0,
    image:        imgFromDrop ? '' : urlImageVal,
    image_b64:    imgFromDrop ? imageB64 : '',
    description:  (document.getElementById('f-description')?.value || '').trim(),
    type:         document.getElementById('f-type').value,
    volume:       document.getElementById('f-volume').value,
    tags:         document.getElementById('f-tags').value.split(',').map(t=>t.trim()).filter(Boolean),
    available:    document.getElementById('f-available').checked,
    isBestseller: document.getElementById('f-bestseller').checked,
  };''')

# ─────────────────────────────────────────────────
# P11 – Update loadProducts image rendering (use image_b64 || image)
# ─────────────────────────────────────────────────
patch('loadProducts_img_b64',
    '''        ${p.image
          ? `<img src="${p.image}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" class="w-12 h-12 object-cover rounded-xl border border-neutral-700 shadow">
             <div style="display:none" class="w-12 h-12 rounded-xl border border-neutral-700 bg-gradient-to-br from-primary-900 to-primary-800 flex items-center justify-center text-primary-400 text-xl">🧴</div>`
          : `<div class="w-12 h-12 rounded-xl border border-neutral-700 bg-gradient-to-br from-primary-900 to-primary-800 flex items-center justify-center text-primary-400 text-xl">🧴</div>`}''',
    '''        ${(p.image_b64 || p.image)
          ? `<img src="${p.image_b64 || p.image}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" class="w-12 h-12 object-cover rounded-xl border border-neutral-700 shadow">
             <div style="display:none" class="w-12 h-12 rounded-xl border border-neutral-700 bg-gradient-to-br from-primary-900 to-primary-800 flex items-center justify-center text-primary-400 text-xl">🧴</div>`
          : `<div class="w-12 h-12 rounded-xl border border-neutral-700 bg-gradient-to-br from-primary-900 to-primary-800 flex items-center justify-center text-primary-400 text-xl">🧴</div>`}''')

# ─────────────────────────────────────────────────
# P12 – Update switchTab for new tabs + load legal settings on settings
# ─────────────────────────────────────────────────
patch('switchTab_new_tabs',
    '''  if (name === 'products') loadProducts();
  if (name === 'orders')   loadOrders();
  if (name === 'settings') loadSystemStatus();''',
    '''  if (name === 'products') loadProducts();
  if (name === 'orders')   loadOrders();
  if (name === 'clients')  loadClients();
  if (name === 'activity') loadActivity();
  if (name === 'faq')      loadFaq();
  if (name === 'settings') { loadSystemStatus(); loadLegalSettings(); loadStripeStatus(); }''')

# ─────────────────────────────────────────────────
# P13 – Update showApp to start auto-refresh
# ─────────────────────────────────────────────────
patch('showApp_autorefresh',
    '''function showApp() {
  document.getElementById('login-overlay').classList.add('hidden');
  document.getElementById('admin-app').classList.remove('hidden');
  document.getElementById('admin-app').classList.add('flex');
  loadDashboard();
}''',
    '''function showApp() {
  document.getElementById('login-overlay').classList.add('hidden');
  document.getElementById('admin-app').classList.remove('hidden');
  document.getElementById('admin-app').classList.add('flex');
  loadDashboard();
  // Auto-refresh stats every 60s
  setInterval(() => {
    const activePanes = document.querySelectorAll('.tab-pane.active');
    activePanes.forEach(p => {
      if (p.id === 'tab-dashboard') loadDashboard();
    });
  }, 60000);
}''')

# ─────────────────────────────────────────────────
# P14 – Update loadDashboard to include stock alerts
# ─────────────────────────────────────────────────
patch('loadDashboard_stock',
    '''  const badge = document.getElementById('badge-new-orders');
  if (d.new_orders > 0) { badge.textContent = d.new_orders; badge.classList.remove('hidden'); }
  loadDashOrders();''',
    '''  const badge = document.getElementById('badge-new-orders');
  if (d.new_orders > 0) { badge.textContent = d.new_orders; badge.classList.remove('hidden'); }
  if (d.low_stock > 0) {
    const lb = document.getElementById('badge-low-stock');
    if (lb) { lb.textContent = d.low_stock; lb.classList.remove('hidden'); }
  }
  loadDashOrders();
  loadStockAlerts();''')

# ─────────────────────────────────────────────────
# P15 – Fix previewImage → update for URL tab, add all new JS
# ─────────────────────────────────────────────────
patch('All_new_JS',
    '''function previewImage() {
  const url = document.getElementById('f-image').value;
  const img = document.getElementById('img-preview');
  if (url && url.startsWith('http')) {
    img.src = url; img.classList.remove('hidden');
  } else {
    img.classList.add('hidden');
  }
}''',
    r'''function previewImageUrl() {
  const url = (document.getElementById('f-image-url')?.value || '').trim();
  const img = document.getElementById('img-preview');
  if (!img) return;
  if (url && (url.startsWith('http') || url.startsWith('data:'))) {
    img.src = url; img.classList.remove('hidden');
  } else {
    img.classList.add('hidden');
  }
}
// Legacy alias
function previewImage() { previewImageUrl(); }

/* ═══════════════ IMAGE DRAG & DROP ════════════════════════════════ */
let imageB64   = '';
let imgFromDrop = false;

function initImgDrop() {
  const zone = document.getElementById('img-drop-zone');
  if (!zone || zone._ddInit) return;
  zone._ddInit = true;
  zone.addEventListener('dragover',  e => { e.preventDefault(); zone.classList.add('dragging'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragging'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('dragging');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) processImageFile(file);
  });
}
function triggerFileInput() { document.getElementById('f-image-file')?.click(); }
function handleFileSelect(e) { const f = e.target.files[0]; if (f) processImageFile(f); }
function processImageFile(file) {
  if (file.size > 2.5 * 1024 * 1024) { toast('Image trop grande (2.5 Mo max)', 'error'); return; }
  const reader = new FileReader();
  reader.onload = ev => {
    imageB64    = ev.target.result;
    imgFromDrop = true;
    const prev  = document.getElementById('img-upload-preview');
    if (prev)  { prev.src = imageB64; prev.classList.remove('hidden'); }
    document.getElementById('img-drop-zone')?.querySelector('.img-placeholder')?.classList.add('hidden');
    const rm = document.getElementById('img-remove-btn');
    if (rm) rm.classList.remove('hidden');
    const si = document.getElementById('img-size-info');
    if (si) si.textContent = (file.size / 1024).toFixed(0) + ' Ko · ' + file.type.split('/')[1].toUpperCase();
  };
  reader.readAsDataURL(file);
}
function clearImageUpload() {
  imageB64 = ''; imgFromDrop = false;
  const prev = document.getElementById('img-upload-preview');
  if (prev) { prev.src = ''; prev.classList.add('hidden'); }
  document.getElementById('img-drop-zone')?.querySelector('.img-placeholder')?.classList.remove('hidden');
  const rm = document.getElementById('img-remove-btn');
  if (rm) rm.classList.add('hidden');
  const si = document.getElementById('img-size-info');
  if (si) si.textContent = '';
  const fi = document.getElementById('f-image-file');
  if (fi) fi.value = '';
}
function switchImgTab(tab) {
  const tabFile = document.getElementById('img-tab-file');
  const tabUrl  = document.getElementById('img-tab-url');
  const panFile = document.getElementById('img-panel-file');
  const panUrl  = document.getElementById('img-panel-url');
  if (!tabFile) return;
  tabFile.classList.toggle('active', tab === 'file');
  tabUrl.classList.toggle('active',  tab === 'url');
  panFile.classList.toggle('hidden', tab !== 'file');
  panUrl.classList.toggle('hidden',  tab !== 'url');
  if (tab === 'file') setTimeout(initImgDrop, 30);
}

/* ═══════════════ CLIENTS ══════════════════════════════════════════ */
let clientsData = [];
async function loadClients() {
  const el = document.getElementById('clients-list');
  el.innerHTML = '<div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Chargement...</div>';
  const r = await api('GET', '/api/admin/clients');
  if (!r.ok) { el.innerHTML = '<p class="text-red-400 text-center py-8">Erreur de chargement</p>'; return; }
  clientsData = await r.json();
  const cnt = document.getElementById('clients-count');
  if (cnt) cnt.textContent = `(${clientsData.length} clients)`;
  renderClients(clientsData);
}
function filterClients() {
  const q = (document.getElementById('client-search')?.value || '').toLowerCase();
  renderClients(clientsData.filter(c =>
    c.name.toLowerCase().includes(q) || c.phone.includes(q) || (c.city||'').toLowerCase().includes(q)
  ));
}
function renderClients(data) {
  const el = document.getElementById('clients-list');
  if (!data.length) {
    el.innerHTML = '<div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Aucun client trouvé — les clients sont créés à partir des commandes.</div>';
    return;
  }
  el.innerHTML = `<div class="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
    <div class="overflow-x-auto"><table class="w-full text-sm">
      <thead class="bg-neutral-800 text-neutral-400 text-xs uppercase tracking-wider">
        <tr>
          <th class="px-4 py-3 text-left">Client</th>
          <th class="px-4 py-3 text-left hidden md:table-cell">Ville</th>
          <th class="px-4 py-3 text-center hidden sm:table-cell">Cmdes</th>
          <th class="px-4 py-3 text-right">Total dépensé</th>
          <th class="px-4 py-3 text-right hidden lg:table-cell">Dernière cmd</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-neutral-800">
        ${data.map((c, idx) => `
          <tr class="hover:bg-primary-600/5 transition cursor-pointer" onclick="toggleClientOrders(${idx})">
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                  ${(c.name||'?')[0].toUpperCase()}
                </div>
                <div>
                  <div class="font-bold text-white text-sm">${escHtml(c.name)}</div>
                  <div class="text-xs text-neutral-500 font-mono">${escHtml(c.phone)}</div>
                </div>
              </div>
            </td>
            <td class="px-4 py-3 hidden md:table-cell text-neutral-400 text-sm">${escHtml(c.city||'—')}</td>
            <td class="px-4 py-3 hidden sm:table-cell text-center">
              <span class="text-xs bg-primary-600/20 text-primary-300 px-2 py-0.5 rounded-full font-bold">${c.orders_count}</span>
            </td>
            <td class="px-4 py-3 text-right font-bold text-gold-400">${(c.total_spent||0).toLocaleString()} MAD</td>
            <td class="px-4 py-3 text-right hidden lg:table-cell text-xs text-neutral-500">
              ${c.last_order ? new Date(c.last_order).toLocaleDateString('fr-FR') : '—'}
            </td>
          </tr>
          <tr id="client-orders-${idx}" class="hidden bg-neutral-800/30">
            <td colspan="5" class="px-4 py-3">
              <div class="text-xs text-neutral-400 mb-2 font-bold uppercase tracking-wider">Historique :</div>
              <div class="space-y-1">
                ${(c.orders||[]).length ? (c.orders||[]).map(o => `
                  <div class="flex flex-wrap items-center gap-3 text-xs py-1 border-b border-neutral-800/50 last:border-0">
                    <span class="font-mono text-neutral-500">#${String(o._id).slice(-6).toUpperCase()}</span>
                    <span class="text-neutral-400">${o.items} article${o.items>1?'s':''}</span>
                    <span class="font-bold text-white">${o.total} MAD</span>
                    <span class="${STATUS_BADGE[o.status]||'badge-done'} text-white text-[10px] px-2 py-0.5 rounded-full">${o.status||'?'}</span>
                    <span class="text-neutral-600">${o.date ? new Date(o.date).toLocaleDateString('fr-FR') : '—'}</span>
                  </div>`).join('') : '<p class="text-neutral-600 italic text-xs">Aucune commande</p>'}
              </div>
            </td>
          </tr>`).join('')}
      </tbody>
    </table></div>
  </div>`;
}
function toggleClientOrders(idx) {
  document.getElementById('client-orders-' + idx)?.classList.toggle('hidden');
}

/* ═══════════════ ACTIVITY ══════════════════════════════════════════ */
let activityData   = [];
let activityFilter = '';
async function loadActivity() {
  const el = document.getElementById('activity-list');
  const r = await api('GET', '/api/admin/activity?limit=150');
  if (!r.ok) { el.innerHTML = '<p class="text-red-400 text-center py-6">Erreur</p>'; return; }
  activityData = await r.json();
  renderActivity(activityFilter ? activityData.filter(a => a.type === activityFilter) : activityData);
}
function filterActivity(event, type) {
  activityFilter = type;
  document.querySelectorAll('.act-filter-btn').forEach(b => {
    b.classList.remove('bg-primary-600', 'text-white');
    b.classList.add('bg-neutral-800', 'text-neutral-400');
  });
  if (event?.target) {
    event.target.classList.add('bg-primary-600', 'text-white');
    event.target.classList.remove('bg-neutral-800', 'text-neutral-400');
  }
  renderActivity(type ? activityData.filter(a => a.type === type) : activityData);
}
function renderActivity(data) {
  const el = document.getElementById('activity-list');
  if (!data.length) {
    el.innerHTML = '<div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Aucune activité enregistrée. Les actions apparaîtront ici après connexion.</div>';
    return;
  }
  const colors = { auth:'bg-blue-500', product:'bg-primary-500', order:'bg-emerald-500', faq:'bg-gold-500', upload:'bg-orange-500' };
  el.innerHTML = `<div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-4 space-y-0.5">
    ${data.map(a => `
      <div class="flex items-start gap-3 py-2.5 border-b border-neutral-800/40 last:border-0">
        <div class="activity-dot ${colors[a.type]||'bg-neutral-600'} mt-1.5 flex-shrink-0"></div>
        <div class="flex-1 min-w-0">
          <p class="text-sm text-white leading-snug">${escHtml(a.desc)}</p>
          <p class="text-xs text-neutral-500 mt-0.5">${relativeTime(a.timestamp)} · <span class="text-neutral-600">${escHtml(a.user||'admin')}</span></p>
        </div>
        <span class="text-[10px] px-2 py-0.5 rounded-full font-bold flex-shrink-0 bg-neutral-800 text-neutral-400">${escHtml(a.type||'?')}</span>
      </div>`).join('')}
  </div>`;
}
function relativeTime(iso) {
  if (!iso) return '—';
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60)    return `il y a ${diff}s`;
  if (diff < 3600)  return `il y a ${Math.floor(diff/60)}min`;
  if (diff < 86400) return `il y a ${Math.floor(diff/3600)}h`;
  return new Date(iso).toLocaleDateString('fr-FR');
}

/* ═══════════════ FAQ ════════════════════════════════════════════════ */
let faqData   = [];
let faqEditId = null;
async function loadFaq() {
  const el = document.getElementById('faq-list');
  const r = await api('GET', '/api/admin/faq');
  if (!r.ok) { el.innerHTML = '<p class="text-red-400 text-center py-6">Erreur</p>'; return; }
  faqData = await r.json();
  renderFaq();
}
function renderFaq() {
  const el = document.getElementById('faq-list');
  if (!faqData.length) {
    el.innerHTML = '<div class="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 text-center text-neutral-500">Aucune FAQ — cliquez &quot;Ajouter&quot; pour créer la première entrée.</div>';
    return;
  }
  el.innerHTML = faqData.map(f => `
    <div class="faq-item">
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1 min-w-0">
          <p class="font-bold text-white text-sm">${escHtml(f.question_fr||'')}</p>
          ${f.question_ar ? `<p class="text-xs text-neutral-500 text-right mt-0.5" dir="rtl">${escHtml(f.question_ar)}</p>` : ''}
          <p class="text-sm text-neutral-400 mt-2 leading-relaxed">${escHtml(f.answer_fr||'')}</p>
          ${f.answer_ar ? `<p class="text-xs text-neutral-600 text-right mt-1" dir="rtl">${escHtml(f.answer_ar)}</p>` : ''}
        </div>
        <div class="flex gap-1 flex-shrink-0 mt-0.5">
          <button onclick="editFaq('${f._id}')" class="p-2 text-neutral-400 hover:text-primary-400 hover:bg-primary-500/10 rounded-lg transition" aria-label="Modifier"><i class="ph ph-pencil text-sm"></i></button>
          <button onclick="deleteFaq('${f._id}')" class="p-2 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition" aria-label="Supprimer"><i class="ph ph-trash text-sm"></i></button>
        </div>
      </div>
    </div>`).join('');
}
function openFaqForm(id) {
  if (DEMO_MODE) { toast('Mode Démo : modification désactivée', 'warning'); return; }
  faqEditId = id;
  document.getElementById('faq-form-title').textContent = id ? 'Modifier la FAQ' : 'Nouvelle entrée FAQ';
  document.getElementById('faq-edit-id').value = id || '';
  const f = id ? faqData.find(x => x._id === id) : null;
  ['q-fr','q-ar','a-fr','a-ar'].forEach(k => {
    const map = {'q-fr':'question_fr','q-ar':'question_ar','a-fr':'answer_fr','a-ar':'answer_ar'};
    const el = document.getElementById('faq-' + k);
    if (el) el.value = f ? (f[map[k]]||'') : '';
  });
  const box = document.getElementById('faq-form-box');
  box.classList.remove('hidden');
  box.scrollIntoView({behavior: 'smooth', block: 'nearest'});
}
function closeFaqForm() {
  document.getElementById('faq-form-box').classList.add('hidden');
  faqEditId = null;
}
async function saveFaq(e) {
  e.preventDefault();
  if (DEMO_MODE) { toast('Mode Démo', 'warning'); return; }
  const id  = document.getElementById('faq-edit-id').value;
  const payload = {
    question_fr: document.getElementById('faq-q-fr').value.trim(),
    answer_fr:   document.getElementById('faq-a-fr').value.trim(),
    question_ar: document.getElementById('faq-q-ar').value.trim(),
    answer_ar:   document.getElementById('faq-a-ar').value.trim(),
    order: faqData.length
  };
  const r = await api(id ? 'PUT' : 'POST', id ? `/api/admin/faq/${id}` : '/api/admin/faq', payload);
  if (r.ok) { toast(id ? 'FAQ mise à jour ✓' : 'FAQ ajoutée ✓'); closeFaqForm(); loadFaq(); }
  else       { toast('Erreur sauvegarde', 'error'); }
}
function editFaq(id)   { openFaqForm(id); }
async function deleteFaq(id) {
  if (DEMO_MODE) { toast('Mode Démo', 'warning'); return; }
  if (!confirm('Supprimer cette entrée FAQ ?')) return;
  const r = await api('DELETE', `/api/admin/faq/${id}`);
  if (r.ok) { toast('FAQ supprimée'); loadFaq(); } else toast('Erreur suppression', 'error');
}

/* ═══════════════ STOCK ALERTS ══════════════════════════════════════ */
async function loadStockAlerts() {
  const el = document.getElementById('dash-stock-alerts');
  if (!el) return;
  const r = await api('GET', '/api/admin/stock-alerts');
  if (!r.ok) { el.innerHTML = '<p class="text-neutral-500 text-sm">Impossible de charger les alertes</p>'; return; }
  const items = await r.json();
  const badge = document.getElementById('badge-low-stock');
  if (items.length > 0 && badge) { badge.textContent = items.length; badge.classList.remove('hidden'); }
  else if (badge)               badge.classList.add('hidden');
  if (!items.length) {
    el.innerHTML = '<p class="text-emerald-400 text-sm flex items-center gap-1.5"><i class="ph-fill ph-check-circle"></i> Tous les stocks sont corrects ✓</p>';
    return;
  }
  el.innerHTML = items.slice(0, 8).map(p => `
    <div class="flex items-center justify-between text-sm py-1">
      <span class="text-neutral-300 truncate max-w-[62%]">${escHtml(p.name||p.reference||'?')}</span>
      <span class="font-bold text-[11px] px-2 py-0.5 rounded-lg ${p.stock<=0?'bg-red-500/15 text-red-400':p.stock<=2?'bg-orange-500/15 text-orange-400':'bg-yellow-500/15 text-yellow-400'}">
        ${p.stock<=0?'Rupture':p.stock+' restant'+(p.stock>1?'s':'')}
      </span>
    </div>`).join('');
}

/* ═══════════════ LEGAL SETTINGS ════════════════════════════════════ */
function loadLegalSettings() {
  const s = JSON.parse(localStorage.getItem('jp_legal') || '{}');
  ['name','address','phone','ice','rc','if'].forEach(k => {
    const el = document.getElementById('legal-' + k);
    if (el) el.value = s[k] || '';
  });
}
async function saveLegalSettings(e) {
  e.preventDefault();
  if (DEMO_MODE) { toast('Mode Démo', 'warning'); return; }
  const s = {};
  ['name','address','phone','ice','rc','if'].forEach(k => {
    const el = document.getElementById('legal-' + k);
    if (el) s[k] = el.value.trim();
  });
  localStorage.setItem('jp_legal', JSON.stringify(s));
  try { await api('POST', '/api/admin/settings', s); } catch {}
  toast('Informations légales enregistrées ✓');
}

/* ═══════════════ EXPORT ════════════════════════════════════════════ */
async function exportOrdersCsv() {
  const r = await api('GET', '/api/admin/export/orders');
  if (!r.ok) { toast('Erreur export', 'error'); return; }
  const blob = await r.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'commandes-jamali.csv'; a.click();
  URL.revokeObjectURL(url);
  toast('Export téléchargé ✓');
}

/* ═══════════════ STRIPE STATUS ═════════════════════════════════════ */
async function loadStripeStatus() {
  const el = document.getElementById('stripe-status-display');
  if (!el) return;
  try {
    const r = await fetch('/api/stripe-key');
    const d = await r.json();
    const pk = d.publishable_key || '';
    if (pk && !pk.includes('replace')) {
      el.innerHTML = `<div class="flex items-center gap-2 text-emerald-400 font-bold"><i class="ph-fill ph-check-circle text-lg"></i> Stripe configuré (test mode)</div>
        <p class="text-xs text-neutral-500 mt-1 font-mono">${pk.slice(0,20)}...</p>`;
    } else {
      el.innerHTML = `<div class="flex items-center gap-2 text-amber-400"><i class="ph-fill ph-warning text-lg"></i> Clés Stripe non configurées</div>
        <p class="text-xs text-neutral-500 mt-1">Ajoutez <code class="font-mono bg-neutral-800 px-1 rounded">STRIPE_PUBLISHABLE_KEY</code> dans .env</p>`;
    }
  } catch { el.innerHTML = '<span class="text-neutral-500">Non disponible</span>'; }
}''')

# ─────────────────────────────────────────────────
# Write result
# ─────────────────────────────────────────────────
with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nPatches OK  ({len(ok)}/{len(ok)+len(fail)}) :")
for p in ok:   print(f"  ✓ {p}")
if fail:
    print(f"\nPatches FAIL ({len(fail)}) :")
    for p in fail: print(f"  ✗ {p}")

print(f"\nFile size: {len(html)} chars (~{len(html.splitlines())} lines)")
sys.exit(1 if fail else 0)
