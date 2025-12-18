-- ============================================
-- SCHÉMA ÉTENDU - MODULES COMPLÉMENTAIRES
-- Application de Gestion Scolaire Complète
-- ============================================

-- ========== MODULE INSCRIPTIONS EN LIGNE ==========

-- Table des candidatures
CREATE TABLE IF NOT EXISTS candidatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_dossier VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    lieu_naissance VARCHAR(100),
    sexe VARCHAR(10) CHECK(sexe IN ('M', 'F')),
    nationalite VARCHAR(50),
    email VARCHAR(100) NOT NULL,
    telephone VARCHAR(20),
    adresse TEXT,
    filiere_souhaitee_id INTEGER,
    niveau_souhaite_id INTEGER,
    diplome_obtenu VARCHAR(200),
    etablissement_origine VARCHAR(200),
    annee_obtention INTEGER,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'acceptee', 'refusee', 'liste_attente')),
    date_candidature DATE DEFAULT CURRENT_DATE,
    date_traitement DATE,
    traite_par INTEGER,
    notes_complementaires TEXT,
    documents_paths TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filiere_souhaitee_id) REFERENCES filieres(id),
    FOREIGN KEY (niveau_souhaite_id) REFERENCES niveaux(id),
    FOREIGN KEY (traite_par) REFERENCES users(id)
);

-- Table des concours d'entrée
CREATE TABLE IF NOT EXISTS concours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    date_concours DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    lieu VARCHAR(200),
    nombre_places INTEGER,
    filiere_id INTEGER,
    annee_academique_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filiere_id) REFERENCES filieres(id),
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des résultats de concours
CREATE TABLE IF NOT EXISTS resultats_concours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concours_id INTEGER NOT NULL,
    candidature_id INTEGER NOT NULL,
    note_ecrit DECIMAL(4,2),
    note_oral DECIMAL(4,2),
    note_totale DECIMAL(4,2),
    rang INTEGER,
    statut VARCHAR(20) CHECK(statut IN ('admis', 'liste_attente', 'refuse')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (concours_id) REFERENCES concours(id),
    FOREIGN KEY (candidature_id) REFERENCES candidatures(id)
);

-- ========== MODULE PRÉREQUIS ET ÉQUIVALENCES ==========

-- Table des prérequis
CREATE TABLE IF NOT EXISTS prerequis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matiere_id INTEGER NOT NULL,
    prerequis_matiere_id INTEGER NOT NULL,
    niveau_requis DECIMAL(4,2) DEFAULT 10.0,
    is_obligatoire BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (prerequis_matiere_id) REFERENCES matieres(id)
);

-- Table des équivalences
CREATE TABLE IF NOT EXISTS equivalences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    matiere_origine VARCHAR(100) NOT NULL,
    etablissement_origine VARCHAR(200),
    matiere_equivalente_id INTEGER NOT NULL,
    note_equivalente DECIMAL(4,2),
    date_equivalence DATE DEFAULT CURRENT_DATE,
    valide_par INTEGER NOT NULL,
    date_validation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (matiere_equivalente_id) REFERENCES matieres(id),
    FOREIGN KEY (valide_par) REFERENCES users(id)
);

-- Table des transferts étudiants
CREATE TABLE IF NOT EXISTS transferts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    etablissement_origine VARCHAR(200),
    filiere_origine VARCHAR(100),
    niveau_origine VARCHAR(50),
    etablissement_destination VARCHAR(200),
    filiere_destination_id INTEGER,
    niveau_destination_id INTEGER,
    type_transfert VARCHAR(20) CHECK(type_transfert IN ('entrant', 'sortant', 'interne')),
    date_transfert DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK(statut IN ('en_cours', 'valide', 'rejete')),
    documents_paths TEXT, -- JSON array
    traite_par INTEGER,
    date_traitement TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (filiere_destination_id) REFERENCES filieres(id),
    FOREIGN KEY (niveau_destination_id) REFERENCES niveaux(id),
    FOREIGN KEY (traite_par) REFERENCES users(id)
);

