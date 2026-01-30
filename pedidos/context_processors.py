from utils.firestore_utils import get_firestore_client
from datetime import date

def citas_hoy_count(request):
    """Añade el contador de citas hoy a todos los templates"""
    if not request.user.is_authenticated:
        return {}
    
    try:
        db = get_firestore_client()
        citas_ref = db.collection("citas")
        docs = citas_ref.stream()
        
        citas_hoy = 0
        hoy = date.today().isoformat()
        
        for doc in docs:
            data = doc.to_dict()
            if data.get("Fecha") == hoy:
                citas_hoy += 1
        
        return {"citas_hoy_count_global": citas_hoy}
    
    except Exception as e:
        print(f"Error en context processor: {e}")
        return {"citas_hoy_count_global": 0}