"""
Module de gestion de la base de données
"""
import sqlite3
import os
from contextlib import contextmanager
from functools import wraps
from flask import g, current_app

def get_db():
    """Obtient une connexion à la base de données"""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Ferme la connexion à la base de données"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@contextmanager
def get_db_connection():
    """Context manager pour la connexion à la base de données"""
    db = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()

def dict_factory(cursor, row):
    """Convertit les lignes en dictionnaires"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def query_db(query, args=(), one=False):
    """Exécute une requête et retourne les résultats"""
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    results = cursor.fetchall()
    return (dict(row) for row in results) if results else None

def execute_db(query, args=()):
    """Exécute une requête d'insertion/modification"""
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    return cursor.lastrowid


