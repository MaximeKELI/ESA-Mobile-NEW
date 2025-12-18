-- ============================================
-- SCHÉMA POUR LES 10 FONCTIONNALITÉS PRIORITAIRES
-- ============================================

-- ========== 1. E-LEARNING ==========

-- Table des cours en ligne
CREATE TABLE IF NOT EXISTS cours_online (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    matiere_id INTEGER,
    classe_id INTEGER,
    enseignant_id INTEGER NOT NULL,
    type_cours VARCHAR(20) CHECK(type_cours IN ('video', 'texte', 'mixte', 'interactif')),
    duree_estimee INTEGER, -- en minutes
    niveau_difficulte VARCHAR(20) CHECK(niveau_difficulte IN ('debutant', 'intermediaire', 'avance')),
    is_public BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    date_creation DATE DEFAULT CURRENT_DATE,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (enseignant_id) REFERENCES users(id)
);

-- Table des modules de cours
CREATE TABLE IF NOT EXISTS modules_cours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cours_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER NOT NULL,
    type_module VARCHAR(20) CHECK(type_module IN ('video', 'texte', 'quiz', 'devoir', 'ressource')),
    contenu TEXT, -- JSON ou texte
    duree_estimee INTEGER,
    is_obligatoire BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cours_id) REFERENCES cours_online(id) ON DELETE CASCADE
);

-- Table des vidéos
CREATE TABLE IF NOT EXISTS videos_cours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    url_video VARCHAR(500),
    duree_secondes INTEGER,
    transcription TEXT,
    sous_titres_path VARCHAR(255),
    is_telechargeable BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules_cours(id) ON DELETE CASCADE
);

-- Table des quiz
CREATE TABLE IF NOT EXISTS quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER,
    cours_id INTEGER,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_quiz VARCHAR(20) CHECK(type_quiz IN ('formative', 'sommatif', 'auto_evaluation')),
    duree_minutes INTEGER,
    nombre_tentatives_max INTEGER DEFAULT 3,
    note_minimale DECIMAL(4,2) DEFAULT 10.0,
    is_actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules_cours(id),
    FOREIGN KEY (cours_id) REFERENCES cours_online(id)
);

-- Table des questions de quiz
CREATE TABLE IF NOT EXISTS questions_quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    type_question VARCHAR(20) CHECK(type_question IN ('choix_multiple', 'vrai_faux', 'texte_libre', 'numerique')),
    points DECIMAL(4,2) DEFAULT 1.0,
    ordre INTEGER NOT NULL,
    reponses_possibles TEXT, -- JSON array
    reponse_correcte TEXT, -- JSON
    explication TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
);

-- Table des tentatives de quiz
CREATE TABLE IF NOT EXISTS tentatives_quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    note_obtenue DECIMAL(4,2),
    nombre_tentative INTEGER DEFAULT 1,
    date_tentative TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duree_secondes INTEGER,
    reponses TEXT, -- JSON
    is_termine BOOLEAN DEFAULT 0,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
);

-- Table des devoirs en ligne
CREATE TABLE IF NOT EXISTS devoirs_online (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cours_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_publication DATE DEFAULT CURRENT_DATE,
    date_limite DATE NOT NULL,
    points_maximaux DECIMAL(4,2) DEFAULT 20.0,
    type_devoir VARCHAR(20) CHECK(type_devoir IN ('individuel', 'groupe', 'presentation')),
    consignes TEXT,
    fichiers_attaches TEXT, -- JSON array
    is_actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cours_id) REFERENCES cours_online(id)
);

-- Table des soumissions de devoirs
CREATE TABLE IF NOT EXISTS soumissions_devoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    devoir_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    contenu TEXT,
    fichiers_paths TEXT, -- JSON array
    date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note DECIMAL(4,2),
    commentaires TEXT,
    corrige_par INTEGER,
    date_correction TIMESTAMP,
    statut VARCHAR(20) DEFAULT 'soumis' CHECK(statut IN ('soumis', 'en_correction', 'corrige', 'retourne')),
    FOREIGN KEY (devoir_id) REFERENCES devoirs_online(id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (corrige_par) REFERENCES users(id)
);

