from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils.firestore_utils import get_firestore_client
from datetime import date, datetime
from django.contrib import messages
import json  # 👈 Añadido aquí al inicio


# ======================================================
# LISTADO
# ======================================================
@login_required
def pedidos_home(request):
    db = get_firestore_client()
    pedidos_ref = db.collection("pedidos")
    docs = pedidos_ref.stream()

    # Mapeo de estados a iconos
    ICONOS_ESTADOS = {
        "Nuevo": "🟢",
        "diseño": "🎨",
        "fabricacion": "🧵",
        "trabajo iniciado": "🚧",
        "trabajo terminado": "✅",
        "cobrado": "💰",
        "retirado": "🚚",
        "pendiente": "⏳"
    }

    pedidos = []
    for doc in docs:
        data = doc.to_dict()
        data["ID"] = doc.id
        
        # Generar iconos para los estados
        estados = data.get("Estados", [])
        iconos_html = ""
        for estado in estados:
            icono = ICONOS_ESTADOS.get(estado, "❓")
            iconos_html += f'<span title="{estado}" style="margin-right: 6px; font-size: 1.2em;">{icono}</span>'
        
        data["Estados_iconos"] = iconos_html
        pedidos.append(data)

    # 🔻 Orden descendente: del más alto al más bajo (5, 4, 3...)
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
    except Exception as e:
        print(f"Error al cargar productos: {e}")
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
    except Exception as e:
        print(f"Error al cargar tejidos: {e}")
        tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]

    # === OBTENER NUEVO ID ===
    pedidos_ref = db.collection("pedidos").stream()
    ids = [int(doc.id) for doc in pedidos_ref]
    nuevo_id = max(ids) + 1 if ids else 1

    # === MANEJO DE POST ===
    if request.method == "POST":
        productos = []
        index = 0

        while True:
            nombre_key = f"producto_nombre_{index}"
            if nombre_key not in request.POST:
                break

            nombre = request.POST.get(f"producto_nombre_{index}", "").strip()
            tejido = request.POST.get(f"producto_tejido_{index}", "").strip()
            cantidad_raw = request.POST.get(f"producto_cantidad_{index}", "").strip()
            precio_raw = request.POST.get(f"producto_precio_{index}", "").strip()

            # Si todos están vacíos, saltar
            if not nombre and not tejido and not cantidad_raw and not precio_raw:
                index += 1
                continue

            try:
                cantidad = float(cantidad_raw) if cantidad_raw else 0
            except ValueError:
                cantidad = 0

            try:
                precio_unitario = float(precio_raw) if precio_raw else 0
            except ValueError:
                precio_unitario = 0

            if nombre or tejido or cantidad > 0 or precio_unitario > 0:
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
        except ValueError:
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

    estados = ["Nuevo", "diseño", "fabricacion", "trabajo iniciado", "pendiente", "cobrado",                              "retirado", "trabajo terminado"]

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
    except Exception as e:
        print(f"Error al cargar productos: {e}")
        productos_disponibles = ["Camiseta", "Maillot", "Culote"]

    # === CARGAR TEJIDOS ===
    tejidos_disponibles = []
    try:
        tejidos_ref = db.collection("tejidos").where("activo", "==", True).stream()
        for doc_tejido in tejidos_ref:
            data = doc_tejido.to_dict()
            if data.get("nombre"):
                tejidos_disponibles.append(data["nombre"])
        if not tejidos_disponibles:
            tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]
    except Exception as e:
        print(f"Error al cargar tejidos: {e}")
        tejidos_disponibles = ["Sin Definir", "Malaga", "Verona"]

    if request.method == "POST":
        productos = []
        index = 0

        while True:
            nombre_key = f"producto_nombre_{index}"
            if nombre_key not in request.POST:
                break

            nombre = request.POST.get(f"producto_nombre_{index}", "").strip()
            tejido = request.POST.get(f"producto_tejido_{index}", "").strip()
            cantidad_raw = request.POST.get(f"producto_cantidad_{index}", "").strip()
            precio_raw = request.POST.get(f"producto_precio_{index}", "").strip()

            if not nombre and not tejido and not cantidad_raw and not precio_raw:
                index += 1
                continue

            try:
                cantidad = float(cantidad_raw) if cantidad_raw else 0
            except ValueError:
                cantidad = 0

            try:
                precio_unitario = float(precio_raw) if precio_raw else 0
            except ValueError:
                precio_unitario = 0

            if nombre or tejido or cantidad > 0 or precio_unitario > 0:
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
        except ValueError:
            pago_adelantado = 0.0

        # 🔹 NUEVO: Lógica para Fecha_finalizacion (solo la primera vez)
        estados = request.POST.getlist("Estados")
        estados_set = set(estados)
        tres_estados = {"trabajo terminado", "retirado", "cobrado"}
        fecha_finalizacion = pedido.get("Fecha_finalizacion")  # conservar si ya existe
        if fecha_finalizacion is None and tres_estados.issubset(estados_set):
            fecha_finalizacion = date.today().isoformat()
        # Si ya existe, no se modifica

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

    estados = ["Nuevo", "diseño", "fabricacion", "trabajo iniciado", "pendiente", "cobrado", "retirado", "trabajo terminado"]

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
        # Paso 1: Obtener todos los pedidos EXCEPTO el que se va a eliminar
        all_docs = db.collection("pedidos").stream()
        pedidos = []
        for d in all_docs:
            if d.id != str(pedido_id):
                pedidos.append((int(d.id), d.to_dict()))
        
        # Ordenar por ID original
        pedidos.sort(key=lambda x: x[0])
        
        # Paso 2: Eliminar TODOS los pedidos
        batch = db.batch()
        all_refs = db.collection("pedidos").list_documents()
        for doc_ref in all_refs:
            batch.delete(doc_ref)
        batch.commit()
        
        # Paso 3: Volver a crear con IDs consecutivos
        if pedidos:
            batch = db.batch()
            for nuevo_id, datos in enumerate(pedidos, start=1):
                new_ref = db.collection("pedidos").document(str(nuevo_id))
                batch.set(new_ref, datos[1])
            batch.commit()
        
        return redirect("/pedidos/")

    pedido = doc.to_dict()
    return render(request, "pedidos/eliminar.html", {
        "pedido_id": pedido_id,
        "pedido": pedido,
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
    pedidos_ref = db.collection("pedidos")
    docs = pedidos_ref.stream()

    ICONOS_ESTADOS = {
        "Nuevo": "🟢",
        "diseño": "🎨",
        "fabricacion": "🧵",
        "trabajo iniciado": "🚧",
        "trabajo terminado": "✅",
        "cobrado": "💰",
        "retirado": "🚚",
        "pendiente": "⏳"
    }

    pedidos = []
    for doc in docs:
        data = doc.to_dict()
        data["ID"] = doc.id
        
        estados = data.get("Estados", [])
        iconos_html = ""
        for estado in estados:
            icono = ICONOS_ESTADOS.get(estado, "❓")
            iconos_html += f'<span title="{estado}" style="margin-right: 6px; font-size: 1.2em;">{icono}</span>'
        
        data["Estados_iconos"] = iconos_html
        # 👇 AÑADIDO: Estados en formato JSON para el filtro
        data["Estados_json"] = json.dumps(estados)
        pedidos.append(data)

    # 🔻 Orden descendente: del más alto al más bajo (5, 4, 3...)
    pedidos = sorted(pedidos, key=lambda x: int(x["ID"]), reverse=True)

    # 👇 AÑADIDO: lista de todos los estados para el filtro
    estados_todos = ["Nuevo", "diseño", "fabricacion", "trabajo iniciado", "trabajo terminado", "cobrado", "retirado", "pendiente"]

    return render(request, "pedidos/resumen.html", {
        "pedidos": pedidos,
        "estados_todos": estados_todos
    })


# ======================================================
# CONFIGURACIÓN
# ======================================================
@login_required
def configuracion(request):
    db = get_firestore_client()

    if request.method == "POST":
        if request.POST.get("accion") == "backup":
            # --- EXPORTAR ---
            docs = db.collection("pedidos").stream()
            backup_data = {}
            for doc in docs:
                data = doc.to_dict()
                for k, v in data.items():
                    if isinstance(v, (date,)):
                        data[k] = v.isoformat()
                backup_data[doc.id] = data

            filename = f"backup_pedidos_{date.today().strftime('%Y%m%d_%H%M')}.json"
            response = HttpResponse(
                json.dumps(backup_data, indent=2, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        elif request.POST.get("accion") == "restore_preview":
            # --- VISTA PREVIA DE RESTAURACIÓN ---
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

            except (json.JSONDecodeError, UnicodeDecodeError):
                from django.contrib import messages
                messages.error(request, "❌ El archivo no es un JSON válido.")
                return redirect("configuracion")
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"❌ Error al leer el archivo: {str(e)}")
                return redirect("configuracion")

        elif request.POST.get("accion") == "restore_confirm":
            # --- EJECUTAR RESTAURACIÓN ---
            backup_data = request.session.get("backup_data")
            if not backup_data:
                from django.contrib import messages
                messages.error(request, "⚠️ No hay datos de backup pendientes. Sube un archivo primero.")
                return redirect("configuracion")

            try:
                # 1. Eliminar todos los pedidos actuales
                batch = db.batch()
                all_refs = db.collection("pedidos").list_documents()
                for doc_ref in all_refs:
                    batch.delete(doc_ref)
                batch.commit()

                # 2. Restaurar desde el backup
                if backup_data:
                    batch = db.batch()
                    for doc_id, data in backup_data.items():
                        new_ref = db.collection("pedidos").document(str(doc_id))
                        batch.set(new_ref, data)
                    batch.commit()

                # Limpiar sesión
                request.session.pop("backup_data", None)
                request.session.pop("backup_filename", None)

                from django.contrib import messages
                messages.success(request, f"✅ ¡Backup restaurado con éxito! Se han cargado {len(backup_data)} pedidos.")
                return redirect("configuracion")

            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"❌ Error al restaurar: {str(e)}")
                return redirect("configuracion")

    return render(request, "pedidos/configuracion.html")
# ======================================================
# AGENDA
# ======================================================
@login_required
def agenda(request):
    try:
        db = get_firestore_client()
        citas_ref = db.collection("citas")
        docs = citas_ref.stream()
        
        citas = []
        citas_hoy = 0
        hoy = date.today().isoformat()
        
        for doc in docs:
            data = doc.to_dict()
            data["ID"] = doc.id
            citas.append(data)
            
            # Contar citas de hoy
            if data.get("Fecha") == hoy:
                citas_hoy += 1
        
        # Ordenar por fecha y hora (más cercanas primero)
        citas = sorted(citas, key=lambda x: (x.get("Fecha", ""), x.get("Hora", "")))
    except Exception as e:
        # Si hay error (colección no existe), mostrar lista vacía
        citas = []
        citas_hoy = 0
        print(f"Error al cargar citas: {e}")
    
    return render(request, "pedidos/agenda.html", {
        "citas": citas,
        "citas_hoy_count": citas_hoy  # 👈 Añadido contador
    })

@login_required
def agenda_guardar(request):
    if request.method == 'POST':
        db = get_firestore_client()
        
        cita_id = request.POST.get('cita_id', '').strip()
        fecha = request.POST.get('Fecha', '').strip()
        hora = request.POST.get('Hora', '').strip()
        cliente = request.POST.get('Cliente', '').strip()
        telefono = request.POST.get('Telefono', '').strip()
        tipo = request.POST.get('Tipo', '').strip()
        club = request.POST.get('Club', '').strip()
        notas = request.POST.get('Notas', '').strip()
        
        # Validar campos obligatorios
        if not fecha or not hora or not cliente or not telefono or not tipo:
            messages.error(request, "Por favor, completa todos los campos obligatorios.")
            return redirect('agenda')
        
        # Crear datos de la cita
        data = {
            "Fecha": fecha,
            "Hora": hora,
            "Cliente": cliente,
            "Telefono": telefono,
            "Tipo": tipo,
            "Club": club,
            "Notas": notas,
            "Fecha_creacion": datetime.now().isoformat()
        }
        
        try:
            if cita_id:
                # Actualizar cita existente
                cita_ref = db.collection("citas").document(cita_id)
                cita_ref.update(data)
                messages.success(request, "✅ Cita actualizada correctamente.")
            else:
                # Crear nueva cita
                db.collection("citas").add(data)
                messages.success(request, "✅ Cita creada correctamente.")
        except Exception as e:
            messages.error(request, f"❌ Error al guardar la cita: {str(e)}")
        
        return redirect('agenda')
    
    return redirect('agenda')


@login_required
def agenda_eliminar(request, cita_id):
    if request.method == 'GET':
        db = get_firestore_client()
        
        try:
            # Eliminar cita
            db.collection("citas").document(cita_id).delete()
            messages.success(request, "✅ Cita eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"❌ Error al eliminar la cita: {str(e)}")
        
        return redirect('agenda')
    
    return redirect('agenda')
============================================
🔹 TAREAS (PÁGINA INDEPENDIENTE)
============================================
@login_required
def tareas(request):
    """Página principal de tareas"""
    return render(request, "pedidos/tareas.html")

@login_required
def tareas_listar(request):
    """Listar todas las tareas (pendientes y completadas)"""
    try:
        db = get_firestore_client()
        tareas_ref = db.collection("tareas").order_by("fecha_creacion", direction=firestore.Query.DESCENDING)
        docs = tareas_ref.stream()
        
        tareas = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            tareas.append(data)
        
        return JsonResponse({"tareas": tareas}, safe=False)
    
    except Exception as e:
        print(f"Error al listar tareas: {e}")
        return JsonResponse({"tareas": []}, safe=False)

@login_required
def tareas_guardar(request):
    """Crear nueva tarea"""
    if request.method == 'POST':
        try:
            db = get_firestore_client()
            
            cliente_club = request.POST.get('cliente_club', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            
            if not cliente_club or not descripcion:
                return JsonResponse({"error": "Cliente/Club y descripción son obligatorios"}, status=400)
            
            data = {
                "cliente_club": cliente_club,
                "descripcion": descripcion,
                "completada": False,
                "fecha_creacion": datetime.now().isoformat(),
                "usuario": request.user.username
            }
            
            # Crear nueva tarea
            db.collection("tareas").add(data)
            
            return JsonResponse({"success": True, "message": "Tarea creada correctamente"})
        
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

@login_required
def tareas_completar(request, tarea_id):
    """Marcar tarea como completada"""
    if request.method == 'POST':
        try:
            db = get_firestore_client()
            
            tarea_ref = db.collection("tareas").document(tarea_id)
            doc = tarea_ref.get()
            
            if not doc.exists:
                return JsonResponse({"error": "Tarea no encontrada"}, status=404)
            
            # Marcar como completada
            tarea_ref.update({
                "completada": True,
                "fecha_completada": datetime.now().isoformat()
            })
            
            return JsonResponse({"success": True, "message": "Tarea completada"})
        
        except Exception as e:
            print(f"Error al completar tarea: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

@login_required
def tareas_eliminar(request, tarea_id):
    """Eliminar tarea"""
    if request.method == 'POST':
        try:
            db = get_firestore_client()
            
            # Eliminar tarea
            db.collection("tareas").document(tarea_id).delete()
            
            return JsonResponse({"success": True, "message": "Tarea eliminada"})
        
        except Exception as e:
            print(f"Error al eliminar tarea: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)