-- ========== MODULE BOURSES ET AIDES ==========

-- Table des types de bourses
CREATE TABLE IF NOT EXISTS types_bourses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    duree_mois INTEGER DEFAULT 12,
    criteres_eligibilite TEXT,
    nombre_places INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des attributions de bourses
CREATE TABLE IF NOT EXISTS bourses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_bourse_id INTEGER NOT NULL,
    montant_total DECIMAL(10,2) NOT NULL,
    montant_mensuel DECIMAL(10,2),
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'active' CHECK(statut IN ('active', 'suspendue', 'terminee', 'annulee')),
    raison_suspension TEXT,
    attribue_par INTEGER NOT NULL,
    date_attribution DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (type_bourse_id) REFERENCES types_bourses(id),
    FOREIGN KEY (attribue_par) REFERENCES users(id)
);

-- Table des paiements de bourses
CREATE TABLE IF NOT EXISTS paiements_bourses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bourse_id INTEGER NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    mois_paye VARCHAR(20) NOT NULL,
    date_paiement DATE DEFAULT CURRENT_DATE,
    mode_paiement VARCHAR(20),
    reference_paiement VARCHAR(100),
    valide_par INTEGER,
    date_validation TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bourse_id) REFERENCES bourses(id),
    FOREIGN KEY (valide_par) REFERENCES users(id)
);

-- ========== MODULE RESSOURCES HUMAINES ==========

-- Table des types de personnel
CREATE TABLE IF NOT EXISTS types_personnel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    description TEXT
);

-- Table des postes
CREATE TABLE IF NOT EXISTS postes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    type_personnel_id INTEGER,
    description TEXT,
    salaire_base DECIMAL(10,2),
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (type_personnel_id) REFERENCES types_personnel(id)
);

-- Table des contrats
CREATE TABLE IF NOT EXISTS contrats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    poste_id INTEGER NOT NULL,
    type_contrat VARCHAR(20) CHECK(type_contrat IN ('CDI', 'CDD', 'STAGE', 'CONSULTANT', 'VACATAIRE')),
    date_debut DATE NOT NULL,
    date_fin DATE,
    salaire DECIMAL(10,2),
    statut VARCHAR(20) DEFAULT 'actif' CHECK(statut IN ('actif', 'suspendu', 'resilie', 'termine')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personnel_id) REFERENCES users(id),
    FOREIGN KEY (poste_id) REFERENCES postes(id)
);

-- Table des congés
CREATE TABLE IF NOT EXISTS conges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    type_conge VARCHAR(20) CHECK(type_conge IN ('annuel', 'maladie', 'maternite', 'paternite', 'exceptionnel', 'sans_solde')),
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    nombre_jours INTEGER NOT NULL,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'approuve', 'rejete')),
    approuve_par INTEGER,
    date_approbation TIMESTAMP,
    raison TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personnel_id) REFERENCES users(id),
    FOREIGN KEY (approuve_par) REFERENCES users(id)
);

-- Table des évaluations du personnel
CREATE TABLE IF NOT EXISTS evaluations_personnel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    evaluateur_id INTEGER NOT NULL,
    periode VARCHAR(20) NOT NULL,
    annee INTEGER NOT NULL,
    note_globale DECIMAL(4,2),
    commentaires TEXT,
    points_forts TEXT,
    points_amelioration TEXT,
    date_evaluation DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personnel_id) REFERENCES users(id),
    FOREIGN KEY (evaluateur_id) REFERENCES users(id)
);

-- ========== MODULE INFRASTRUCTURE ==========