-- Table de progression des cours
CREATE TABLE IF NOT EXISTS progression_cours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cours_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    module_id INTEGER,
    pourcentage_completion DECIMAL(5,2) DEFAULT 0,
    date_debut DATE,
    date_derniere_activite TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temps_total_minutes INTEGER DEFAULT 0,
    is_termine BOOLEAN DEFAULT 0,
    date_completion DATE,
    certificat_path VARCHAR(255),
    FOREIGN KEY (cours_id) REFERENCES cours_online(id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (module_id) REFERENCES modules_cours(id),
    UNIQUE(cours_id, etudiant_id)
);

-- ========== 2. PRÉDICTION ML ==========

-- Table des modèles ML
CREATE TABLE IF NOT EXISTS modeles_ml (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    type_modele VARCHAR(50) CHECK(type_modele IN ('classification', 'regression', 'clustering')),
    version VARCHAR(20),
    chemin_modele VARCHAR(255),
    precision DECIMAL(5,2),
    date_entrainement DATE,
    parametres TEXT, -- JSON
    is_actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des prédictions
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    modele_id INTEGER NOT NULL,
    type_prediction VARCHAR(50) CHECK(type_prediction IN ('reussite', 'abandon', 'inscription', 'paiement')),
    prediction_valeur DECIMAL(5,2), -- Probabilité ou valeur
    confiance DECIMAL(5,2),
    facteurs_risque TEXT, -- JSON
    recommandations TEXT, -- JSON
    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_validee BOOLEAN DEFAULT 0,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (modele_id) REFERENCES modeles_ml(id)
);

-- Table des données d'entraînement
CREATE TABLE IF NOT EXISTS donnees_entrainement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER,
    annee_academique VARCHAR(20),
    moyenne_generale DECIMAL(4,2),
    nombre_absences INTEGER,
    nombre_retards INTEGER,
    solde_impaye DECIMAL(10,2),
    nombre_notes_bonnes INTEGER,
    nombre_notes_faibles INTEGER,
    resultat_reel VARCHAR(20), -- 'reussi', 'echec', 'abandon'
    date_collecte DATE DEFAULT CURRENT_DATE
);

-- ========== 3. MOBILE MONEY ==========

-- Table des transactions Mobile Money
CREATE TABLE IF NOT EXISTS transactions_mobile_money (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_frais_id INTEGER,
    montant DECIMAL(10,2) NOT NULL,
    operateur VARCHAR(20) CHECK(operateur IN ('moov', 'togocel', 'autre')),
    numero_telephone VARCHAR(20) NOT NULL,
    reference_transaction VARCHAR(100) UNIQUE,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'validee', 'echec', 'annulee')),
    date_transaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_validation TIMESTAMP,
    callback_data TEXT, -- JSON des données du callback
    webhook_received BOOLEAN DEFAULT 0,
    date_webhook TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (type_frais_id) REFERENCES types_frais(id)
);

-- Table de configuration Mobile Money
CREATE TABLE IF NOT EXISTS config_mobile_money (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operateur VARCHAR(20) UNIQUE NOT NULL,
    api_url VARCHAR(255),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    merchant_id VARCHAR(100),
    webhook_url VARCHAR(255),
    is_actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 4. CHAT TEMPS RÉEL ==========

-- Table des conversations
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_conversation VARCHAR(20) CHECK(type_conversation IN ('individuelle', 'groupe', 'classe', 'matiere')),
    titre VARCHAR(200),
    createur_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (createur_id) REFERENCES users(id)
);

-- Table des participants aux conversations
CREATE TABLE IF NOT EXISTS participants_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) DEFAULT 'membre' CHECK(role IN ('admin', 'moderateur', 'membre')),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_derniere_lecture TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(conversation_id, user_id)
);

-- Table des messages chat (complément à messages existante)
CREATE TABLE IF NOT EXISTS messages_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    expediteur_id INTEGER NOT NULL,
    contenu TEXT NOT NULL,
    type_message VARCHAR(20) DEFAULT 'texte' CHECK(type_message IN ('texte', 'fichier', 'image', 'audio', 'video')),
    fichier_path VARCHAR(255),
    is_edite BOOLEAN DEFAULT 0,
    date_edition TIMESTAMP,
    is_supprime BOOLEAN DEFAULT 0,
    date_suppression TIMESTAMP,
    reponse_a INTEGER, -- ID du message auquel on répond
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (expediteur_id) REFERENCES users(id),
    FOREIGN KEY (reponse_a) REFERENCES messages_chat(id)
);

