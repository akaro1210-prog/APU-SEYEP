"""
calculator.py — Motor matemático de cálculo APU (replica exactamente la lógica del Excel/HTML).
Incluye el cálculo detallado de Dotación / EPP anual y mensual por perfil RRHH.
"""
from state import CATS, get_catalogo_base_dotacion


def fmt_cop(val: float) -> str:
    try:
        num = round(float(val or 0))
        return f"$ {num:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$ 0"


def fmt_pct(val: float) -> str:
    pct = float(val or 0) * 100
    s = f"{pct:.3f}".rstrip("0").rstrip(".")
    return f"{s.replace('.', ',')}%"


def calc_margen_efectivo(params: dict) -> dict:
    margen_base = float(params.get("margen", 0.17) or 0.0)
    rte = float(params.get("rte", 0.11) or 0.0) if params.get("aplicaRte", True) else 0.0
    ica = float(params.get("ica", 0.00966) or 0.0) if params.get("aplicaIca", False) else 0.0
    rete_iva = float(params.get("reteIva", 0.0285) or 0.0) if params.get("aplicaReteIva", False) else 0.0
    rete_ica = float(params.get("reteIca", 0.00966) or 0.0) if params.get("aplicaReteIca", False) else 0.0
    cuatro_por_mil = float(params.get("cuatroPorMil", 0.004) or 0.0) if params.get("aplica4x1000", True) else 0.0

    impuestos = rte + ica + rete_iva + rete_ica + cuatro_por_mil
    total_pct = margen_base + impuestos
    return {
        "margenBase": margen_base,
        "rte": rte,
        "ica": ica,
        "reteIva": rete_iva,
        "reteIca": rete_ica,
        "cuatroPorMil": cuatro_por_mil,
        "impuestos": impuestos,
        "totalPct": total_pct,
    }


def calc_tabla_dotacion(catalogo: list[dict], modo: str = "operativo", meses: int = 12) -> dict:
    """
    Calcula los totales de la tabla base de dotación (Operativos o Administrativos).
    modo: 'operativo' | 'administrativo'
    """
    campo_cant = "cantOperativo" if modo == "operativo" else "cantAdministrativo"
    meses_div = max(float(meses or 12), 1.0)
    total_anual = 0.0
    total_senas = 0.0
    filas = []

    for item in catalogo:
        cant = float(item.get(campo_cant, 0) or 0)
        precio = float(item.get("precioUnitario", 0) or 0)
        subtotal = cant * precio
        total_anual += subtotal
        es_carne = bool(item.get("esCarne", False)) or "carn" in str(item.get("nombre", "")).lower()
        if not es_carne:
            total_senas += subtotal
        filas.append({
            "id": item["id"],
            "nombre": item.get("nombre", ""),
            "cantidadAnio": cant,
            "precioUnitario": precio,
            "valorTotal": subtotal,
            "descripcion": item.get("descripcion", ""),
            "esCarne": es_carne,
        })

    costo_mes = total_anual / meses_div
    return {
        "filas": filas,
        "totalAnual": total_anual,
        "totalSenas": total_senas,
        "meses": meses_div,
        "costoMes": costo_mes,
    }


def calc_dotacion_perfil(perfil: dict, params: dict, catalogo: list[dict] | None = None) -> dict:
    """
    Calcula el costo anual y mensual de Dotación / EPP para un perfil de RRHH específico.
    - Si perfil['dotacion'] es False -> costoAplicadoMes = 0.0 (pero igual retorna el desglose configurado).
    - Si perfil tiene 'dotacionCantidades', suma (cantidad_anual * precioUnitario) de cada elemento seleccionado.
    - Si no tiene 'dotacionCantidades', usa params.get('dotacionMes', 41250).
    """
    cat = catalogo if catalogo is not None else get_catalogo_base_dotacion()
    meses_div = max(float(perfil.get("dotacionMeses", params.get("dotacionMesesAnio", 12)) or 12), 1.0)
    cant_map = perfil.get("dotacionCantidades")

    if isinstance(cant_map, dict) and len(cant_map) > 0:
        total_anual = 0.0
        total_senas = 0.0
        items_activos = []
        for item in cat:
            iid = int(item["id"])
            cant = float(cant_map.get(iid, cant_map.get(str(iid), 0)) or 0)
            precio = float(item.get("precioUnitario", 0) or 0)
            sub = cant * precio
            total_anual += sub
            es_carne = bool(item.get("esCarne", False)) or "carn" in str(item.get("nombre", "")).lower()
            if not es_carne:
                total_senas += sub
            if cant > 0:
                items_activos.append({
                    "id": iid,
                    "nombre": item.get("nombre", ""),
                    "cantidadAnio": cant,
                    "precioUnitario": precio,
                    "valorTotal": sub,
                })
        costo_mes_calculado = total_anual / meses_div
    else:
        costo_mes_calculado = float(params.get("dotacionMes", 41250) or 0.0)
        total_anual = costo_mes_calculado * meses_div
        total_senas = total_anual
        items_activos = []

    aplica = bool(perfil.get("dotacion", False))
    return {
        "aplica": aplica,
        "totalAnual": total_anual,
        "totalSenas": total_senas,
        "meses": meses_div,
        "costoMesConfigurado": costo_mes_calculado,
        "costoMes": costo_mes_calculado if aplica else 0.0,
        "itemsActivos": items_activos,
    }