-- Table des salles
CREATE TABLE IF NOT EXISTS salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    type_salle VARCHAR(20) CHECK(type_salle IN ('classe', 'amphitheatre', 'laboratoire', 'bibliotheque', 'bureau', 'salle_reunion', 'autre')),
    capacite INTEGER,
    equipements TEXT, -- JSON array
    batiment VARCHAR(50),
    etage INTEGER,
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des réservations de salles
CREATE TABLE IF NOT EXISTS reservations_salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salle_id INTEGER NOT NULL,
    reserve_par INTEGER NOT NULL,
    date_reservation DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    motif VARCHAR(200),
    type_reservation VARCHAR(20) CHECK(type_reservation IN ('cours', 'examen', 'reunion', 'evenement', 'autre')),
    statut VARCHAR(20) DEFAULT 'confirmee' CHECK(statut IN ('confirmee', 'annulee', 'terminee')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (salle_id) REFERENCES salles(id),
    FOREIGN KEY (reserve_par) REFERENCES users(id)
);

-- Table des équipements
CREATE TABLE IF NOT EXISTS equipements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    type_equipement VARCHAR(50),
    marque VARCHAR(50),
    modele VARCHAR(50),
    numero_serie VARCHAR(100),
    date_acquisition DATE,
    valeur_acquisition DECIMAL(10,2),
    etat VARCHAR(20) CHECK(etat IN ('neuf', 'bon', 'moyen', 'mauvais', 'hors_service')),
    salle_id INTEGER,
    fournisseur VARCHAR(100),
    garantie_jusqu_a DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (salle_id) REFERENCES salles(id)
);

-- Table de maintenance
CREATE TABLE IF NOT EXISTS maintenances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipement_id INTEGER,
    salle_id INTEGER,
    type_maintenance VARCHAR(20) CHECK(type_maintenance IN ('preventive', 'corrective', 'reparation')),
    description TEXT NOT NULL,
    date_intervention DATE NOT NULL,
    technicien VARCHAR(100),
    cout DECIMAL(10,2),
    statut VARCHAR(20) DEFAULT 'planifiee' CHECK(statut IN ('planifiee', 'en_cours', 'terminee', 'annulee')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipement_id) REFERENCES equipements(id),
    FOREIGN KEY (salle_id) REFERENCES salles(id)
);

-- ========== MODULE BIBLIOTHÈQUE ==========

-- Table des ouvrages
CREATE TABLE IF NOT EXISTS ouvrages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn VARCHAR(20),
    titre VARCHAR(200) NOT NULL,
    auteur VARCHAR(200),
    editeur VARCHAR(100),
    annee_publication INTEGER,
    langue VARCHAR(20) DEFAULT 'français',
    categorie VARCHAR(50),
    nombre_exemplaires INTEGER DEFAULT 1,
    nombre_disponibles INTEGER DEFAULT 1,
    cote VARCHAR(50),
    description TEXT,
    image_couverture VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des exemplaires
CREATE TABLE IF NOT EXISTS exemplaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ouvrage_id INTEGER NOT NULL,
    numero_exemplaire VARCHAR(20) UNIQUE NOT NULL,
    etat VARCHAR(20) CHECK(etat IN ('neuf', 'bon', 'moyen', 'mauvais', 'perdu')),
    date_acquisition DATE,
    prix_acquisition DECIMAL(10,2),
    localisation VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ouvrage_id) REFERENCES ouvrages(id)
);

-- Table des emprunts
CREATE TABLE IF NOT EXISTS emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exemplaire_id INTEGER NOT NULL,
    emprunteur_id INTEGER NOT NULL,
    date_emprunt DATE DEFAULT CURRENT_DATE,
    date_retour_prevue DATE NOT NULL,
    date_retour_effective DATE,
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK(statut IN ('en_cours', 'retourne', 'retarde', 'perdu')),
    nombre_prolongations INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exemplaire_id) REFERENCES exemplaires(id),
    FOREIGN KEY (emprunteur_id) REFERENCES users(id)
);

-- Table des réservations bibliothèque
CREATE TABLE IF NOT EXISTS reservations_bibliotheque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ouvrage_id INTEGER NOT NULL,
    reserve_par INTEGER NOT NULL,
    date_reservation DATE DEFAULT CURRENT_DATE,
    date_expiration DATE,
    statut VARCHAR(20) DEFAULT 'active' CHECK(statut IN ('active', 'satisfaite', 'expiree', 'annulee')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ouvrage_id) REFERENCES ouvrages(id),
    FOREIGN KEY (reserve_par) REFERENCES users(id)
);

