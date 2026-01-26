from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils.firestore_utils import get_firestore_client
from datetime import date
import json


# ======================================================
# LISTADO
# ======================================================
@login_required
def pedidos_home(request):
    db = get_firestore_client()
    pedidos_ref = db.collection("pedidos")
    docs = pedidos_ref.stream()

    ICONOS_ESTADOS = {
        "Nuevo": "🟢",
        "diseño": "🎨",
        "fabricacion": "🧵",
        "trabajo empezado": "⚙️",
        "trabajo terminado": "✅",
        "cobrado": "💰",
        "retirado": "🚚",
        "pendiente": "⏳",
    }

    pedidos = []
    for doc in docs:
        data = doc.to_dict()
        data["ID"] = doc.id

        iconos_html = ""
        for estado in data.get("Estados", []):
            icono = ICONOS_ESTADOS.get(estado, "❓")
            iconos_html += f'<span title="{estado}" style="margin-right: 6px; font-size: 1.2em;">{icono}</span>'

        data["Estados_iconos"] = iconos_html
        pedidos.append(data)

    pedidos = sorted(pedidos, key=lambda x: int(x["ID"]), reverse=True)

    return render(request, "pedidos/home.html", {"pedidos": pedidos})


# ======================================================
# CREAR
# ======================================================
@login_required
def pedido_crear(request):
    db = get_firestore_client()

    # === CARGAR PRODUCTOS ===
    productos_disponibles = []
    try:
        productos_ref = db.collection("productos").where("activo", "==", True).stream()
        for doc in productos_ref:
            data = doc.to_dict()
            if data.get("nombre"):
                productos_disponibles.append(data["nombre"])
        if not productos_disponibles:
            productos_disponibles = ["Camiseta", "Maillot", "Culote"]
    except Exception:
        productos_disponibles = ["Camiseta", "Maillot", "Culote"]

    # === CARGAR TEJIDOS ===
    tejidos_disponibles = []
    try:
        tejidos_ref = db.collection("tejidos").where("activo", "==", True).stream()
        for doc in tejidos_ref:
            data = doc.to_dict()
            if data.get("nombre"):
                tejidos_disponibles.append(data["nombre"])
        if not tejidos_disponibles:
            tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]
    except Exception:
        tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]

    # === OBTENER ID ===
    pedidos_ref = db.collection("pedidos").stream()
    ids = [int(doc.id) for doc in pedidos_ref]
    nuevo_id = max(ids) + 1 if ids else 1

    if request.method == "POST":
        productos = []
        index = 0

        while True:
            if f"producto_nombre_{index}" not in request.POST:
                break

            nombre = request.POST.get(f"producto_nombre_{index}", "").strip()
            tejido = request.POST.get(f"producto_tejido_{index}", "").strip()
            cantidad_raw = request.POST.get(f"producto_cantidad_{index}", "").strip()
            precio_raw = request.POST.get(f"producto_precio_{index}", "").strip()

            if nombre or tejido or cantidad_raw or precio_raw:
                try:
                    cantidad = float(cantidad_raw) if cantidad_raw else 0
                except:
                    cantidad = 0

                try:
                    precio_unitario = float(precio_raw) if precio_raw else 0
                except:
                    precio_unitario = 0

                productos.append({
                    "Producto": nombre,
                    "tejido": tejido,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": round(cantidad * precio_unitario, 2),
                })

            index += 1

        total_pedido = sum(p["subtotal"] for p in productos)

        pago_adelantado_raw = request.POST.get("Pago_adelantado", "").strip()
        try:
            pago_adelantado = float(pago_adelantado_raw) if pago_adelantado_raw else 0.0
        except:
            pago_adelantado = 0.0

        db.collection("pedidos").document(str(nuevo_id)).set({
            "Cliente": request.POST.get("Cliente", "").strip(),
            "Telefono": request.POST.get("Telefono", "").strip(),
            "Club": request.POST.get("Club", "").strip(),
            "Fecha_entrega_estimada": request.POST.get("Fecha_entrega_estimada", "").strip(),
            "Fecha_entrada": request.POST.get("Fecha_entrada", "").strip(),
            "Comentarios": request.POST.get("Comentarios", "").strip(),
            "Estados": request.POST.getlist("Estados"),
            "Precio": request.POST.get("Precio", "").strip(),
            "Precio_factura": request.POST.get("Precio_factura", "").strip(),
            "Forma_pago": request.POST.get("Forma_pago", "").strip(),
            "Pago_adelantado": pago_adelantado,
            "DestinoTotal": request.POST.get("DestinoTotal", "").strip(),
            "productos": productos,
            "total_pedido": total_pedido,
        })

        return redirect("/pedidos/")

    # ⭐ CORREGIDO: ESTADOS (lista limpia y bien indentada)
    estados = [
        "Nuevo",
        "diseño",
        "fabricacion",
        "trabajo empezado",
        "pendiente",
        "cobrado",
        "retirado",
        "trabajo terminado",
    ]

    return render(request, "pedidos/crear.html", {
        "pedido_id": nuevo_id,
        "estados": estados,
        "productos_disponibles": sorted(productos_disponibles),
        "tejidos_disponibles": sorted(tejidos_disponibles),
        "fecha_hoy": date.today().isoformat(),
    })


