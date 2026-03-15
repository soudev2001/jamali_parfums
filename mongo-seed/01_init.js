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

  // ── Collection Homme ──────────────────────────────────────────────────────
  {
    reference: "JH-001", name: "Bois Précieux", brand: "Jamali Exclusif",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 50,
    image: "https://images.unsplash.com/photo-1614703530089-72c676bb915b?auto=format&fit=crop&q=80&w=400",
    tags: ["boisé","cèdre","vétiver"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-002", name: "Sultan Noir", brand: "Jamali Exclusif",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 35,
    image: "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&q=80&w=400",
    tags: ["oriental","épicé","santal"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JH-003", name: "Azur Casablanca", brand: "Jamali Exclusif",
    category: "Homme", type: "EDT", volume: "100ml", price: 150, stock: 40,
    image: "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?auto=format&fit=crop&q=80&w=400",
    tags: ["aquatique","frais","marin"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JH-004", name: "Ambre du Désert", brand: "Jamali Collection",
    category: "Homme", type: "EDP", volume: "100ml", price: 150, stock: 3,
    image: "https://images.unsplash.com/photo-1615397347318-620251781297?auto=format&fit=crop&q=80&w=400",
    tags: ["ambre","épicé","fumé"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Collection Femme ──────────────────────────────────────────────────────
  {
    reference: "JF-001", name: "Rose de Marrakech", brand: "Jamali Exclusif",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 60,
    image: "https://images.unsplash.com/photo-1595425964070-5b1287c8005d?auto=format&fit=crop&q=80&w=400",
    tags: ["floral","rose","jasmin"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-002", name: "Nuit Dorée", brand: "Jamali Exclusif",
    category: "Femme", type: "EDP", volume: "100ml", price: 150, stock: 45,
    image: "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?auto=format&fit=crop&q=80&w=400",
    tags: ["vanille","oriental","doux"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JF-003", name: "Lune de Jasmin", brand: "Jamali Exclusif",
    category: "Femme", type: "EDT", volume: "100ml", price: 150, stock: 55,
    image: "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&q=80&w=400",
    tags: ["floral","jasmin","musc"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JF-004", name: "Poudre de Soie", brand: "Jamali Collection",
    category: "Femme", type: "Extrait", volume: "50ml", price: 150, stock: 0,
    image: "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&q=80&w=400",
    tags: ["poudré","iris","musc"], isBestseller: false, available: false, createdAt: new Date()
  },

  // ── Collection Mixte ──────────────────────────────────────────────────────
  {
    reference: "JM-001", name: "Atlas Spirit", brand: "Jamali Exclusif",
    category: "Mixte", type: "EDP", volume: "100ml", price: 150, stock: 70,
    image: "https://images.unsplash.com/photo-1584433144859-1f4868f7b593?auto=format&fit=crop&q=80&w=400",
    tags: ["boisé","cèdre","ambre"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JM-002", name: "Musc Satin", brand: "Jamali Collection",
    category: "Mixte", type: "Musc", volume: "100ml", price: 150, stock: 80,
    image: "https://images.unsplash.com/photo-1615397347318-620251781297?auto=format&fit=crop&q=80&w=400",
    tags: ["musc","doux","soyeux"], isBestseller: false, available: true, createdAt: new Date()
  },

  // ── Collection Oriental / Oud ─────────────────────────────────────────────
  {
    reference: "JO-001", name: "Al Oud Royale", brand: "Jamali Oud",
    category: "Oriental", type: "Oud", volume: "100ml", price: 150, stock: 25,
    image: "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&q=80&w=400",
    tags: ["oud","encens","safran"], isBestseller: true, available: true, createdAt: new Date()
  },
  {
    reference: "JO-002", name: "Oud Blanc Céleste", brand: "Jamali Oud",
    category: "Oriental", type: "Oud", volume: "100ml", price: 150, stock: 30,
    image: "https://images.unsplash.com/photo-1584433144859-1f4868f7b593?auto=format&fit=crop&q=80&w=400",
    tags: ["oud blanc","floral","musc"], isBestseller: false, available: true, createdAt: new Date()
  },
  {
    reference: "JO-003", name: "Bakhour Doré", brand: "Jamali Oud",
    category: "Oriental", type: "Oud", volume: "50ml", price: 150, stock: 15,
    image: "https://images.unsplash.com/photo-1614703530089-72c676bb915b?auto=format&fit=crop&q=80&w=400",
    tags: ["bakhour","encens","ambregris"], isBestseller: true, available: true, createdAt: new Date()
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
