import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date
import logging
from dotenv import load_dotenv

# 🔥 CARGA EL .env DESDE LA RAÍZ DEL PROYECTO
load_dotenv()

logger = logging.getLogger(__name__)

COLLECTIONS = {
    "pedidos": "pedidos",
    "gastos": "gastos",
    "totales": "totales",
    "listas": "listas",
    "trabajos": "trabajos",
    "posibles_clientes": "posibles_clientes",
}

_firestore_client = None


def read_env(key, required=True, default=None):
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(
            f"❌ ERROR: Falta la variable '{key}' en el archivo .env\n"
            f"Revísala exactamente así: {key}=valor"
        )
    return value


def get_firestore_client():
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    if not firebase_admin._apps:
        cred_json = {
            "type": read_env("FIREBASE_TYPE"),
            "project_id": read_env("FIREBASE_PROJECT_ID"),
            "private_key": read_env("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": read_env("FIREBASE_CLIENT_EMAIL"),
            "token_uri": read_env(
                "FIREBASE_TOKEN_URI",
                required=False,
                default="https://oauth2.googleapis.com/token"
            ),
        }

        cred = credentials.Certificate(cred_json)
        firebase_admin.initialize_app(cred)

    _firestore_client = firestore.client()
    return _firestore_client


def load_dataframes_firestore():
    db = get_firestore_client()
    data = {}

    for key, collection in COLLECTIONS.items():
        rows = []
        for doc in db.collection(collection).stream():
            r = doc.to_dict()
            r["id_documento_firestore"] = doc.id
            rows.append(r)

        data[f"df_{key}"] = pd.DataFrame(rows)

    return data