# ======================================================
# EDITAR
# ======================================================
@login_required
def pedido_editar(request, pedido_id):
    db = get_firestore_client()

    ref = db.collection("pedidos").document(str(pedido_id))
    doc = ref.get()

    if not doc.exists:
        return HttpResponse("Pedido no encontrado", status=404)

    pedido = doc.to_dict()

    # === CARGAR PRODUCTOS ===
    productos_disponibles = []
    try:
        productos_ref = db.collection("productos").where("activo", "==", True).stream()
        for doc_prod in productos_ref:
            data = doc_prod.to_dict()
            if data.get("nombre"):
                productos_disponibles.append(data["nombre"])
        if not productos_disponibles:
            productos_disponibles = ["Camiseta", "Maillot", "Culote"]
    except:
        productos_disponibles = ["Camiseta", "Maillot", "Culote"]

    # === CARGAR TEJIDOS ===
    tejidos_disponibles = []
    try:
        tejidos_ref = db.collection("tejidos").where("activo", "==", True).stream()
        for doc_tej in tejidos_ref:
            data = doc_tej.to_dict()
            if data.get("nombre"):
                tejidos_disponibles.append(data["nombre"])
        if not tejidos_disponibles:
            tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]
    except:
        tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]

    if request.method == "POST":
        productos = []
        index = 0

        while True:
            if f"producto_nombre_{index}" not in request.POST:
                break

            nombre = request.POST.get(f"producto_nombre_{index}", "").strip()
            tejido = request.POST.get(f"producto_tejido_{index}", "").strip()
            cantidad_raw = request.POST.get(f"producto_cantidad_{index}", "").strip()
            precio_raw = request.POST.get(f"producto_precio_{index}", "").strip()

            if nombre or tejido or cantidad_raw or precio_raw:
                try:
                    cantidad = float(cantidad_raw) if cantidad_raw else 0
                except:
                    cantidad = 0

                try:
                    precio_unitario = float(precio_raw) if precio_raw else 0
                except:
                    precio_unitario = 0

                productos.append({
                    "Producto": nombre,
                    "tejido": tejido,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": round(cantidad * precio_unitario, 2),
                })

            index += 1

        total_pedido = sum(p["subtotal"] for p in productos)

        pago_adelantado_raw = request.POST.get("Pago_adelantado", "").strip()
        try:
            pago_adelantado = float(pago_adelantado_raw) if pago_adelantado_raw else 0.0
        except:
            pago_adelantado = 0.0

        estados = request.POST.getlist("Estados")
        estados_set = set(estados)

        tres_estados = {"trabajo terminado", "retirado", "cobrado"}
        fecha_finalizacion = pedido.get("Fecha_finalizacion")

        if fecha_finalizacion is None and tres_estados.issubset(estados_set):
            fecha_finalizacion = date.today().isoformat()

        ref.update({
            "Cliente": request.POST.get("Cliente", "").strip(),
            "Telefono": request.POST.get("Telefono", "").strip(),
            "Club": request.POST.get("Club", "").strip(),
            "Fecha_entrega_estimada": request.POST.get("Fecha_entrega_estimada", "").strip(),
            "Fecha_entrada": request.POST.get("Fecha_entrada", "").strip(),
            "Comentarios": request.POST.get("Comentarios", "").strip(),
            "Estados": estados,
            "Precio": request.POST.get("Precio", "").strip(),
            "Precio_factura": request.POST.get("Precio_factura", "").strip(),
            "Forma_pago": request.POST.get("Forma_pago", "").strip(),
            "Pago_adelantado": pago_adelantado,
            "DestinoTotal": request.POST.get("DestinoTotal", "").strip(),
            "productos": productos,
            "total_pedido": total_pedido,
            "Fecha_finalizacion": fecha_finalizacion,
        })

        return redirect("/pedidos/")

    # ⭐ CORREGIDO
    estados = [
        "Nuevo",
        "diseño",
        "fabricacion",
        "trabajo empezado",
        "pendiente",
        "cobrado",
        "retirado",
        "trabajo terminado",
    ]

    return render(request, "pedidos/editar.html", {
        "pedido_id": pedido_id,
        "pedido": pedido,
        "productos": pedido.get("productos", []),
        "estados": estados,
        "productos_disponibles": sorted(productos_disponibles),
        "tejidos_disponibles": sorted(tejidos_disponibles),
    })