def costo_rrhh(perfil: dict, unidad: str, params: dict, catalogo_dotacion: list[dict] | None = None) -> float:
    smmlv = float(params.get("salMin", 1750905))
    salario = float(perfil.get("salario", 0) or 0)
    aux_fijo = float(perfil.get("auxFijo", 0) or 0)
    bono = float(perfil.get("bono", 0) or 0)

    aux_trans = 0.0 if salario == 0 else (
        float(params.get("auxTrans", 249095)) if salario < 2 * smmlv else 0.0
    )

    arl_map = params.get("arl", {})
    nivel = int(perfil.get("arlNivel", 1))
    arl = float(arl_map.get(nivel, arl_map.get(str(nivel), 0.0)))

    if salario < 13 * smmlv:
        if perfil.get("contrato") == "directo":
            f = float(params.get("factDirecto", 0.43)) + arl
            base = salario * (1 + f) + aux_fijo + aux_trans
        else:
            f = float(params.get("factSub", 0.57)) + arl
            base = salario * (1 + f) * 1.065 + aux_fijo * 1.03 + aux_trans * 1.03
    else:
        if not perfil.get("prestacional", True):
            f = float(params.get("factIntegral", 0.41)) + arl
            base = salario + salario * 0.7 * f
        else:
            f = float(params.get("factAlto", 0.567)) + arl
            base = salario * (1 + f) + aux_fijo + aux_trans

    base += bono
    dot_info = calc_dotacion_perfil(perfil, params, catalogo_dotacion)
    dot = dot_info["costoMes"]
    util = float(perfil.get("util", 1.0) or 1.0)
    if util <= 0:
        util = 1.0

    mes = (base + dot) / util
    dias_mes = float(params.get("diasMes", 22) or 22)
    horas_dia = float(params.get("horasDia", 8) or 8)
    dia = mes / dias_mes
    hora = dia / horas_dia

    return {"MES": mes, "DIA": dia, "HORA": hora, "UNIDAD": mes}.get(unidad, mes)


def costo_recurso(recurso: dict, unidad: str, params: dict) -> float:
    costo = float(recurso.get("costo", 0) or 0)
    meses = max(float(recurso.get("meses", 1) or 1), 1.0)
    mtto = float(recurso.get("mtto", 0) or 0)
    factor_uso = max(float(recurso.get("factorUso", 1) or 1), 0.01)

    mes = (costo / meses) * (1 + mtto) / factor_uso
    dias_mes = float(params.get("diasMes", 22) or 22)
    horas_dia = float(params.get("horasDia", 8) or 8)
    dia = mes / dias_mes
    hora = dia / horas_dia

    return {"MES": mes, "DIA": dia, "HORA": hora, "UNIDAD": costo}.get(unidad, mes)