-- Table de présence (online/offline)
CREATE TABLE IF NOT EXISTS presence_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    is_online BOOLEAN DEFAULT 0,
    derniere_activite TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_info TEXT, -- JSON
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id)
);

-- ========== 5. WORKFLOWS AUTOMATISÉS ==========

-- Table des workflows
CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    type_workflow VARCHAR(50) CHECK(type_workflow IN ('inscription', 'validation_note', 'paiement', 'deliberation', 'personnalise')),
    is_actif BOOLEAN DEFAULT 1,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Table des étapes de workflow
CREATE TABLE IF NOT EXISTS etapes_workflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    ordre INTEGER NOT NULL,
    nom VARCHAR(100) NOT NULL,
    type_etape VARCHAR(50) CHECK(type_etape IN ('condition', 'action', 'approbation', 'notification', 'attente')),
    conditions TEXT, -- JSON
    actions TEXT, -- JSON
    approbateur_role VARCHAR(20),
    timeout_jours INTEGER,
    is_obligatoire BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Table des instances de workflow
CREATE TABLE IF NOT EXISTS instances_workflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    entite_type VARCHAR(50), -- 'etudiant', 'paiement', 'note', etc.
    entite_id INTEGER,
    etape_actuelle_id INTEGER,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK(statut IN ('en_cours', 'termine', 'bloque', 'annule')),
    donnees_contexte TEXT, -- JSON
    date_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_fin TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id),
    FOREIGN KEY (etape_actuelle_id) REFERENCES etapes_workflow(id)
);

-- Table de l'historique des workflows
CREATE TABLE IF NOT EXISTS historique_workflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    etape_id INTEGER NOT NULL,
    action_effectuee VARCHAR(100),
    acteur_id INTEGER,
    resultat TEXT, -- JSON
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES instances_workflow(id),
    FOREIGN KEY (etape_id) REFERENCES etapes_workflow(id),
    FOREIGN KEY (acteur_id) REFERENCES users(id)
);

-- ========== 6. TABLEAUX DE BORD PERSONNALISABLES ==========

-- Table des widgets
CREATE TABLE IF NOT EXISTS widgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    type_widget VARCHAR(50) CHECK(type_widget IN ('graphique', 'statistique', 'liste', 'calendrier', 'personnalise')),
    description TEXT,
    configuration_defaut TEXT, -- JSON
    is_systeme BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des tableaux de bord
CREATE TABLE IF NOT EXISTS tableaux_bord (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nom VARCHAR(100) NOT NULL,
    is_par_defaut BOOLEAN DEFAULT 0,
    layout TEXT, -- JSON (position des widgets)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des widgets dans les tableaux de bord
CREATE TABLE IF NOT EXISTS widgets_tableaux_bord (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tableau_bord_id INTEGER NOT NULL,
    widget_id INTEGER NOT NULL,
    position_x INTEGER,
    position_y INTEGER,
    largeur INTEGER DEFAULT 1,
    hauteur INTEGER DEFAULT 1,
    configuration TEXT, -- JSON (filtres, paramètres)
    ordre INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tableau_bord_id) REFERENCES tableaux_bord(id) ON DELETE CASCADE,
    FOREIGN KEY (widget_id) REFERENCES widgets(id)
);

-- ========== 7. PORTFOLIO NUMÉRIQUE ==========

-- Table des portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL UNIQUE,
    titre VARCHAR(200),
    description TEXT,
    is_public BOOLEAN DEFAULT 0,
    url_public VARCHAR(255),
    theme VARCHAR(50),
    date_creation DATE DEFAULT CURRENT_DATE,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
);

-- Table des compétences
CREATE TABLE IF NOT EXISTS competences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    categorie VARCHAR(50),
    niveau_max INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des compétences acquises
CREATE TABLE IF NOT EXISTS competences_acquises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    competence_id INTEGER NOT NULL,
    niveau INTEGER DEFAULT 1,
    date_acquisition DATE DEFAULT CURRENT_DATE,
    preuve_path VARCHAR(255), -- Lien vers preuve
    valide_par INTEGER,
    date_validation TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competences(id),
    FOREIGN KEY (valide_par) REFERENCES users(id)
);