# ======================================================
# DETALLE
# ======================================================
@login_required
def pedido_detalle(request, pedido_id):
    db = get_firestore_client()
    ref = db.collection("pedidos").document(str(pedido_id))
    doc = ref.get()

    if not doc.exists:
        return HttpResponse("Pedido no encontrado", status=404)

    pedido = doc.to_dict()

    return render(request, "pedidos/detalle.html", {
        "pedido_id": pedido_id,
        "pedido": pedido,
    })


# ======================================================
# ELIMINAR
# ======================================================
@login_required
def pedido_eliminar(request, pedido_id):
    db = get_firestore_client()
    ref = db.collection("pedidos").document(str(pedido_id))
    doc = ref.get()

    if not doc.exists:
        return HttpResponse("Pedido no encontrado", status=404)

    if request.method == "POST":
        all_docs = db.collection("pedidos").stream()
        pedidos = []
        for d in all_docs:
            if d.id != str(pedido_id):
                pedidos.append((int(d.id), d.to_dict()))

        pedidos.sort(key=lambda x: x[0])

        batch = db.batch()
        all_refs = db.collection("pedidos").list_documents()
        for doc_ref in all_refs:
            batch.delete(doc_ref)
        batch.commit()

        if pedidos:
            batch = db.batch()
            for nuevo_id, datos in enumerate(pedidos, start=1):
                new_ref = db.collection("pedidos").document(str(nuevo_id))
                batch.set(new_ref, datos[1])
            batch.commit()

        return redirect("/pedidos/")

    return render(request, "pedidos/eliminar.html", {
        "pedido_id": pedido_id,
        "pedido": doc.to_dict(),
    })


# ======================================================
# POSIBLES CLIENTES
# ======================================================
@login_required
def posibles_clientes(request):
    return render(request, "pedidos/posibles_clientes.html")


# ======================================================
# GASTOS
# ======================================================
@login_required
def gastos(request):
    return render(request, "pedidos/gastos.html")


