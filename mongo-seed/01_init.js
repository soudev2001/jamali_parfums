// mongo-seed/01_init.js
// Initialisation de la base de données jamali_db avec les données de départ
// Ce script est exécuté automatiquement au premier démarrage du conteneur MongoDB

db = db.getSiblingDB('jamali_db');

// ─── Création des index ───────────────────────────────────────────────────────
db.products.createIndex({ reference: 1 }, { unique: true });
db.products.createIndex({ category: 1 });
db.orders.createIndex({ date: -1 });

// ─── Nettoyage (idempotent) ───────────────────────────────────────────────────
db.products.deleteMany({});
db.categories.deleteMany({});

// ─── Catégories ──────────────────────────────────────────────────────────────
db.categories.insertMany([
  { slug: "homme",  label: "Pour Homme",  icon: "ph-gender-male"    },
  { slug: "femme",  label: "Pour Femme",  icon: "ph-gender-female"  },
  { slug: "mixte",  label: "Mixte",       icon: "ph-intersex"       },
  { slug: "oud",    label: "Collection Oud", icon: "ph-flower-lotus" },
  { slug: "promo",  label: "Promotions",  icon: "ph-tag"            }
]);

// ─── Produits ─────────────────────────────────────────────────────────────────
db.products.insertMany([

  // ── Collection Homme ──────────────────────────────────────────────────────
  {
    reference:   "JH-001",
    name:        "Bois Précieux",
    nameAr:      "الخشب النفيس",
    category:    "homme",
    price:       150,
    stock:       50,
    description: "Un accord boisé profond, notes de cèdre, vétiver et cuir fumé. Tenue >12h.",
    notes:       { top: ["bergamote", "cardamome"], heart: ["cèdre", "cuir"], base: ["vétiver", "musc"] },
    available:   true,
    createdAt:   new Date()
  },
  {
    reference:   "JH-002",
    name:        "Sultan Noir",
    nameAr:      "السلطان الأسود",
    category:    "homme",
    price:       150,
    stock:       35,
    description: "Frais et oriental, fusion d'agrumes siciliens et de bois exotiques. Idéal bureau.",
    notes:       { top: ["citron", "pamplemousse"], heart: ["poivre noir", "géranium"], base: ["santal", "ambre"] },
    available:   true,
    createdAt:   new Date()
  },
  {
    reference:   "JH-003",
    name:        "Azur Casablanca",
    nameAr:      "أزور الدار البيضاء",
    category:    "homme",
    price:       150,
    stock:       40,
    description: "Aquatique et moderne. Note de sel marin, menthe fraîche et cèdre blanc.",
    notes:       { top: ["menthe", "sel marin"], heart: ["lavande", "romarin"], base: ["cèdre blanc", "mousse"] },
    available:   true,
    createdAt:   new Date()
  },

  // ── Collection Femme ──────────────────────────────────────────────────────
  {
    reference:   "JF-001",
    name:        "Rose de Marrakech",
    nameAr:      "وردة مراكش",
    category:    "femme",
    price:       150,
    stock:       60,
    description: "Floral luxueux, rose centifolia de Kélaa M'Gouna, jasmin et oud rose.",
    notes:       { top: ["bergamote", "fraise"], heart: ["rose", "jasmin"], base: ["oud rose", "musc blanc"] },
    available:   true,
    createdAt:   new Date()
  },
  {
    reference:   "JF-002",
    name:        "Nuit Dorée",
    nameAr:      "الليلة الذهبية",
    category:    "femme",
    price:       150,
    stock:       45,
    description: "Oriental envoûtant. Vanille crémeuse, fleur d'oranger et patchouli doux.",
    notes:       { top: ["mandarine", "fleur d'oranger"], heart: ["ylang-ylang", "néroli"], base: ["vanille", "patchouli"] },
    available:   true,
    createdAt:   new Date()
  },
  {
    reference:   "JF-003",
    name:        "Lune de Jasmin",
    nameAr:      "قمر الياسمين",
    category:    "femme",
    price:       150,
    stock:       55,
    description: "Frais floral, jasmin sambac absolu, muguet et fond musqué très propre.",
    notes:       { top: ["poire", "pêche"], heart: ["jasmin", "muguet"], base: ["musc propre", "bois de cachemire"] },
    available:   true,
    createdAt:   new Date()
  },

  // ── Collection Mixte ──────────────────────────────────────────────────────
  {
    reference:   "JM-001",
    name:        "Atlas Spirit",
    nameAr:      "روح الأطلس",
    category:    "mixte",
    price:       150,
    stock:       70,
    description: "Inspiré des montagnes de l'Atlas. Cèdre marocain, labdanum et ambre chaud.",
    notes:       { top: ["eucalyptus", "pin"], heart: ["cèdre marocain", "iris"], base: ["labdanum", "ambre"] },
    available:   true,
    createdAt:   new Date()
  },
  {
    reference:   "JM-002",
    name:        "Musc Satin",
    nameAr:      "مسك الساتان",
    category:    "mixte",
    price:       150,
    stock:       80,
    description: "Musc doux et soyeux, signature quotidienne idéale. Longue durée.",
    notes:       { top: ["bergamote", "mandarine"], heart: ["musc blanc", "pivoine"], base: ["santal", "cèdre"] },
    available:   true,
    createdAt:   new Date()
  },

  // ── Collection Oud ────────────────────────────────────────────────────────
  {
    reference:   "JO-001",
    name:        "Al Oud Royale",
    nameAr:      "العود الملكي",
    category:    "oud",
    price:       150,
    stock:       25,
    description: "Oud sombre et résineux, encens sacré, rose rouge, ambregris. Longévité >24h.",
    notes:       { top: ["safran", "épices"], heart: ["oud", "rose rouge"], base: ["encens", "ambregris"] },
    available:   true,
    createdAt:   new Date()
  },
  {
    reference:   "JO-002",
    name:        "Oud Blanc Céleste",
    nameAr:      "العود الأبيض السماوي",
    category:    "oud",
    price:       150,
    stock:       30,
    description: "Version légère et aérienne de l'oud. Oud blanc, bois de lait et musc soyeux.",
    notes:       { top: ["citron yuzu", "gingembre"], heart: ["oud blanc", "fleur de tiaré"], base: ["bois de lait", "musc"] },
    available:   true,
    createdAt:   new Date()
  }
]);

print('Jamali DB initialisee : ' + db.products.countDocuments() + ' parfums inseres.');

// ─── Utilisateur applicatif (readWrite sur jamali_db) ────────────────────────
// Ce user est celui référencé dans MONGO_URI
db.createUser({
  user: "jamali_admin",
  pwd:  "JamaliApp2026",
  roles: [{ role: "readWrite", db: "jamali_db" }]
});

print('User jamali_admin cree avec acces readWrite sur jamali_db.');
