# utils/cargar_productos.py
import os
import sys

# Añadir la raíz del proyecto al path para importar settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imperyo.settings')
django.setup()

from utils.firestore_utils import get_firestore_client

db = get_firestore_client()

# Tu lista de productos
PRODUCTOS = [
    "Camiseta Trail",
    "Maillot",
    "Culote",
    "Equipacion Ciclista",
    "Equipacion Running",
    "Calza",
    "Manguitos",
    "Corta Vientos",
    "Calcetines",
    "Guantes",
    "Arreglo",
    "Falda Pantalon",
    "Camiseta Trail Asillas",
    "Camiseta Trail Sin Mangas",
    "Equipacion Ciclista + Running",
    "Camiseta chica Nadadora",
    "Camiseta Externas",
    "Cortavientos externos",
    "Guantes Ext.",
    "Polos Ext.",
    "Gorras Ext.",
    "Top",
    "Chaquetas"
]

def cargar_productos_en_firestore():
    # Opcional: borrar existentes (solo si quieres reemplazar todo)
    # docs = db.collection("productos").stream()
    # for doc in docs:
    #     db.collection("productos").document(doc.id).delete()

    for nombre in PRODUCTOS:
        # Evitar duplicados: usar el nombre como ID (normalizado)
        doc_id = nombre.lower().replace(" ", "_").replace(".", "").replace("+", "plus")
        db.collection("productos").document(doc_id).set({
            "nombre": nombre,
            "activo": True
        })
    print(f"✅ {len(PRODUCTOS)} productos cargados en Firestore.")

if __name__ == "__main__":
    cargar_productos_en_firestore()