# ======================================================
# RESUMEN
# ======================================================
@login_required
def resumen(request):
    db = get_firestore_client()
    docs = db.collection("pedidos").stream()

    ICONOS_ESTADOS = {
        "Nuevo": "🟢",
        "diseño": "🎨",
        "fabricacion": "🧵",
        "trabajo empezado": "⚙️",
        "trabajo terminado": "✅",
        "cobrado": "💰",
        "retirado": "🚚",
        "pendiente": "⏳",
    }

    pedidos = []
    for doc in docs:
        data = doc.to_dict()
        data["ID"] = doc.id

        iconos_html = ""
        for estado in data.get("Estados", []):
            icono = ICONOS_ESTADOS.get(estado, "❓")
            iconos_html += f'<span title="{estado}" style="margin-right: 6px; font-size: 1.2em;">{icono}</span>'

        data["Estados_iconos"] = iconos_html
        data["Estados_json"] = json.dumps(data.get("Estados", []))
        pedidos.append(data)

    pedidos = sorted(pedidos, key=lambda x: int(x["ID"]), reverse=True)

    estados_todos = [
        "Nuevo",
        "diseño",
        "fabricacion",
        "trabajo empezado",
        "trabajo terminado",
        "cobrado",
        "retirado",
        "pendiente",
    ]

    return render(request, "pedidos/resumen.html", {
        "pedidos": pedidos,
        "estados_todos": estados_todos,
    })


# ======================================================
# CONFIGURACIÓN
# ======================================================
@login_required
def configuracion(request):
    db = get_firestore_client()

    if request.method == "POST":
        if request.POST.get("accion") == "backup":
            docs = db.collection("pedidos").stream()
            backup_data = {}
            for doc in docs:
                data = doc.to_dict()
                for k, v in data.items():
                    if isinstance(v, date):
                        data[k] = v.isoformat()
                backup_data[doc.id] = data

            filename = f"backup_pedidos_{date.today().strftime('%Y%m%d_%H%M')}.json"
            response = HttpResponse(
                json.dumps(backup_data, indent=2, ensure_ascii=False),
                content_type="application/json; charset=utf-8",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        elif request.POST.get("accion") == "restore_preview":
            archivo = request.FILES.get("backup_file")
            if not archivo:
                from django.contrib import messages
                messages.error(request, "⚠️ No se ha seleccionado ningún archivo.")
                return redirect("configuracion")

            try:
                contenido = json.load(archivo)
                if not isinstance(contenido, dict):
                    raise ValueError("Formato inválido: el archivo debe contener un objeto JSON.")

                ejemplo_id = next(iter(contenido), None)
                if ejemplo_id and not isinstance(contenido[ejemplo_id], dict):
                    raise ValueError("Estructura incorrecta en los datos.")

                request.session["backup_data"] = contenido
                request.session["backup_filename"] = archivo.name

                return render(request, "pedidos/restore_confirm.html", {
                    "num_pedidos": len(contenido),
                    "filename": archivo.name,
                })

            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"❌ Error al leer el archivo: {str(e)}")
                return redirect("configuracion")

        elif request.POST.get("accion") == "restore_confirm":
            backup_data = request.session.get("backup_data")
            if not backup_data:
                from django.contrib import messages
                messages.error(request, "⚠️ No hay datos de backup pendientes.")
                return redirect("configuracion")

            try:
                batch = db.batch()
                all_refs = db.collection("pedidos").list_documents()
                for doc_ref in all_refs:
                    batch.delete(doc_ref)
                batch.commit()

                batch = db.batch()
                for doc_id, data in backup_data.items():
                    ref = db.collection("pedidos").document(str(doc_id))
                    batch.set(ref, data)
                batch.commit()

                request.session.pop("backup_data", None)
                request.session.pop("backup_filename", None)

                from django.contrib import messages
                messages.success(request, "✅ Backup restaurado con éxito.")
                return redirect("configuracion")

            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"❌ Error al restaurar: {str(e)}")
                return redirect("configuracion")

    return render(request, "pedidos/configuracion.html")
