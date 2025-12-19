-- ============================================
-- SCHÉMA DE BASE DE DONNÉES - ESA TOGO
-- Application de Gestion Scolaire
-- ============================================

-- Table des utilisateurs (tous les profils)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'comptabilite', 'enseignant', 'etudiant', 'parent')),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20),
    adresse TEXT,
    photo_path VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP
);

-- Table des années académiques
CREATE TABLE IF NOT EXISTS annees_academiques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    is_active BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des filières
CREATE TABLE IF NOT EXISTS filieres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des niveaux
CREATE TABLE IF NOT EXISTS niveaux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    ordre INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des classes
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    filiere_id INTEGER NOT NULL,
    niveau_id INTEGER NOT NULL,
    annee_academique_id INTEGER NOT NULL,
    effectif_max INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filiere_id) REFERENCES filieres(id),
    FOREIGN KEY (niveau_id) REFERENCES niveaux(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des matières
CREATE TABLE IF NOT EXISTS matieres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    coefficient DECIMAL(3,2) DEFAULT 1.0,
    volume_horaire INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de liaison classe-matière
CREATE TABLE IF NOT EXISTS classe_matieres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe_id INTEGER NOT NULL,
    matiere_id INTEGER NOT NULL,
    enseignant_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (enseignant_id) REFERENCES users(id)
);

-- Table des étudiants
CREATE TABLE IF NOT EXISTS etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    numero_etudiant VARCHAR(20) UNIQUE NOT NULL,
    date_naissance DATE,
    lieu_naissance VARCHAR(100),
    sexe VARCHAR(10) CHECK(sexe IN ('M', 'F')),
    nationalite VARCHAR(50),
    classe_id INTEGER,
    annee_academique_id INTEGER NOT NULL,
    date_inscription DATE DEFAULT CURRENT_DATE,
    qr_code_path VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des parents
CREATE TABLE IF NOT EXISTS parents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    profession VARCHAR(100),
    lien_parente VARCHAR(50) CHECK(lien_parente IN ('pere', 'mere', 'tuteur')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table de liaison parent-étudiant
CREATE TABLE IF NOT EXISTS parent_etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    is_principal BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES parents(id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    UNIQUE(parent_id, etudiant_id)
);

-- Table des enseignants
CREATE TABLE IF NOT EXISTS enseignants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    specialite VARCHAR(100),
    date_embauche DATE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des types de frais
CREATE TABLE IF NOT EXISTS types_frais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    is_obligatoire BOOLEAN DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des frais par classe
CREATE TABLE IF NOT EXISTS frais_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe_id INTEGER NOT NULL,
    type_frais_id INTEGER NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    annee_academique_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (type_frais_id) REFERENCES types_frais(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des paiements
CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_frais_id INTEGER NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    mode_paiement VARCHAR(20) CHECK(mode_paiement IN ('especes', 'mobile_money', 'virement')),
    reference_paiement VARCHAR(100),
    date_paiement DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'valide', 'rejete')),
    valide_par INTEGER,
    date_validation TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (type_frais_id) REFERENCES types_frais(id),
    FOREIGN KEY (valide_par) REFERENCES users(id)
);

-- Table des tranches de paiement
CREATE TABLE IF NOT EXISTS tranches_paiement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_frais_id INTEGER NOT NULL,
    montant_total DECIMAL(10,2) NOT NULL,
    montant_paye DECIMAL(10,2) DEFAULT 0,
    nombre_tranches INTEGER DEFAULT 1,
    date_echeance DATE,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK(statut IN ('en_cours', 'paye', 'en_retard')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (type_frais_id) REFERENCES types_frais(id)
);

-- Table des notes
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    matiere_id INTEGER NOT NULL,
    classe_id INTEGER NOT NULL,
    type_note VARCHAR(20) CHECK(type_note IN ('devoir', 'controle', 'examen')),
    note DECIMAL(4,2) NOT NULL CHECK(note >= 0 AND note <= 20),
    coefficient DECIMAL(3,2) DEFAULT 1.0,
    date_note DATE DEFAULT CURRENT_DATE,
    enseignant_id INTEGER NOT NULL,
    is_valide BOOLEAN DEFAULT 0,
    valide_par INTEGER,
    date_validation TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (enseignant_id) REFERENCES users(id),
    FOREIGN KEY (valide_par) REFERENCES users(id)
);

-- Table d'historique des modifications de notes
CREATE TABLE IF NOT EXISTS notes_historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    ancienne_note DECIMAL(4,2),
    nouvelle_note DECIMAL(4,2),
    modifie_par INTEGER NOT NULL,
    raison TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id),
    FOREIGN KEY (modifie_par) REFERENCES users(id)
);