-- Table des amendes
CREATE TABLE IF NOT EXISTS amendes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emprunt_id INTEGER NOT NULL,
    type_amende VARCHAR(20) CHECK(type_amende IN ('retard', 'perte', 'degat')),
    montant DECIMAL(10,2) NOT NULL,
    date_amende DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'impayee' CHECK(statut IN ('impayee', 'payee', 'annulee')),
    date_paiement DATE,
    notes TEXT,
    FOREIGN KEY (emprunt_id) REFERENCES emprunts(id)
);

-- ========== MODULE STAGES ==========

-- Table des entreprises
CREATE TABLE IF NOT EXISTS entreprises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raison_sociale VARCHAR(200) NOT NULL,
    secteur_activite VARCHAR(100),
    adresse TEXT,
    telephone VARCHAR(20),
    email VARCHAR(100),
    site_web VARCHAR(200),
    contact_nom VARCHAR(100),
    contact_prenom VARCHAR(100),
    contact_poste VARCHAR(100),
    contact_telephone VARCHAR(20),
    contact_email VARCHAR(100),
    type_partenaire VARCHAR(20) CHECK(type_partenaire IN ('stage', 'alternance', 'emploi', 'autre')),
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des offres de stage
CREATE TABLE IF NOT EXISTS offres_stage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entreprise_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_mois INTEGER,
    date_debut DATE,
    date_fin DATE,
    remuneration DECIMAL(10,2),
    filiere_id INTEGER,
    niveau_requis VARCHAR(50),
    nombre_places INTEGER DEFAULT 1,
    competences_requises TEXT,
    statut VARCHAR(20) DEFAULT 'ouverte' CHECK(statut IN ('ouverte', 'fermee', 'pourvue')),
    date_publication DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id),
    FOREIGN KEY (filiere_id) REFERENCES filieres(id)
);

-- Table des conventions de stage
CREATE TABLE IF NOT EXISTS conventions_stage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    offre_stage_id INTEGER NOT NULL,
    entreprise_id INTEGER NOT NULL,
    tuteur_entreprise VARCHAR(200),
    tuteur_ecole_id INTEGER,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    objectifs TEXT,
    taches TEXT,
    remuneration DECIMAL(10,2),
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'validee', 'en_cours', 'terminee', 'annulee')),
    date_signature_etudiant DATE,
    date_signature_entreprise DATE,
    date_signature_ecole DATE,
    documents_paths TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (offre_stage_id) REFERENCES offres_stage(id),
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id),
    FOREIGN KEY (tuteur_ecole_id) REFERENCES users(id)
);

-- Table des évaluations de stage
CREATE TABLE IF NOT EXISTS evaluations_stage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    convention_id INTEGER NOT NULL,
    type_evaluation VARCHAR(20) CHECK(type_evaluation IN ('mi_parcours', 'fin_stage', 'entreprise', 'ecole')),
    note_globale DECIMAL(4,2),
    commentaires TEXT,
    points_forts TEXT,
    points_amelioration TEXT,
    evalue_par INTEGER,
    date_evaluation DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (convention_id) REFERENCES conventions_stage(id),
    FOREIGN KEY (evalue_par) REFERENCES users(id)
);

-- ========== MODULE ÉVÉNEMENTS ==========

-- Table des événements
CREATE TABLE IF NOT EXISTS evenements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_evenement VARCHAR(50) CHECK(type_evenement IN ('conference', 'seminaire', 'competition', 'sortie', 'ceremonie', 'autre')),
    date_debut DATE NOT NULL,
    date_fin DATE,
    heure_debut TIME,
    heure_fin TIME,
    lieu VARCHAR(200),
    organisateur_id INTEGER,
    nombre_places INTEGER,
    cout_participation DECIMAL(10,2),
    is_public BOOLEAN DEFAULT 1,
    statut VARCHAR(20) DEFAULT 'planifie' CHECK(statut IN ('planifie', 'en_cours', 'termine', 'annule')),
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organisateur_id) REFERENCES users(id)
);