def calc_row(row: dict, state: dict) -> dict:
    params = state["p"]
    cat_dot = state.get("dotacionCatalogo")
    tipo = row.get("tipo", "manual")
    ref = row.get("ref")
    unidad = row.get("unidad", "MES")

    cu = 0.0
    if tipo == "rrhh":
        perfil = next((r for r in state["rrhh"] if r["id"] == ref), None)
        cu = costo_rrhh(perfil, unidad, params, cat_dot) if perfil else 0.0
    elif tipo == "recurso":
        rec = next((r for r in state["recursos"] if r["id"] == ref), None)
        cu = costo_recurso(rec, unidad, params) if rec else 0.0
    else:
        cu = float(row.get("costoManual", 0) or 0)

    tiempo = float(row.get("tiempo", 0) or 0)
    dedic = float(row.get("dedic", 1) or 1)
    cant = float(row.get("cant", 0) or 0)

    total = round(tiempo * dedic * cant * cu)
    m_info = calc_margen_efectivo(params)
    divisor = (1.0 - m_info["totalPct"]) if (1.0 - m_info["totalPct"]) != 0 else 1.0
    venta = round(total / divisor)

    return {"cu": cu, "total": total, "venta": venta}


def calc_item(item: dict, state: dict) -> dict:
    por_cat = {c: {"total": 0, "venta": 0} for c in CATS}
    total = 0
    venta = 0

    for row in item.get("filas", []):
        res = calc_row(row, state)
        cat = row.get("cat", "OTROS")
        if cat == "EQUIPOS":
            cat = "EQUIPOS Y SOFTWARE"
        elif cat == "SERVICIOS EXTERNOS/INTERNOS":
            cat = "SERVICIOS EXTERNOS"
        if cat not in por_cat:
            por_cat[cat] = {"total": 0, "venta": 0}
        por_cat[cat]["total"] += res["total"]
        por_cat[cat]["venta"] += res["venta"]
        total += res["total"]
        venta += res["venta"]

    return {"porCat": por_cat, "total": total, "venta": venta}


def calc_resumen_general(state: dict) -> dict:
    items_resumen = []
    subtotal = 0

    for idx, item in enumerate(state.get("items", []), start=1):
        c = calc_item(item, state)
        cant = float(item.get("cantidad", 0) or 0)
        valor_u = c["venta"]
        valor_t = round(valor_u * cant)
        subtotal += valor_t
        items_resumen.append({
            "idx": idx,
            "id": item["id"],
            "nombre": item.get("nombre", ""),
            "tiempoTexto": item.get("tiempoTexto", ""),
            "unidadEntrega": item.get("unidadEntrega", "GLB"),
            "cantidad": cant,
            "costoUnitario": c["total"],
            "valorUnitario": valor_u,
            "valorTotal": valor_t,
        })

    iva_pct = float(state["p"].get("iva", 0.19) or 0)
    rte_pct = float(state["p"].get("rte", 0.11) or 0)
    iva = round(subtotal * iva_pct)
    con_iva = subtotal + iva
    rte = round(subtotal * rte_pct)
    neto = con_iva - rte

    return {
        "items": items_resumen,
        "subtotal": subtotal,
        "iva": iva,
        "conIva": con_iva,
        "rte": rte,
        "neto": neto,
    }


def fmt_num_informe(val: float, dash_if_zero: bool = True) -> str:
    """Formatea valores numéricos al estilo del Informe GM (ej. '1.127.325,00' o '-' si es 0)."""
    try:
        num = float(val or 0.0)
        if dash_if_zero and abs(num) < 0.005:
            return "-"
        entero = int(abs(num))
        dec = int(round((abs(num) - entero) * 100))
        if dec == 100:
            entero += 1
            dec = 0
        sign = "-" if num < 0 else ""
        entero_str = f"{entero:,}".replace(",", ".")
        return f"{sign}{entero_str},{dec:02d}"
    except (ValueError, TypeError):
        return "-" if dash_if_zero else "0,00"


def fmt_pct_informe(val: float) -> str:
    """Formatea un porcentaje en formato '(17,4%)' o '(0,0%)'."""
    pct = float(val or 0.0) * 100.0
    return f"({pct:.1f}%)".replace(".", ",")


