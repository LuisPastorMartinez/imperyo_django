# utils/cargar_tejidos.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.firestore_utils import get_firestore_client

db = get_firestore_client()

TEJIDOS = [
    "Malaga",
    "Verona",
    "Wembley",
    "Sin Definir",
    "Lenox",
    "Fly",
    "Flow",
    "edwin-Lenox",
    "edwin",
    "Lima",
    "Edwin-Verona",
    "Lima-Verona",
    "Lima-Lenox",
    "Thiago",
    "Thiago-Lenox",
    "Thiago-Verona",
    "Verano",
    "Invierno"
]

def cargar_tejidos_en_firestore():
    for nombre in TEJIDOS:
        doc_id = (
            nombre.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "")
            .replace("á", "a").replace("é", "e").replace("í", "i")
            .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        )
        db.collection("tejidos").document(doc_id).set({
            "nombre": nombre,
            "activo": True
        })
    print(f"✅ {len(TEJIDOS)} tejidos cargados en Firestore.")

if __name__ == "__main__":
    cargar_tejidos_en_firestore()