-- Table des inscriptions aux événements
CREATE TABLE IF NOT EXISTS inscriptions_evenements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evenement_id INTEGER NOT NULL,
    participant_id INTEGER NOT NULL,
    date_inscription DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'confirmee' CHECK(statut IN ('confirmee', 'annulee', 'present', 'absent')),
    notes TEXT,
    FOREIGN KEY (evenement_id) REFERENCES evenements(id),
    FOREIGN KEY (participant_id) REFERENCES users(id)
);

-- Table des clubs et associations
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    type_club VARCHAR(50) CHECK(type_club IN ('sportif', 'culturel', 'academique', 'humanitaire', 'autre')),
    responsable_id INTEGER,
    nombre_membres INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsable_id) REFERENCES users(id)
);

-- Table des adhésions aux clubs
CREATE TABLE IF NOT EXISTS adhesions_clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    membre_id INTEGER NOT NULL,
    role VARCHAR(20) DEFAULT 'membre' CHECK(role IN ('membre', 'secretaire', 'tresorier', 'vice_president', 'president')),
    date_adhesion DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'active' CHECK(statut IN ('active', 'suspendue', 'resiliee')),
    FOREIGN KEY (club_id) REFERENCES clubs(id),
    FOREIGN KEY (membre_id) REFERENCES users(id)
);

-- ========== MODULE DIPLÔMES ==========

-- Table des diplômes délivrés
CREATE TABLE IF NOT EXISTS diplomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_diplome VARCHAR(50) CHECK(type_diplome IN ('licence', 'master', 'doctorat', 'certificat', 'attestation')),
    specialite VARCHAR(100),
    mention VARCHAR(20) CHECK(mention IN ('passable', 'assez_bien', 'bien', 'tres_bien', 'excellent')),
    moyenne_obtenue DECIMAL(4,2),
    date_obtention DATE NOT NULL,
    numero_diplome VARCHAR(50) UNIQUE,
    numero_registre VARCHAR(50),
    statut VARCHAR(20) DEFAULT 'delivre' CHECK(statut IN ('delivre', 'en_attente', 'annule')),
    delivre_par INTEGER,
    date_delivrance DATE DEFAULT CURRENT_DATE,
    documents_paths TEXT, -- JSON array
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (delivre_par) REFERENCES users(id)
);

-- Table des certifications
CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    organisme_delivrant VARCHAR(100),
    duree_validite_mois INTEGER,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des certifications obtenues
CREATE TABLE IF NOT EXISTS certifications_obtenues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER,
    personnel_id INTEGER,
    certification_id INTEGER NOT NULL,
    date_obtention DATE NOT NULL,
    date_expiration DATE,
    numero_certificat VARCHAR(50),
    statut VARCHAR(20) DEFAULT 'valide' CHECK(statut IN ('valide', 'expire', 'revoke')),
    documents_paths TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (personnel_id) REFERENCES users(id),
    FOREIGN KEY (certification_id) REFERENCES certifications(id)
);

-- ========== MODULE ALUMNI ==========

-- Table des anciens étudiants
CREATE TABLE IF NOT EXISTS alumni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    annee_sortie INTEGER NOT NULL,
    diplome_obtenu VARCHAR(100),
    profession_actuelle VARCHAR(100),
    entreprise_actuelle VARCHAR(200),
    poste_actuel VARCHAR(100),
    email_professionnel VARCHAR(100),
    telephone_professionnel VARCHAR(20),
    adresse_professionnelle TEXT,
    pays VARCHAR(50),
    ville VARCHAR(100),
    reseaux_sociaux TEXT, -- JSON
    is_actif BOOLEAN DEFAULT 1,
    consentement_contact BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
);