def calc_informe_gm(state: dict) -> dict:
    """
    Calcula todos los renglones informativos de la pestaña 'Informe'
    (1.1 GM: Escenario ejercicio lineal) a partir de los costos APU y parámetros.
    """
    p = state.get("p", {})
    proy = p.get("proyecto", {})
    resumen = calc_resumen_general(state)
    m_ef = calc_margen_efectivo(p)

    plazo_meses = float(proy.get("plazoMeses", 1) or 1)
    valor_total_antes_iva = float(resumen["subtotal"] or 0.0)
    valor_mensual_antes_iva = (
        valor_total_antes_iva / plazo_meses if plazo_meses > 1 else valor_total_antes_iva
    )
    total_meses_str = "-" if plazo_meses <= 1 else f"{plazo_meses:g}".replace(".", ",")

    iva_pct = float(p.get("iva", 0.19) or 0.0)
    iva_val = round(valor_total_antes_iva * iva_pct)
    valor_con_iva = valor_total_antes_iva + iva_val

    # b. GROSS MARGIN - Utilidad Operacional
    ingresos_op = valor_total_antes_iva
    costo_op_total = float(
        sum(round(float(it["costoUnitario"]) * float(it["cantidad"])) for it in resumen["items"])
    )
    gm_val = ingresos_op - costo_op_total
    gm_pct = (gm_val / ingresos_op) if ingresos_op > 0 else m_ef["totalPct"]

    # c. Pólizas - Impuestos Departamentales, otros gastos
    polizas_pct = 0.0
    polizas_val = 0.0

    ica_pct = float(p.get("ica", 0.00966) or 0.0) if p.get("aplicaIca", False) else 0.0
    rete_iva_pct = float(p.get("reteIva", 0.0285) or 0.0) if p.get("aplicaReteIva", False) else 0.0
    rete_ica_pct = float(p.get("reteIca", 0.00966) or 0.0) if p.get("aplicaReteIca", False) else 0.0
    cuatro_mil_pct = float(p.get("cuatroPorMil", 0.004) or 0.0) if p.get("aplica4x1000", True) else 0.0

    otros_gastos_pct = ica_pct + cuatro_mil_pct + rete_ica_pct + rete_iva_pct
    otros_gastos_val = round(ingresos_op * otros_gastos_pct)

    intereses_pct = 0.0
    intereses_val = 0.0

    imp_renta_pct = float(p.get("rte", 0.11) or 0.0) if p.get("aplicaRte", True) else 0.0
    imp_renta_val = round(ingresos_op * imp_renta_pct)

    otros_imp_pct = 0.0
    otros_imp_val = 0.0

    estructura_pct = 0.0
    estructura_val = 0.0

    gestion_pct = 0.0
    gestion_val = 0.0

    amortizacion_pct = 0.0
    amortizacion_val = 0.0

    total_gastos_c = (
        polizas_val
        + otros_gastos_val
        + intereses_val
        + imp_renta_val
        + otros_imp_val
        + estructura_val
        + gestion_val
        + amortizacion_val
    )
    utilidad_val = gm_val - total_gastos_c
    utilidad_pct = (utilidad_val / ingresos_op) if ingresos_op > 0 else m_ef["margenBase"]

    k_ofertado = (ingresos_op / costo_op_total) if costo_op_total > 0 else 0.0

    return {
        "valorMensualAntesIva": valor_mensual_antes_iva,
        "totalMesesStr": total_meses_str,
        "valorTotalAntesIva": valor_total_antes_iva,
        "ivaPct": iva_pct,
        "ivaVal": iva_val,
        "valorConIva": valor_con_iva,
        "ingresosOp": ingresos_op,
        "costoOpTotal": costo_op_total,
        "gmVal": gm_val,
        "gmPct": gm_pct,
        "polizasPct": polizas_pct,
        "polizasVal": polizas_val,
        "otrosGastosPct": otros_gastos_pct,
        "otrosGastosVal": otros_gastos_val,
        "interesesPct": intereses_pct,
        "interesesVal": intereses_val,
        "impRentaPct": imp_renta_pct,
        "impRentaVal": imp_renta_val,
        "otrosImpPct": otros_imp_pct,
        "otrosImpVal": otros_imp_val,
        "estructuraPct": estructura_pct,
        "estructuraVal": estructura_val,
        "gestionPct": gestion_pct,
        "gestionVal": gestion_val,
        "amortizacionPct": amortizacion_pct,
        "amortizacionVal": amortizacion_val,
        "utilidadVal": utilidad_val,
        "utilidadPct": utilidad_pct,
        "kOfertado": k_ofertado,
    }


if __name__ == "__main__":
    try:
        import streamlit as _st
        _st.warning(
            "⚠️ Estás ejecutando `calculator.py` directamente. "
            "Para abrir el Cotizador APU debes ejecutar **`app.py`** "
            "(y verificar que cada archivo `.py` tenga su propio contenido y esté guardado con Ctrl + S)."
        )
    except Exception:
        pass