-- Table des projets portfolio
CREATE TABLE IF NOT EXISTS projets_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_projet VARCHAR(50),
    date_realisation DATE,
    technologies TEXT, -- JSON array
    fichiers_paths TEXT, -- JSON array
    lien_externe VARCHAR(255),
    is_visible BOOLEAN DEFAULT 1,
    ordre INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE)
);

-- Table des certifications portfolio
CREATE TABLE IF NOT EXISTS certifications_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    nom_certification VARCHAR(200) NOT NULL,
    organisme VARCHAR(100),
    date_obtention DATE NOT NULL,
    date_expiration DATE,
    numero_certificat VARCHAR(100),
    fichier_path VARCHAR(255),
    lien_verification VARCHAR(255),
    is_visible BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

-- Table des réalisations
CREATE TABLE IF NOT EXISTS realisations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_realisation VARCHAR(50),
    date_realisation DATE,
    impact TEXT,
    preuves TEXT, -- JSON array
    is_visible BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

-- ========== 8. GAMIFICATION (Amélioration) ==========

-- Table des points (déjà géré dans gamification, mais ajoutons une table de suivi)
CREATE TABLE IF NOT EXISTS historique_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    points INTEGER NOT NULL,
    type_action VARCHAR(50), -- 'bonne_note', 'assiduite', 'paiement', etc.
    description TEXT,
    reference_id INTEGER, -- ID de l'action qui a généré les points
    date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des badges
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    icone_path VARCHAR(255),
    categorie VARCHAR(50),
    points_requis INTEGER DEFAULT 0,
    conditions TEXT, -- JSON
    is_rare BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des badges obtenus
CREATE TABLE IF NOT EXISTS badges_obtenus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    date_obtention TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id),
    UNIQUE(user_id, badge_id)
);

-- Table des défis
CREATE TABLE IF NOT EXISTS defis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_defi VARCHAR(50),
    objectif TEXT, -- JSON
    recompense_points INTEGER DEFAULT 0,
    recompense_badge_id INTEGER,
    date_debut DATE,
    date_fin DATE,
    is_actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recompense_badge_id) REFERENCES badges(id)
);

-- ========== 9. CHATBOT INTELLIGENT ==========

-- Table des conversations chatbot
CREATE TABLE IF NOT EXISTS conversations_chatbot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    contexte TEXT, -- JSON
    derniere_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des messages chatbot
CREATE TABLE IF NOT EXISTS messages_chatbot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    message_utilisateur TEXT,
    reponse_bot TEXT,
    intention VARCHAR(100),
    confiance DECIMAL(4,2),
    date_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations_chatbot(id) ON DELETE CASCADE
);

-- Table de la base de connaissances
CREATE TABLE IF NOT EXISTS base_connaissances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    reponse TEXT NOT NULL,
    categorie VARCHAR(50),
    tags TEXT, -- JSON array
    score_utilite INTEGER DEFAULT 0,
    nombre_utilisations INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 10. EXPORT AVANCÉ ==========

-- Table des templates d'export
CREATE TABLE IF NOT EXISTS templates_export (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    type_export VARCHAR(50) CHECK(type_export IN ('pdf', 'excel', 'csv', 'json', 'xml')),
    categorie VARCHAR(50),
    template_path VARCHAR(255),
    configuration TEXT, -- JSON
    is_systeme BOOLEAN DEFAULT 0,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Table de l'historique des exports
CREATE TABLE IF NOT EXISTS historique_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER,
    type_export VARCHAR(50),
    fichier_path VARCHAR(255),
    parametres TEXT, -- JSON
    nombre_lignes INTEGER,
    taille_fichier INTEGER, -- en bytes
    date_export TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (template_id) REFERENCES templates_export(id)
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_progression_cours ON progression_cours(cours_id, etudiant_id);
CREATE INDEX IF NOT EXISTS idx_predictions_etudiant ON predictions(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_mm ON transactions_mobile_money(statut, date_transaction);
CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages_chat(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_instances_workflow ON instances_workflow(statut, workflow_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_etudiant ON portfolios(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_badges_obtenus ON badges_obtenus(user_id);