-- Table des dons alumni
CREATE TABLE IF NOT EXISTS dons_alumni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumni_id INTEGER NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    date_don DATE DEFAULT CURRENT_DATE,
    type_don VARCHAR(20) CHECK(type_don IN ('unique', 'recurrent', 'legs')),
    frequence VARCHAR(20),
    mode_paiement VARCHAR(20),
    statut VARCHAR(20) DEFAULT 'recu' CHECK(statut IN ('recu', 'en_attente', 'annule')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumni_id) REFERENCES alumni(id)
);

-- ========== MODULE RECHERCHE ==========

-- Table des projets de recherche
CREATE TABLE IF NOT EXISTS projets_recherche (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    responsable_id INTEGER NOT NULL,
    laboratoire VARCHAR(100),
    date_debut DATE,
    date_fin DATE,
    budget_total DECIMAL(10,2),
    statut VARCHAR(20) DEFAULT 'en_cours' CHECK(statut IN ('planifie', 'en_cours', 'suspendu', 'termine', 'annule')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsable_id) REFERENCES users(id)
);

-- Table des publications
CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(200) NOT NULL,
    type_publication VARCHAR(50) CHECK(type_publication IN ('article', 'livre', 'chapitre', 'communication', 'poster', 'autre')),
    auteurs TEXT NOT NULL, -- JSON array
    revue_editeur VARCHAR(200),
    annee_publication INTEGER,
    isbn_issn VARCHAR(50),
    doi VARCHAR(100),
    url VARCHAR(255),
    resume TEXT,
    mots_cles TEXT,
    statut VARCHAR(20) DEFAULT 'soumis' CHECK(statut IN ('soumis', 'accepte', 'publie', 'rejete')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== MODULE LOGISTIQUE ==========

-- Table des transports
CREATE TABLE IF NOT EXISTS transports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_transport VARCHAR(20) CHECK(type_transport IN ('bus', 'minibus', 'autre')),
    numero_immatriculation VARCHAR(50) UNIQUE,
    capacite INTEGER,
    chauffeur VARCHAR(100),
    itineraire TEXT,
    horaires TEXT, -- JSON
    cout_mensuel DECIMAL(10,2),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des inscriptions transport
CREATE TABLE IF NOT EXISTS inscriptions_transport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    transport_id INTEGER NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'active' CHECK(statut IN ('active', 'suspendue', 'terminee')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (transport_id) REFERENCES transports(id)
);

-- Table de la restauration
CREATE TABLE IF NOT EXISTS menus_restauration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_menu DATE NOT NULL,
    type_repas VARCHAR(20) CHECK(type_repas IN ('petit_dejeuner', 'dejeuner', 'diner')),
    plat_principal VARCHAR(200),
    accompagnement VARCHAR(200),
    dessert VARCHAR(200),
    prix DECIMAL(10,2),
    nombre_portions INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des réservations restauration
CREATE TABLE IF NOT EXISTS reservations_restauration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    utilisateur_id INTEGER NOT NULL,
    date_reservation DATE NOT NULL,
    nombre_portions INTEGER DEFAULT 1,
    statut VARCHAR(20) DEFAULT 'reservee' CHECK(statut IN ('reservee', 'consomee', 'annulee')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus_restauration(id),
    FOREIGN KEY (utilisateur_id) REFERENCES users(id)
);

-- Table de l'internat
CREATE TABLE IF NOT EXISTS chambres_internat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_chambre VARCHAR(20) UNIQUE NOT NULL,
    batiment VARCHAR(50),
    etage INTEGER,
    capacite INTEGER DEFAULT 2,
    type_chambre VARCHAR(20) CHECK(type_chambre IN ('simple', 'double', 'triple', 'quatre')),
    cout_mensuel DECIMAL(10,2),
    equipements TEXT, -- JSON array
    is_disponible BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des inscriptions internat
CREATE TABLE IF NOT EXISTS inscriptions_internat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    chambre_id INTEGER NOT NULL,
    date_entree DATE NOT NULL,
    date_sortie DATE,
    statut VARCHAR(20) DEFAULT 'active' CHECK(statut IN ('active', 'terminee', 'resiliee')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (chambre_id) REFERENCES chambres_internat(id)
);

-- ========== MODULE DISCIPLINE ==========

-- Table des sanctions
CREATE TABLE IF NOT EXISTS sanctions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_sanction VARCHAR(50) CHECK(type_sanction IN ('avertissement', 'blame', 'exclusion_temporaire', 'exclusion_definitive', 'autre')),
    motif TEXT NOT NULL,
    date_sanction DATE DEFAULT CURRENT_DATE,
    duree_jours INTEGER, -- Pour exclusions temporaires
    sanctionne_par INTEGER NOT NULL,
    statut VARCHAR(20) DEFAULT 'active' CHECK(statut IN ('active', 'levee', 'annulee')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (sanctionne_par) REFERENCES users(id)
);

-- Table des récompenses
CREATE TABLE IF NOT EXISTS recompenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER,
    personnel_id INTEGER,
    type_recompense VARCHAR(50) CHECK(type_recompense IN ('felicitation', 'medaille', 'trophee', 'bourse_merite', 'autre')),
    motif TEXT NOT NULL,
    date_recompense DATE DEFAULT CURRENT_DATE,
    montant DECIMAL(10,2), -- Pour bourses de mérite
    remise_par INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (personnel_id) REFERENCES users(id),
    FOREIGN KEY (remise_par) REFERENCES users(id)
);

