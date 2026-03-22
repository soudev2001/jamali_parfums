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
  { slug: "Homme",   label: "Pour Homme",     icon: "ph-gender-male"    },
  { slug: "Femme",   label: "Pour Femme",     icon: "ph-gender-female"  },
  { slug: "Mixte",   label: "Mixte",          icon: "ph-intersex"       },
  { slug: "Oriental",label: "Oriental / Oud", icon: "ph-flower-lotus"   }
]);

// ─── Produits ─────────────────────────────────────────────────────────────────
// Champs compatibles avec admin.html : reference, name, brand, category
// (Homme|Femme|Oriental|Mixte), type (EDP|EDT|Cologne|Oud|Musc|Extrait),
// volume (ex: "100ml"), price, stock, image, tags[], isBestseller, available
db.products.insertMany([

  // ══════════════════════════════════════════════════════════════════════════
  //  COLLECTION HOMME
  // ══════════════════════════════════════════════════════════════════════════

  // ── Dolce & Gabbana ───────────────────────────────────────────────────────
  {
    reference: "JH-001", name: "Style DG Homme", brand: "Dolce & Gabbana",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","élégant","cuir"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-002", name: "Style The One", brand: "Dolce & Gabbana",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","épicé","tabac"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-003", name: "Style The One Sport", brand: "Dolce & Gabbana",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","sportif","aquatique"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-004", name: "Style K", brand: "Dolce & Gabbana",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","agrumes","aromatique"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-005", name: "Style Light Blue Homme", brand: "Dolce & Gabbana",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","aquatique","agrumes"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Dunhill ───────────────────────────────────────────────────────────────
  {
    reference: "JH-006", name: "Style Désire", brand: "Dunhill",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-007", name: "Style Désire Blue", brand: "Dunhill",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","aquatique","aromatique"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Giorgio Armani ────────────────────────────────────────────────────────
  {
    reference: "JH-008", name: "Style Acqua Di Gio", brand: "Giorgio Armani",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["aquatique","frais","marin"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-009", name: "Style Armani Code Profumo", brand: "Giorgio Armani",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","ambre","cuir"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-010", name: "Style Stronger with You", brand: "Giorgio Armani",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","cannelle"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-011", name: "Style Stronger Absolutely", brand: "Giorgio Armani",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","épicé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-012", name: "Style Stronger with You Intensely", brand: "Giorgio Armani",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","intense"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Givenchy ──────────────────────────────────────────────────────────────
  {
    reference: "JH-013", name: "Style Gentleman 2017", brand: "Givenchy",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","floral","élégant"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-014", name: "Style Gentleman EDP Réserve Privée", brand: "Givenchy",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","iris","whisky"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-015", name: "Style Boisée Givenchy", brand: "Givenchy",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","cèdre","vétiver"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-016", name: "Style Only Gentleman", brand: "Givenchy",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","cuir","épicé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-017", name: "Style Pi", brand: "Givenchy",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["vanille","amande","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Hermès ────────────────────────────────────────────────────────────────
  {
    reference: "JH-018", name: "Style Terre d'Hermès", brand: "Hermès",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","agrumes","vétiver"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Hugo Boss ─────────────────────────────────────────────────────────────
  {
    reference: "JH-019", name: "Style Boss Bottled", brand: "Hugo Boss",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","pomme","vanille"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-020", name: "Style Boss Bottled Tonic", brand: "Hugo Boss",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","agrumes","gingembre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-021", name: "Style Boss The Scent", brand: "Hugo Boss",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","cuir","gingembre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-022", name: "Style Hugo", brand: "Hugo Boss",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","aromatique","vert"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Jean Paul Gaultier ────────────────────────────────────────────────────
  {
    reference: "JH-023", name: "Style Le Male", brand: "Jean Paul Gaultier",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","menthe"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-024", name: "Style Le Male Elixir", brand: "Jean Paul Gaultier",
    category: "Homme", type: "Extrait", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","lavande"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-025", name: "Style Scandal Homme", brand: "Jean Paul Gaultier",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","caramel","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-026", name: "Style Ultra Male", brand: "Jean Paul Gaultier",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","poire"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Azzaro ────────────────────────────────────────────────────────────────
  {
    reference: "JH-027", name: "Style Chrome", brand: "Azzaro",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","agrumes","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-028", name: "Style The Most Wanted", brand: "Azzaro",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","épicé","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-029", name: "Style Wanted", brand: "Azzaro",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","gingembre","agrumes"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Acqua Di Parma ────────────────────────────────────────────────────────
  {
    reference: "JH-030", name: "Style Acqua Di Parma Oud et Spice", brand: "Acqua Di Parma",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","épicé","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Antonio Banderas ──────────────────────────────────────────────────────
  {
    reference: "JH-031", name: "Style Blue Seduction Homme", brand: "Antonio Banderas",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","aquatique","agrumes"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Bvlgari ───────────────────────────────────────────────────────────────
  {
    reference: "JH-032", name: "Style Man In Black", brand: "Bvlgari",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","cuir","épicé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Lacoste ───────────────────────────────────────────────────────────────
  {
    reference: "JH-033", name: "Style Lacoste Noir", brand: "Lacoste",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","sombre","élégant"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-034", name: "Style Lacoste Blanc", brand: "Lacoste",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","pamplemousse","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-035", name: "Style Lacoste Rouge", brand: "Lacoste",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","épicé","stimulant"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-036", name: "Style Lacoste Essential", brand: "Lacoste",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","vert","tomate"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Carolina Herrera ──────────────────────────────────────────────────────
  {
    reference: "JH-037", name: "Style 212 Men", brand: "Carolina Herrera",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","épicé","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-038", name: "Style 212 Vip Homme", brand: "Carolina Herrera",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","gin","épicé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-039", name: "Style Bad Boy", brand: "Carolina Herrera",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","cacao","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Chanel ────────────────────────────────────────────────────────────────
  {
    reference: "JH-040", name: "Style Allure Homme Sport", brand: "Chanel",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","sportif","agrumes"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-041", name: "Style Bleu de Chanel", brand: "Chanel",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","agrumes","encens"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Christian Dior ────────────────────────────────────────────────────────
  {
    reference: "JH-042", name: "Style Dior Homme Intense", brand: "Christian Dior",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["iris","ambre","élégant"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-043", name: "Style Fahrenheit", brand: "Christian Dior",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","cuir","essence"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-044", name: "Style Sauvage", brand: "Christian Dior",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","poivre","ambroxan"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-045", name: "Style Sauvage Elixir", brand: "Christian Dior",
    category: "Homme", type: "Extrait", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["épicé","boisé","réglisse"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Creed ─────────────────────────────────────────────────────────────────
  {
    reference: "JH-046", name: "Style Aventus", brand: "Creed",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","boisé","ananas"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-047", name: "Style Silver Mountain Water", brand: "Creed",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","thé vert","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Davidoff ──────────────────────────────────────────────────────────────
  {
    reference: "JH-048", name: "Style Cool Water", brand: "Davidoff",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["aquatique","frais","marin"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Diesel ────────────────────────────────────────────────────────────────
  {
    reference: "JH-049", name: "Style Fuel for Life", brand: "Diesel",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","framboise","anis"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-050", name: "Style Only the Brave", brand: "Diesel",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","cuir","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Paco Rabanne ──────────────────────────────────────────────────────────
  {
    reference: "JH-051", name: "Style Black XS L'Excès Homme", brand: "Paco Rabanne",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","épicé","cannelle"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-052", name: "Style Invictus", brand: "Paco Rabanne",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","aquatique","goyave"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-053", name: "Style One Million", brand: "Paco Rabanne",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","épicé","cuir"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-054", name: "Style One Million Intense", brand: "Paco Rabanne",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","épicé","or"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-055", name: "Style Phantom", brand: "Paco Rabanne",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","lavande","citron"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Parfums de Marly ──────────────────────────────────────────────────────
  {
    reference: "JH-056", name: "Style Pegasus", brand: "Parfums de Marly",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","amande"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Ralph Lauren ──────────────────────────────────────────────────────────
  {
    reference: "JH-057", name: "Style Polo Bleu Gold Blend", brand: "Ralph Lauren",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","sauge","vétiver"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Valentino ─────────────────────────────────────────────────────────────
  {
    reference: "JH-058", name: "Style Valentino Uomo", brand: "Valentino",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["cuir","café","iris"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-059", name: "Style Patchouli", brand: "Valentino",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["patchouli","boisé","terreux"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Versace ───────────────────────────────────────────────────────────────
  {
    reference: "JH-060", name: "Style Eros Homme", brand: "Versace",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","menthe","vanille"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Cartier ───────────────────────────────────────────────────────────────
  {
    reference: "JH-061", name: "Style Déclaration", brand: "Cartier",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","épicé","cuir"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Viktor & Rolf ─────────────────────────────────────────────────────────
  {
    reference: "JH-062", name: "Style Spicebomb", brand: "Viktor & Rolf",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["épicé","tabac","explosif"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Yves Saint Laurent ────────────────────────────────────────────────────
  {
    reference: "JH-063", name: "Style L'Homme", brand: "Yves Saint Laurent",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","gingembre","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-064", name: "Style La Nuit de l'Homme", brand: "Yves Saint Laurent",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","cardamome","cèdre"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-065", name: "Style Y", brand: "Yves Saint Laurent",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","pomme","gingembre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-066", name: "Style Y EDP", brand: "Yves Saint Laurent",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","sauge","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Zadig & Voltaire ──────────────────────────────────────────────────────
  {
    reference: "JH-067", name: "Style This Is Him", brand: "Zadig & Voltaire",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","boisé","fève tonka"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Maison Francis Kurkdjian ──────────────────────────────────────────────
  {
    reference: "JH-068", name: "Style Baccarat Rouge 540", brand: "Maison Francis Kurkdjian",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["ambre","safran","cèdre"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Gissah ────────────────────────────────────────────────────────────────
  {
    reference: "JH-069", name: "Style Hudson Valley", brand: "Gissah",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","frais","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-070", name: "Style Imperial Valley", brand: "Gissah",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","oud","épicé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Oud Arabian ───────────────────────────────────────────────────────────
  {
    reference: "JH-071", name: "Style Madawi Gold Edition", brand: "Oud Arabian",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","oud","or"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Calvin Klein ──────────────────────────────────────────────────────────
  {
    reference: "JH-072", name: "Style CK One", brand: "Calvin Klein",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","agrumes","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-073", name: "Style CK One Gold", brand: "Calvin Klein",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","figue","néroli"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Lancôme ───────────────────────────────────────────────────────────────
  {
    reference: "JH-074", name: "Style Oud Bouquet", brand: "Lancôme",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","rose","safran"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Lattafa Perfumes ──────────────────────────────────────────────────────
  {
    reference: "JH-075", name: "Style Ana Abiyedh", brand: "Lattafa Perfumes",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","oriental","doux"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Mancera ───────────────────────────────────────────────────────────────
  {
    reference: "JH-076", name: "Style Red Tobacco", brand: "Mancera",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["tabac","épicé","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Montale ───────────────────────────────────────────────────────────────
  {
    reference: "JH-077", name: "Style Arabians Tonka", brand: "Montale",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fève tonka","oriental","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Parfums de Marly ──────────────────────────────────────────────────────
  {
    reference: "JH-078", name: "Style Layton", brand: "Parfums de Marly",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","menthe"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Tom Ford ──────────────────────────────────────────────────────────────
  {
    reference: "JH-079", name: "Style Black Orchid", brand: "Tom Ford",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","truffe","orchidée"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Xerjoff ───────────────────────────────────────────────────────────────
  {
    reference: "JH-080", name: "Style Erba Pura", brand: "Xerjoff",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","musc","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-081", name: "Style Fleur d'Oranger / Zahr", brand: "Xerjoff",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","fleur d'oranger","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Oud et Musc ───────────────────────────────────────────────────────────
  {
    reference: "JH-082", name: "Style Poussière d'Or", brand: "Oud et Musc",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","or","oriental"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-083", name: "Style Raghba", brand: "Oud et Musc",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-084", name: "Style Oud El Shams", brand: "Oud et Musc",
    category: "Homme", type: "Oud", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","solaire","épicé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Louis Vuitton ─────────────────────────────────────────────────────────
  {
    reference: "JH-085", name: "Style Matière Noire", brand: "Louis Vuitton",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["boisé","oud","cuir"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-086", name: "Style Ombre Nomade", brand: "Louis Vuitton",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","rose","framboise"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-087", name: "Style Imagination", brand: "Louis Vuitton",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","agrumes","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-088", name: "Style Narciso Poudrée", brand: "Louis Vuitton",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["poudré","musc","floral"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Collection Orientale / Arabe ──────────────────────────────────────────
  {
    reference: "JH-089", name: "سحر الكلمات (Sihr Al Kalimat)", brand: "Jamali Oriental",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","mystique","encens"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-090", name: "عود شيخة (Oud Sheikha)", brand: "Jamali Oriental",
    category: "Homme", type: "Oud", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","royal","oriental"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-091", name: "مسك الأبيض (Musc Al Abyad)", brand: "Jamali Oriental",
    category: "Homme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","blanc","doux"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-092", name: "مسك الأسود (Musc Al Aswad)", brand: "Jamali Oriental",
    category: "Homme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","noir","intense"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-093", name: "عود أبيض (Oud Abyad)", brand: "Jamali Oriental",
    category: "Homme", type: "Oud", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","blanc","floral"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-094", name: "رغبة (Raghba)", brand: "Jamali Oriental",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","caramel"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-095", name: "مذهلة (Mudhhila)", brand: "Jamali Oriental",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","ambre","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-096", name: "العود (Al Oud)", brand: "Jamali Oriental",
    category: "Homme", type: "Oud", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","encens","safran"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-097", name: "عود خصوصي (Oud Khoussousi)", brand: "Jamali Oriental",
    category: "Homme", type: "Oud", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","privé","rare"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-098", name: "ورد اسطانبولي (Ward Istanbuli)", brand: "Jamali Oriental",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["rose","istanbul","oriental"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-099", name: "عطر الزهر (Attar Al Zahr)", brand: "Jamali Oriental",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","fleur d'oranger","jasmin"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ══════════════════════════════════════════════════════════════════════════
  //  COLLECTION FEMME
  // ══════════════════════════════════════════════════════════════════════════

  // ── Dolce & Gabbana ───────────────────────────────────────────────────────
  {
    reference: "JF-150", name: "Style L'Impératrice 3", brand: "Dolce & Gabbana",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","floral","pastèque"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-151", name: "Style Light Blue Femme", brand: "Dolce & Gabbana",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","agrumes","pomme"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-152", name: "Style The One Femme", brand: "Dolce & Gabbana",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","pêche"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-153", name: "Style Devotion", brand: "Dolce & Gabbana",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","citron","caramel"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Elie Saab ─────────────────────────────────────────────────────────────
  {
    reference: "JF-154", name: "Style Girl of Now", brand: "Elie Saab",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","amande","orange"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-155", name: "Style Le Parfum", brand: "Elie Saab",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","patchouli"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Escada ────────────────────────────────────────────────────────────────
  {
    reference: "JF-156", name: "Style Cherry In the Air", brand: "Escada",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","cerise","vanille"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-157", name: "Style Collection", brand: "Escada",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","floral","frais"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-158", name: "Style Taj Sunset", brand: "Escada",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","mangue","coco"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Giorgio Armani ────────────────────────────────────────────────────────
  {
    reference: "JF-159", name: "Style My Way", brand: "Giorgio Armani",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","tubéreuse","bergamote"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-160", name: "Style Si", brand: "Giorgio Armani",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","cassis","vanille"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-161", name: "Style Si Passion", brand: "Giorgio Armani",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","rose","vanille"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Gissah ────────────────────────────────────────────────────────────────
  {
    reference: "JF-162", name: "Style Ellora - Legend of the Sky 2", brand: "Gissah",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","musc","oriental"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-163", name: "Style Sora - Legend of the Sky 2", brand: "Gissah",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["frais","fruité","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Givenchy ──────────────────────────────────────────────────────────────
  {
    reference: "JF-164", name: "Style Irrésistible", brand: "Givenchy",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","musc"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-165", name: "Style L'Interdit 2018", brand: "Givenchy",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","tubéreuse","vétiver"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-166", name: "Style L'Interdit Rouge", brand: "Givenchy",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","ambre","sésame"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Gucci ─────────────────────────────────────────────────────────────────
  {
    reference: "JF-167", name: "Style Gucci Bloom", brand: "Gucci",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","tubéreuse","jasmin"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-168", name: "Style Gucci Flora", brand: "Gucci",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","pivoine","osmanthus"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-169", name: "Style Gucci Guilty for Women", brand: "Gucci",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","lilas","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Guerlain ──────────────────────────────────────────────────────────────
  {
    reference: "JF-170", name: "Style La Petite Robe Noire", brand: "Guerlain",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","cerise","amande"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-171", name: "Style Mon Guerlain", brand: "Guerlain",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","lavande"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Hermès ────────────────────────────────────────────────────────────────
  {
    reference: "JF-172", name: "Style Twilly", brand: "Hermès",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","gingembre","tubéreuse"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Jean Paul Gaultier ────────────────────────────────────────────────────
  {
    reference: "JF-173", name: "Style Scandal", brand: "Jean Paul Gaultier",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","miel","gardénia"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-174", name: "Style La Belle", brand: "Jean Paul Gaultier",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","poire"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Avon ──────────────────────────────────────────────────────────────────
  {
    reference: "JF-175", name: "Style Incandessence", brand: "Avon",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","frais","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-176", name: "Style Today", brand: "Avon",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","muguet","rose"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-177", name: "Style Tomorrow", brand: "Avon",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","frais","vert"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Britney Spears ────────────────────────────────────────────────────────
  {
    reference: "JF-178", name: "Style Fantasy", brand: "Britney Spears",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","litchi","chocolat"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-179", name: "Style Midnight Fantasy", brand: "Britney Spears",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","prune","orchidée"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Burberry ──────────────────────────────────────────────────────────────
  {
    reference: "JF-180", name: "Style Burberry Her", brand: "Burberry",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","fraise","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Ajmal ─────────────────────────────────────────────────────────────────
  {
    reference: "JF-181", name: "Style Wisal", brand: "Ajmal",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","rose","oud"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Calvin Klein ──────────────────────────────────────────────────────────
  {
    reference: "JF-182", name: "Style Euphoria", brand: "Calvin Klein",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","grenade","orchidée"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Carolina Herrera ──────────────────────────────────────────────────────
  {
    reference: "JF-183", name: "Style Good Girl", brand: "Carolina Herrera",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","tubéreuse","cacao"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Cartier ───────────────────────────────────────────────────────────────
  {
    reference: "JF-184", name: "Style La Panthère", brand: "Cartier",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","gardénia","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Chanel ────────────────────────────────────────────────────────────────
  {
    reference: "JF-185", name: "Style Chance", brand: "Chanel",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","iris","musc"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-186", name: "Style Coco Mademoiselle", brand: "Chanel",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","orange","patchouli"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Christian Dior ────────────────────────────────────────────────────────
  {
    reference: "JF-187", name: "Style Hypnotic Poison", brand: "Christian Dior",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","amande"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-188", name: "Style J'adore", brand: "Christian Dior",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","ylang-ylang","rose"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-189", name: "Style Miss Dior Chérie", brand: "Christian Dior",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Lancôme ───────────────────────────────────────────────────────────────
  {
    reference: "JF-190", name: "Style Idôle", brand: "Lancôme",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","jasmin"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-191", name: "Style Trésor Midnight Rose", brand: "Lancôme",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","framboise","rose"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-192", name: "Style La Nuit Trésor", brand: "Lancôme",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","orchidée"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-193", name: "Style La Vie Est Belle", brand: "Lancôme",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","iris","praline"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Lattafa ───────────────────────────────────────────────────────────────
  {
    reference: "JF-194", name: "Style Yara", brand: "Lattafa",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","vanille","fruits tropicaux"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-195", name: "Style Khamrah", brand: "Lattafa",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","cannelle","oud"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-196", name: "Style Ameerat Al Arab", brand: "Lattafa",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","ambre","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Marc Jacobs ───────────────────────────────────────────────────────────
  {
    reference: "JF-197", name: "Style Décadence", brand: "Marc Jacobs",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","prune","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Narciso Rodriguez ─────────────────────────────────────────────────────
  {
    reference: "JF-198", name: "Style Narciso Rodriguez For Her", brand: "Narciso Rodriguez",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","floral","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Nina Ricci ────────────────────────────────────────────────────────────
  {
    reference: "JF-199", name: "Style Nina", brand: "Nina Ricci",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","pomme","caramel"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-200", name: "Style L'Extase", brand: "Nina Ricci",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Oriflame ──────────────────────────────────────────────────────────────
  {
    reference: "JF-201", name: "Style Amber Elixir", brand: "Oriflame",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","ambre","vanille"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-202", name: "Style Enigma", brand: "Oriflame",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","épicé","santal"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-203", name: "Style Giordani Gold", brand: "Oriflame",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","néroli","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Paco Rabanne ──────────────────────────────────────────────────────────
  {
    reference: "JF-204", name: "Style Lady Million", brand: "Paco Rabanne",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","miel","ambre"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-205", name: "Style Olympéa", brand: "Paco Rabanne",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","sel"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Parfums de Marly ──────────────────────────────────────────────────────
  {
    reference: "JF-206", name: "Style Delina", brand: "Parfums de Marly",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","litchi"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Thierry Mugler ────────────────────────────────────────────────────────
  {
    reference: "JF-207", name: "Style Alien Femme", brand: "Thierry Mugler",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","jasmin","ambre"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ── Versace ───────────────────────────────────────────────────────────────
  {
    reference: "JF-208", name: "Style Crystal Noir", brand: "Versace",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","gardénia","ambre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-209", name: "Style Eros Femme", brand: "Versace",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","citronnelle","jasmin"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Victoria's Secret ─────────────────────────────────────────────────────
  {
    reference: "JF-210", name: "Style Coconut Passion", brand: "Victoria's Secret",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","coco","vanille"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-211", name: "Style Very Sexy Now 2017", brand: "Victoria's Secret",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","rose","musc"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Yves Rocher ───────────────────────────────────────────────────────────
  {
    reference: "JF-212", name: "Style Comme une Évidence", brand: "Yves Rocher",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","rose","cèdre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-213", name: "Style So Elixir", brand: "Yves Rocher",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","rose","vanille"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Yves Saint Laurent ────────────────────────────────────────────────────
  {
    reference: "JF-214", name: "Style Black Opium", brand: "Yves Saint Laurent",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","café","vanille"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-215", name: "Style Cinéma", brand: "Yves Saint Laurent",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","amande","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-216", name: "Style Libre", brand: "Yves Saint Laurent",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","lavande","vanille"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-217", name: "Style Manifesto", brand: "Yves Saint Laurent",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","cassis","jasmin"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-218", name: "Style Mon Paris", brand: "Yves Saint Laurent",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","fraise","pivoine"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Zadig & Voltaire ──────────────────────────────────────────────────────
  {
    reference: "JF-219", name: "Style This Is Her", brand: "Zadig & Voltaire",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","café","santal"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Maison Francis Kurkdjian ──────────────────────────────────────────────
  {
    reference: "JF-220", name: "Style Baccarat Rouge 540", brand: "Maison Francis Kurkdjian",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["ambre","safran","cèdre"], isBestseller: true, available: true, createdAt: new Date()
  },

  // ══════════════════════════════════════════════════════════════════════════
  //  COLLECTION JAMALI ORIENTAL FEMME
  // ══════════════════════════════════════════════════════════════════════════
  {
    reference: "JF-221", name: "وشوشة (Washwasha)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","musc","doux"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-224", name: "مسك الأبيض (Musc Al Abyad)", brand: "Jamali Parfum",
    category: "Femme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","blanc","doux"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-225", name: "مسك الأسود (Musc Al Aswad)", brand: "Jamali Parfum",
    category: "Femme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","noir","intense"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-226", name: "مسك الطهارة (Musc Tahara)", brand: "Jamali Parfum",
    category: "Femme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","tahara","propre"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-227", name: "مسك الفانيلا (Musc Vanille)", brand: "Jamali Parfum",
    category: "Femme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","vanille","gourmand"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-229", name: "رقبة (Raqaba)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","vanille","caramel"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-230", name: "مذهلة (Mudhhila)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oriental","ambre","boisé"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-231", name: "العود (Al Oud)", brand: "Jamali Parfum",
    category: "Femme", type: "Oud", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["oud","encens","safran"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-233", name: "ورد اسطانبولي (Ward Istanbuli)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["rose","istanbul","oriental"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-234", name: "عطر الزهر (Attar Al Zahr)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","fleur d'oranger","jasmin"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-235", name: "عطر الخوخ (Attar Al Khokh)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","pêche","doux"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-236", name: "عطر المانجا (Attar Al Manga)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","mangue","tropical"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-237", name: "عطر الشوكولا (Attar Chocolat)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["gourmand","chocolat","vanille"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-238", name: "عطر الفواكه (Attar Al Fawakih)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","fruits rouges","tropical"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-239", name: "عطر التوت (Attar Al Tout)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","framboise","mûre"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-240", name: "عطر الرمان (Attar Al Rumman)", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["fruité","grenade","frais"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-241", name: "عطر الطهارة (Attar Tahara)", brand: "Jamali Parfum",
    category: "Femme", type: "Musc", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["musc","tahara","propre"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-242", name: "Style Lovely", brand: "Jamali Parfum",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "", tags: ["floral","doux","musc"], isBestseller: false, available: true, createdAt: new Date()
  }
]);

print('Jamali DB initialisee : ' + db.products.countDocuments() + ' parfums inseres.');

// ─── Utilisateur applicatif (readWrite sur jamali_db) ────────────────────────
db.createUser({
  user: "jamali_admin",
  pwd:  "JamaliApp2026",
  roles: [{ role: "readWrite", db: "jamali_db" }]
});

print('User jamali_admin cree avec acces readWrite sur jamali_db.');