-- Table des moyennes
CREATE TABLE IF NOT EXISTS moyennes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    matiere_id INTEGER NOT NULL,
    classe_id INTEGER NOT NULL,
    moyenne DECIMAL(4,2) NOT NULL,
    periode VARCHAR(20) CHECK(periode IN ('trimestre1', 'trimestre2', 'trimestre3', 'annuel')),
    annee_academique_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des classements
CREATE TABLE IF NOT EXISTS classements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    classe_id INTEGER NOT NULL,
    rang INTEGER NOT NULL,
    moyenne_generale DECIMAL(4,2) NOT NULL,
    periode VARCHAR(20) CHECK(periode IN ('trimestre1', 'trimestre2', 'trimestre3', 'annuel')),
    annee_academique_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des décisions académiques
CREATE TABLE IF NOT EXISTS decisions_academiques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    classe_id INTEGER NOT NULL,
    decision VARCHAR(50) CHECK(decision IN ('admis', 'redouble', 'exclu', 'passage_conditionnel')),
    moyenne_generale DECIMAL(4,2),
    periode VARCHAR(20),
    annee_academique_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des absences
CREATE TABLE IF NOT EXISTS absences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    classe_id INTEGER NOT NULL,
    matiere_id INTEGER,
    date_absence DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    type_absence VARCHAR(20) CHECK(type_absence IN ('absence', 'retard', 'justifie')),
    justificatif TEXT,
    enseignant_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (enseignant_id) REFERENCES users(id)
);

-- Table des emplois du temps
CREATE TABLE IF NOT EXISTS emplois_temps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe_id INTEGER NOT NULL,
    matiere_id INTEGER NOT NULL,
    enseignant_id INTEGER NOT NULL,
    jour_semaine VARCHAR(10) CHECK(jour_semaine IN ('lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi')),
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    salle VARCHAR(50),
    annee_academique_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (enseignant_id) REFERENCES users(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des examens
CREATE TABLE IF NOT EXISTS examens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    type_examen VARCHAR(20) CHECK(type_examen IN ('devoir', 'controle', 'examen_final')),
    date_examen DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    classe_id INTEGER,
    matiere_id INTEGER,
    coefficient DECIMAL(3,2) DEFAULT 1.0,
    annee_academique_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des délibérations
CREATE TABLE IF NOT EXISTS deliberations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe_id INTEGER NOT NULL,
    periode VARCHAR(20) NOT NULL,
    annee_academique_id INTEGER NOT NULL,
    date_deliberation DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK(statut IN ('en_cours', 'termine', 'valide')),
    valide_par INTEGER,
    date_validation TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id),
    FOREIGN KEY (valide_par) REFERENCES users(id)
);

-- Table des annonces
CREATE TABLE IF NOT EXISTS annonces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(200) NOT NULL,
    contenu TEXT NOT NULL,
    type_annonce VARCHAR(20) CHECK(type_annonce IN ('generale', 'classe', 'filiere', 'urgence')),
    destinataires TEXT, -- JSON array des IDs de classes/étudiants
    auteur_id INTEGER NOT NULL,
    is_urgent BOOLEAN DEFAULT 0,
    date_publication TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_expiration DATE,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (auteur_id) REFERENCES users(id)
);

-- Table des messages internes
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expediteur_id INTEGER NOT NULL,
    destinataire_id INTEGER NOT NULL,
    sujet VARCHAR(200),
    contenu TEXT NOT NULL,
    is_lu BOOLEAN DEFAULT 0,
    date_lecture TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expediteur_id) REFERENCES users(id),
    FOREIGN KEY (destinataire_id) REFERENCES users(id)
);

-- Table des notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type_notification VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    lien VARCHAR(255),
    is_lu BOOLEAN DEFAULT 0,
    date_lecture TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des logs de connexion
CREATE TABLE IF NOT EXISTS logs_connexion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    statut VARCHAR(20) CHECK(statut IN ('succes', 'echec')),
    raison_echec VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des logs d'actions
CREATE TABLE IF NOT EXISTS logs_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 0,
    action VARCHAR(100) NOT NULL,
    table_affectee VARCHAR(50),
    enregistrement_id INTEGER,
    anciennes_valeurs TEXT, -- JSON
    nouvelles_valeurs TEXT, -- JSON
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des paramètres globaux
CREATE TABLE IF NOT EXISTS parametres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cle VARCHAR(100) UNIQUE NOT NULL,
    valeur TEXT NOT NULL,
    type_valeur VARCHAR(20) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_etudiants_classe ON etudiants(classe_id);
CREATE INDEX IF NOT EXISTS idx_etudiants_numero ON etudiants(numero_etudiant);
CREATE INDEX IF NOT EXISTS idx_notes_etudiant ON notes(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_notes_matiere ON notes(matiere_id);
CREATE INDEX IF NOT EXISTS idx_paiements_etudiant ON paiements(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_paiements_statut ON paiements(statut);
CREATE INDEX IF NOT EXISTS idx_absences_etudiant ON absences(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_messages_destinataire ON messages(destinataire_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);