-- ========== MODULE SANTÉ ==========

-- Table des dossiers médicaux
CREATE TABLE IF NOT EXISTS dossiers_medicaux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER,
    personnel_id INTEGER,
    groupe_sanguin VARCHAR(10),
    allergies TEXT,
    maladies_chroniques TEXT,
    medicaments_habituels TEXT,
    contact_urgence_nom VARCHAR(100),
    contact_urgence_telephone VARCHAR(20),
    notes_medicales TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (personnel_id) REFERENCES users(id)
);

-- Table des visites médicales
CREATE TABLE IF NOT EXISTS visites_medicales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dossier_medical_id INTEGER NOT NULL,
    date_visite DATE NOT NULL,
    type_visite VARCHAR(50) CHECK(type_visite IN ('entree', 'annuelle', 'urgence', 'vaccination', 'autre')),
    medecin VARCHAR(100),
    diagnostic TEXT,
    prescriptions TEXT,
    prochaine_visite DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dossier_medical_id) REFERENCES dossiers_medicaux(id)
);

-- ========== MODULE RATTRAPAGES ==========

-- Table des sessions de rattrapage
CREATE TABLE IF NOT EXISTS sessions_rattrapage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    annee_academique_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (annee_academique_id) REFERENCES annees_academiques(id)
);

-- Table des inscriptions au rattrapage
CREATE TABLE IF NOT EXISTS inscriptions_rattrapage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    matiere_id INTEGER NOT NULL,
    date_examen DATE,
    heure_examen TIME,
    salle_id INTEGER,
    note_obtenue DECIMAL(4,2),
    statut VARCHAR(20) DEFAULT 'inscrit' CHECK(statut IN ('inscrit', 'present', 'absent', 'admis', 'ajourne')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions_rattrapage(id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (matiere_id) REFERENCES matieres(id),
    FOREIGN KEY (salle_id) REFERENCES salles(id)
);

-- Index supplémentaires pour performance
CREATE INDEX IF NOT EXISTS idx_candidatures_statut ON candidatures(statut);
CREATE INDEX IF NOT EXISTS idx_bourses_etudiant ON bourses(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_emprunts_emprunteur ON emprunts(emprunteur_id);
CREATE INDEX IF NOT EXISTS idx_conventions_etudiant ON conventions_stage(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_evenements_date ON evenements(date_debut);
CREATE INDEX IF NOT EXISTS idx_diplomes_etudiant ON diplomes(etudiant_id);

