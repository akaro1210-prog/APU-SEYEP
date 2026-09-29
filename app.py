"""
app.py — Punto de entrada principal de la aplicación Streamlit para el Cotizador APU.
Ejecución: streamlit run app.py
"""
import base64
import json
import pandas as pd
import streamlit as st
from state import (
    CATS,
    INTRO_ECO_CONSOLIDADA,
    INTRO_ECO_INDIVIDUAL,
    SECCIONES_RECURSOS,
    UNIDADES,
    build_dotacion_perfil_from_catalogo,
    get_catalogo_base_dotacion,
    get_catalogo_base_recursos,
    init_session_state,
    next_id,
)
from calculator import (
    costo_rrhh,
    costo_recurso,
    calc_dotacion_perfil,
    calc_tabla_dotacion,
    calc_row,
    calc_item,
    calc_margen_efectivo,
    calc_resumen_general,
    calc_informe_gm,
    fmt_cop,
    fmt_pct,
    fmt_num_informe,
    fmt_pct_informe,
)
from pdf_generator import generar_pdf_formato_a, generar_pdf_formato_b

st.set_page_config(
    page_title="Cotizador APU — SEYEP SAS",
    page_icon="🧮",
    layout="wide",
)

init_session_state()
state = st.session_state["apu_state"]

col_title, col_pdf_a, col_pdf_b = st.columns([3.5, 1.2, 1.2])
with col_title:
    st.title("🧮 Cotizador APU — SEYEP SAS")
    st.caption("Herramienta de Análisis de Precios Unitarios y Generación Directa de Cotizaciones en PDF")
with col_pdf_a:
    st.write("")
    st.download_button(
        label="📄 Descargar PDF Propuesta (A)",
        data=generar_pdf_formato_a(state),
        file_name=f"Propuesta_{state['cot'].get('referencia') or 'SEYEP'}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with col_pdf_b:
    st.write("")
    st.download_button(
        label="⚡ Descargar PDF Rápido (B)",
        data=generar_pdf_formato_b(state),
        file_name=f"Cotizacion_Rapida_{state['cot'].get('referencia') or 'SEYEP'}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

tabs = st.tabs([
    "⚙️ 1. Parámetros",
    "👷 2. Personal (RRHH)",
    "🧰 3. Equipos y materiales",
    "📋 4. Ítems / APU",
    "💰 5. Resumen y oferta",
    "📄 6. PDF Propuesta (Formato A)",
    "📄 7. PDF Rápido (Formato B)",
    "📊 8. Informe",
])

# ================= TAB 1: PARÁMETROS =================
with tabs[0]:
    P = state["p"]
    with st.container(border=True):
        st.subheader("Información del proyecto")
        c1, c2, c3 = st.columns(3)
        with c1:
            P["proyecto"]["nombre"] = st.text_input("Nombre del proyecto", value=P["proyecto"]["nombre"])
            P["proyecto"]["plazoMeses"] = st.number_input("Plazo de ejecución (meses)", value=float(P["proyecto"]["plazoMeses"]), min_value=0.1, step=1.0)
        with c2:
            P["proyecto"]["contratante"] = st.text_input("Empresa contratante", value=P["proyecto"]["contratante"])
            P["proyecto"]["anticipoPct"] = st.number_input("Anticipo (%)", value=float(P["proyecto"]["anticipoPct"] * 100), step=5.0) / 100.0
        with c3:
            P["proyecto"]["contratista"] = st.text_input("Empresa contratista", value=P["proyecto"]["contratista"])
            P["proyecto"]["formaPagoDias"] = st.number_input("Forma de pago (días)", value=int(P["proyecto"]["formaPagoDias"]), step=5)

    with st.container(border=True):
        st.subheader("Impuestos, margen comercial y tributos sumados al APU")
        i1, i2 = st.columns(2)
        with i1:
            P["iva"] = st.number_input("IVA facturación (%)", value=float(P["iva"] * 100), step=1.0, format="%.2f") / 100.0
        with i2:
            P["margen"] = st.number_input("Margen de ganancia base (%)", value=float(P["margen"] * 100), step=0.5, format="%.2f") / 100.0

        st.markdown("---")
        st.markdown("**Selección de impuestos y retenciones aplicables en la cotización (se suman con el margen de ganancia en el APU):**")
        t0, t1, t2, t3, t4 = st.columns(5)
        with t0:
            P["aplicaRte"] = st.checkbox("Sumar Retefuente al Margen", value=bool(P.get("aplicaRte", True)))
            P["rte"] = st.number_input("Retefuente (%)", value=float(P.get("rte", 0.11) * 100), step=0.5, format="%.2f", disabled=not P["aplicaRte"], key="rte_sum_inp") / 100.0
        with t1:
            P["aplicaIca"] = st.checkbox("Aplicar ICA", value=bool(P.get("aplicaIca", False)))
            P["ica"] = st.number_input("ICA (%)", value=float(P.get("ica", 0.00966) * 100), step=0.01, format="%.3f", disabled=not P["aplicaIca"]) / 100.0
        with t2:
            P["aplicaReteIva"] = st.checkbox("Aplicar Rete IVA", value=bool(P.get("aplicaReteIva", False)))
            P["reteIva"] = st.number_input("Rete IVA (%)", value=float(P.get("reteIva", 0.0285) * 100), step=0.05, format="%.3f", disabled=not P["aplicaReteIva"]) / 100.0
        with t3:
            P["aplicaReteIca"] = st.checkbox("Aplicar Rete ICA", value=bool(P.get("aplicaReteIca", False)))
            P["reteIca"] = st.number_input("Rete ICA (%)", value=float(P.get("reteIca", 0.00966) * 100), step=0.01, format="%.3f", disabled=not P["aplicaReteIca"]) / 100.0
        with t4:
            P["aplica4x1000"] = st.checkbox("Aplicar 4x1000", value=bool(P.get("aplica4x1000", True)))
            P["cuatroPorMil"] = st.number_input("4x1000 (%)", value=float(P.get("cuatroPorMil", 0.004) * 100), step=0.05, format="%.3f", disabled=not P["aplica4x1000"]) / 100.0

        m_ef = calc_margen_efectivo(P)
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Margen de Ganancia Base", f"{m_ef['margenBase']*100:.2f}%")
        mc2.metric("+ Retefuente e Impuestos Seleccionados", f"{m_ef['impuestos']*100:.3f}%")
        mc3.metric("= Margen Total + Impuestos (APU)", f"{m_ef['totalPct']*100:.3f}%")
        st.caption("Fórmula aplicada a cada ítem en el APU: Valor de Venta = Costo Directo / (1 − (Margen Base + Retefuente + Impuestos Seleccionados)).")

    with st.container(border=True):
        st.subheader("Salario mínimo, factores prestacionales y ARL")
        s1, s2, s3 = st.columns(3)
        with s1:
            P["salMin"] = st.number_input("Salario mínimo legal vigente (COP)", value=int(P["salMin"]), step=10000)
        with s2:
            P["auxTrans"] = st.number_input("Auxilio de transporte (COP)", value=int(P["auxTrans"]), step=5000)
        with s3:
            P["dotacionMes"] = st.number_input("Dotación / EPP mensual base referencial", value=int(P["dotacionMes"]), step=5000)

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            P["factDirecto"] = st.number_input("Contratación directa (< 13 SMMLV) %", value=float(P["factDirecto"] * 100), step=0.5) / 100.0
        with f2:
            P["factSub"] = st.number_input("Subcontratación / ETT %", value=float(P["factSub"] * 100), step=0.5) / 100.0
        with f3:
            P["factAlto"] = st.number_input("Salario alto (> 13 SMMLV) %", value=float(P["factAlto"] * 100), step=0.5) / 100.0
        with f4:
            P["factIntegral"] = st.number_input("Contrato integral %", value=float(P["factIntegral"] * 100), step=0.5) / 100.0

        st.markdown("**Riesgo ARL por nivel (%) y Calendario**")
        a_cols = st.columns(7)
        for idx_arl, nivel in enumerate([1, 2, 3, 4, 5]):
            val_actual = float(P["arl"].get(nivel, P["arl"].get(str(nivel), 0.0)) * 100)
            P["arl"][nivel] = a_cols[idx_arl].number_input(f"ARL Nivel {nivel} (%)", value=val_actual, step=0.01, format="%.3f") / 100.0
        P["diasMes"] = a_cols[5].number_input("Días hábiles/mes", value=int(P["diasMes"]), min_value=1, step=1)
        P["horasDia"] = a_cols[6].number_input("Horas/día", value=int(P["horasDia"]), min_value=1, step=1)

# ================= TAB 2: PERSONAL (RRHH) + DOTACIÓN Y EPP =================
with tabs[1]:
    cat_dot = state["dotacionCatalogo"]
    meses_dot_global = int(state["p"].get("dotacionMesesAnio", 12) or 12)

    head_c1, head_c2 = st.columns([3.5, 1.5])
    with head_c1:
        st.subheader("Perfiles de Recursos Humanos (RRHH) y Selección de Dotación / EPP")
        st.caption("Configura los perfiles salariales y despliega la sección de Dotación / EPP de cada perfil para seleccionar los elementos y cantidades anuales que le aplican.")
    with head_c2:
        if st.button("+ Agregar perfil RRHH", type="primary", use_container_width=True):
            state["rrhh"].append({
                "id": next_id(),
                "nombre": "Nuevo perfil",
                "salario": int(state["p"]["salMin"]),
                "auxFijo": 0,
                "bono": 0,
                "contrato": "directo",
                "prestacional": True,
                "arlNivel": 1,
                "dotacion": True,
                "tipoDotacion": "operativo",
                "dotacionMeses": meses_dot_global,
                "dotacionCantidades": build_dotacion_perfil_from_catalogo(cat_dot, "operativo"),
                "util": 1.0,
            })
            st.rerun()

    for r in list(state["rrhh"]):
        with st.container(border=True):
            cols = st.columns([2.1, 1.3, 1.1, 1.1, 1.3, 1.2, 0.8, 0.9, 0.9, 2.3, 0.5])
            r["nombre"] = cols[0].text_input("Nombre del perfil", value=r["nombre"], key=f"rrhh_nom_{r['id']}")
            r["salario"] = cols[1].number_input("Salario base", value=int(r["salario"]), step=50000, key=f"rrhh_sal_{r['id']}")
            r["auxFijo"] = cols[2].number_input("Aux. fijo", value=int(r["auxFijo"]), step=10000, key=f"rrhh_aux_{r['id']}")
            r["bono"] = cols[3].number_input("Bono var.", value=int(r["bono"]), step=10000, key=f"rrhh_bon_{r['id']}")
            r["contrato"] = cols[4].selectbox("Contrato", ["directo", "subcontratado"], index=0 if r["contrato"] == "directo" else 1, key=f"rrhh_con_{r['id']}")
            r["prestacional"] = cols[5].selectbox("Prestacional", [True, False], format_func=lambda x: "Sí" if x else "No (integral)", index=0 if r["prestacional"] else 1, key=f"rrhh_pre_{r['id']}")
            r["arlNivel"] = cols[6].selectbox("ARL", [1, 2, 3, 4, 5], index=int(r["arlNivel"]) - 1, key=f"rrhh_arl_{r['id']}")
            r["dotacion"] = cols[7].checkbox("Aplica Dotación", value=bool(r["dotacion"]), key=f"rrhh_dot_{r['id']}")
            r["util"] = cols[8].number_input("Util.", value=float(r["util"]), min_value=0.1, step=0.1, key=f"rrhh_uti_{r['id']}")

            dot_info = calc_dotacion_perfil(r, state["p"], cat_dot)
            c_mes = costo_rrhh(r, "MES", state["p"], cat_dot)
            c_dia = costo_rrhh(r, "DIA", state["p"], cat_dot)
            c_hor = costo_rrhh(r, "HORA", state["p"], cat_dot)
            cols[9].markdown(
                f"**Mes:** {fmt_cop(c_mes)} *(Dot: {fmt_cop(dot_info['costoMes'])})*  \n"
                f"**Día:** {fmt_cop(c_dia)} · **Hora:** {fmt_cop(c_hor)}"
            )
            if cols[10].button("✕", key=f"del_rrhh_{r['id']}"):
                state["rrhh"].remove(r)
                st.rerun()

            # ---- SECCIÓN DESPLEGABLE DE DOTACIÓN / EPP POR PERFIL ----
            resumen_items_txt = (
                f"{len(dot_info['itemsActivos'])} elementos seleccionados · "
                f"Anual: {fmt_cop(dot_info['totalAnual'])} · "
                f"Mensual ({int(dot_info['meses'])}m): {fmt_cop(dot_info['costoMesConfigurado'])}"
            )
            estado_dot_badge = "✅ ACTIVA EN COSTO" if r["dotacion"] else "⚪ INACTIVA (No suma al costo)"

            with st.expander(f"🦺 Seleccionar Dotación y EPP para «{r['nombre']}» — [{estado_dot_badge}] — {resumen_items_txt}", expanded=False):
                b_col1, b_col2, b_col3, b_col4 = st.columns([1.4, 1.4, 1.2, 1.5])
                if b_col1.button("📋 Cargar tabla Operativos", key=f"btn_op_{r['id']}", use_container_width=True):
                    r["tipoDotacion"] = "operativo"
                    r["dotacionCantidades"] = build_dotacion_perfil_from_catalogo(cat_dot, "operativo")
                    r["dotacion"] = True
                    st.rerun()
                if b_col2.button("📋 Cargar tabla Administrativos", key=f"btn_ad_{r['id']}", use_container_width=True):
                    r["tipoDotacion"] = "administrativo"
                    r["dotacionCantidades"] = build_dotacion_perfil_from_catalogo(cat_dot, "administrativo")
                    r["dotacion"] = True
                    st.rerun()
                if b_col3.button("🧹 Limpiar selección (0)", key=f"btn_cl_{r['id']}", use_container_width=True):
                    r["tipoDotacion"] = "personalizado"
                    r["dotacionCantidades"] = {int(it["id"]): 0.0 for it in cat_dot}
                    st.rerun()
                r["dotacionMeses"] = b_col4.number_input(
                    "Meses amortización dotación",
                    value=int(r.get("dotacionMeses", 12) or 12),
                    min_value=1,
                    max_value=60,
                    step=1,
                    key=f"dot_meses_perf_{r['id']}",
                )

                st.markdown("##### Detalle de elementos de Dotación / EPP para este perfil")
                h_cols = st.columns([0.6, 2.4, 1.2, 1.3, 1.3, 2.6])
                h_cols[0].markdown("**Aplica**")
                h_cols[1].markdown("**Dotación (Producto)**")
                h_cols[2].markdown("**Cant. / año**")
                h_cols[3].markdown("**Precio Unitario**")
                h_cols[4].markdown("**Valor Total Año**")
                h_cols[5].markdown("**Descripción**")

                for item_d in cat_dot:
                    iid = int(item_d["id"])
                    cant_actual = float(r["dotacionCantidades"].get(iid, 0.0) or 0.0)
                    aplica_item = cant_actual > 0

                    ic = st.columns([0.6, 2.4, 1.2, 1.3, 1.3, 2.6])
                    chk = ic[0].checkbox(
                        "✔",
                        value=aplica_item,
                        key=f"chk_p_{r['id']}_{iid}",
                        label_visibility="collapsed",
                    )
                    ic[1].markdown(f"**{item_d['nombre']}**")

                    # Si el usuario activa el check y estaba en 0, asignamos 1 por defecto (o cantOperativo si > 0)
                    if chk and cant_actual == 0:
                        default_c = float(item_d.get("cantOperativo", 1) or 1)
                        cant_actual = default_c if default_c > 0 else 1.0
                        r["dotacionCantidades"][iid] = cant_actual
                    elif not chk and cant_actual > 0:
                        cant_actual = 0.0
                        r["dotacionCantidades"][iid] = 0.0

                    nueva_cant = ic[2].number_input(
                        "Cant/año",
                        value=float(cant_actual),
                        min_value=0.0,
                        step=1.0,
                        key=f"cnt_p_{r['id']}_{iid}",
                        label_visibility="collapsed",
                    )
                    r["dotacionCantidades"][iid] = nueva_cant

                    precio_u = float(item_d.get("precioUnitario", 0) or 0)
                    subtotal_i = nueva_cant * precio_u
                    ic[3].markdown(f"`{fmt_cop(precio_u)}`")
                    ic[4].markdown(f"**{fmt_cop(subtotal_i)}**" if subtotal_i > 0 else "—")
                    ic[5].caption(item_d.get("descripcion", ""))

                dot_recalc = calc_dotacion_perfil(r, state["p"], cat_dot)
                m_d1, m_d2, m_d3, m_d4 = st.columns(4)
                m_d1.metric("Total Dotación básica año", fmt_cop(dot_recalc["totalAnual"]))
                m_d2.metric("Dotación SENAS (sin Carné)", fmt_cop(dot_recalc["totalSenas"]))
                m_d3.metric("Meses (Amortización)", f"{int(dot_recalc['meses'])} meses")
                m_d4.metric("Dotación básica (mes) perfil", fmt_cop(dot_recalc["costoMesConfigurado"]))

    st.markdown("---")
    # ---- SECCIÓN DE TABLAS MAESTRAS DE DOTACIÓN (OPERATIVOS Y ADMINISTRATIVOS) ----
    with st.expander("📦 Catálogo y Tablas Base de Dotación — DETALLE EPP COLABORADORES OPERATIVOS Y ADMINISTRATIVOS (Excel)", expanded=True):
        top_d1, top_d2, top_d3, top_d4 = st.columns([2.5, 1.2, 1.3, 1.3])
        with top_d1:
            st.markdown(
                "Modifica los precios unitarios, descripciones o cantidades anuales base para **Colaboradores Operativos** y **Colaboradores Administrativos** tal como en tu hoja de Excel."
            )
        with top_d2:
            state["p"]["dotacionMesesAnio"] = st.number_input(
                "Meses base de cálculo (Año)",
                value=int(state["p"].get("dotacionMesesAnio", 12) or 12),
                min_value=1,
                max_value=60,
                step=1,
            )
        with top_d3:
            if st.button("+ Agregar elemento EPP al catálogo", use_container_width=True):
                nuevo_id = next_id()
                cat_dot.append({
                    "id": nuevo_id,
                    "nombre": "Nuevo EPP / Dotación",
                    "precioUnitario": 0,
                    "cantOperativo": 1,
                    "cantAdministrativo": 0,
                    "descripcion": "Descripción del elemento",
                    "esCarne": False,
                })
                for perf in state["rrhh"]:
                    perf.setdefault("dotacionCantidades", {})[nuevo_id] = 0.0
                st.rerun()
        with top_d4:
            if st.button("🔄 Restaurar tabla EPP Excel", use_container_width=True):
                state["dotacionCatalogo"] = get_catalogo_base_dotacion()
                for perf in state["rrhh"]:
                    tipo_p = perf.get("tipoDotacion", "operativo")
                    perf["dotacionCantidades"] = build_dotacion_perfil_from_catalogo(
                        state["dotacionCatalogo"],
                        tipo_p if tipo_p in ("operativo", "administrativo") else "operativo",
                    )
                st.rerun()

        tab_op, tab_adm = st.tabs([
            "🟠 DETALLE - EPP - COLABORADORES OPERATIVOS",
            "🟠 DETALLE - EPP - COLABORADORES ADMINISTRATIVOS",
        ])

        with tab_op:
            st.markdown("##### DETALLE - EPP - COLABORADORES OPERATIVOS")
            hc = st.columns([2.2, 1.1, 1.3, 1.3, 2.6, 0.5])
            hc[0].markdown("**Dotación (Producto)**")
            hc[1].markdown("**Cantidad / año**")
            hc[2].markdown("**Precio Unitario**")
            hc[3].markdown("**Valor total**")
            hc[4].markdown("**Descripción**")
            hc[5].markdown("**Elim.**")

            for item in list(cat_dot):
                rc = st.columns([2.2, 1.1, 1.3, 1.3, 2.6, 0.5])
                item["nombre"] = rc[0].text_input("Producto", value=item["nombre"], key=f"op_nom_{item['id']}", label_visibility="collapsed")
                item["cantOperativo"] = rc[1].number_input("Cant Op", value=float(item.get("cantOperativo", 0)), min_value=0.0, step=1.0, key=f"op_cnt_{item['id']}", label_visibility="collapsed")
                item["precioUnitario"] = rc[2].number_input("Precio", value=int(item.get("precioUnitario", 0)), min_value=0, step=1000, key=f"op_pre_{item['id']}", label_visibility="collapsed")
                val_tot_op = float(item["cantOperativo"]) * float(item["precioUnitario"])
                rc[3].markdown(f"**{fmt_cop(val_tot_op)}**" if val_tot_op > 0 else "—")
                item["descripcion"] = rc[4].text_input("Desc", value=item.get("descripcion", ""), key=f"op_des_{item['id']}", label_visibility="collapsed")
                if rc[5].button("✕", key=f"del_dot_op_{item['id']}"):
                    cat_dot.remove(item)
                    st.rerun()

            res_op = calc_tabla_dotacion(cat_dot, "operativo", state["p"]["dotacionMesesAnio"])
            o1, o2, o3, o4 = st.columns(4)
            o1.metric("Total Dotación básica año (Operativos)", fmt_cop(res_op["totalAnual"]))
            o2.metric("Dotación SENAS", fmt_cop(res_op["totalSenas"]))
            o3.metric("Meses", f"{int(res_op['meses'])}")
            o4.metric("Dotación básica (mes)", fmt_cop(res_op["costoMes"]))

        with tab_adm:
            st.markdown("##### DETALLE - EPP - COLABORADORES ADMINISTRATIVOS")
            hc = st.columns([2.2, 1.1, 1.3, 1.3, 2.6, 0.5])
            hc[0].markdown("**Dotación (Producto)**")
            hc[1].markdown("**Cantidad / año**")
            hc[2].markdown("**Precio Unitario**")
            hc[3].markdown("**Valor total**")
            hc[4].markdown("**Descripción**")
            hc[5].markdown("**Elim.**")

            for item in list(cat_dot):
                rc = st.columns([2.2, 1.1, 1.3, 1.3, 2.6, 0.5])
                item["nombre"] = rc[0].text_input("Producto", value=item["nombre"], key=f"ad_nom_{item['id']}", label_visibility="collapsed")
                item["cantAdministrativo"] = rc[1].number_input("Cant Adm", value=float(item.get("cantAdministrativo", 0)), min_value=0.0, step=1.0, key=f"ad_cnt_{item['id']}", label_visibility="collapsed")
                item["precioUnitario"] = rc[2].number_input("Precio", value=int(item.get("precioUnitario", 0)), min_value=0, step=1000, key=f"ad_pre_{item['id']}", label_visibility="collapsed")
                val_tot_ad = float(item["cantAdministrativo"]) * float(item["precioUnitario"])
                rc[3].markdown(f"**{fmt_cop(val_tot_ad)}**" if val_tot_ad > 0 else "—")
                item["descripcion"] = rc[4].text_input("Desc", value=item.get("descripcion", ""), key=f"ad_des_{item['id']}", label_visibility="collapsed")
                if rc[5].button("✕", key=f"del_dot_ad_{item['id']}"):
                    cat_dot.remove(item)
                    st.rerun()

            res_adm = calc_tabla_dotacion(cat_dot, "administrativo", state["p"]["dotacionMesesAnio"])
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Total dotación anual (Administrativos)", fmt_cop(res_adm["totalAnual"]))
            a2.metric("Dotación SENAS", fmt_cop(res_adm["totalSenas"]))
            a3.metric("Meses", f"{int(res_adm['meses'])}")
            a4.metric("Dotación Básica mes", fmt_cop(res_adm["costoMes"]))

# ================= TAB 3: EQUIPOS Y MATERIALES =================
with tabs[2]:
    top_c1, top_c2, top_c3 = st.columns([3, 1.4, 1.4])
    with top_c1:
        st.subheader("Equipos, materiales y servicios por sección (Catálogo Excel)")
        st.caption("Incluye las secciones y valores predeterminados de tu Excel. Costo Mes = (Valor Compra / Meses) × (1 + % Mtto) / Factor de uso.")
    with top_c2:
        if st.button("🔄 Restaurar lista Excel", use_container_width=True):
            state["recursos"] = get_catalogo_base_recursos()
            st.rerun()
    with top_c3:
        if st.button("+ Agregar recurso general", type="primary", use_container_width=True):
            state["recursos"].append({
                "id": next_id(),
                "seccion": "EQUIPOS Y SOFTWARE",
                "subgrupo": "AMORTIZABLES",
                "nombre": "Nuevo recurso",
                "descripcion": "",
                "unidadMedida": "UN",
                "costo": 0,
                "meses": 1,
                "mtto": 0.0,
                "factorUso": 1.0,
            })
            st.rerun()

    for idx_s, sec in enumerate(SECCIONES_RECURSOS, start=1):
        recs_sec = [r for r in state["recursos"] if r.get("seccion", "EQUIPOS Y SOFTWARE") == sec]
        with st.expander(f"📂 {idx_s}. {sec} ({len(recs_sec)} ítems)", expanded=True):
            if not recs_sec:
                st.caption("No hay recursos registrados en esta sección.")
            for r in list(recs_sec):
                with st.container(border=True):
                    cols = st.columns([1.3, 1.8, 1.8, 0.7, 1.2, 0.8, 0.8, 0.8, 1.9, 0.4])
                    r["subgrupo"] = cols[0].text_input("Subgrupo", value=r.get("subgrupo", ""), key=f"rec_sub_{r['id']}")
                    r["nombre"] = cols[1].text_input("Recurso / Ítem", value=r["nombre"], key=f"rec_nom_{r['id']}")
                    r["descripcion"] = cols[2].text_input("Descripción / Notas", value=r.get("descripcion", ""), key=f"rec_des_{r['id']}")
                    r["unidadMedida"] = cols[3].text_input("Und.", value=r.get("unidadMedida", "UN"), key=f"rec_und_{r['id']}")
                    r["costo"] = cols[4].number_input("Valor Compra ($)", value=int(r["costo"]), step=10000, key=f"rec_cos_{r['id']}")
                    r["meses"] = cols[5].number_input("Meses", value=int(r["meses"]), min_value=1, step=1, key=f"rec_mes_{r['id']}")
                    r["mtto"] = cols[6].number_input("Mtto %", value=float(r["mtto"] * 100), step=1.0, key=f"rec_mtt_{r['id']}") / 100.0
                    r["factorUso"] = cols[7].number_input("F. Uso", value=float(r["factorUso"]), min_value=0.1, step=0.1, key=f"rec_uso_{r['id']}")

                    rm = costo_recurso(r, "MES", state["p"])
                    rd = costo_recurso(r, "DIA", state["p"])
                    rh = costo_recurso(r, "HORA", state["p"])
                    cols[8].markdown(f"**Mes:** {fmt_cop(rm)}  \n**Día:** {fmt_cop(rd)} · **Hora:** {fmt_cop(rh)}")
                    if cols[9].button("✕", key=f"del_rec_{r['id']}"):
                        state["recursos"].remove(r)
                        st.rerun()

            if st.button(f"+ Agregar en {sec}", key=f"add_rec_sec_{sec}"):
                state["recursos"].append({
                    "id": next_id(),
                    "seccion": sec,
                    "subgrupo": "AMORTIZABLES" if sec in ("EQUIPOS Y SOFTWARE", "HERRAMIENTAS Y EPP") else "",
                    "nombre": f"Nuevo en {sec.lower()}",
                    "descripcion": "",
                    "unidadMedida": "UN",
                    "costo": 0,
                    "meses": 1,
                    "mtto": 0.0,
                    "factorUso": 1.0,
                })
                st.rerun()

MODO_TABLA_KEYS = [
    "modo_tabla_oferta_tab_apu",
    "modo_tabla_oferta_tab_resumen",
    "modo_tabla_oferta_tab_fmt_a",
    "modo_tabla_oferta_tab_fmt_b",
]


def _on_modo_tabla_change(source_key: str):
    """Callback ejecutado únicamente cuando el usuario cambia el radio button de disposición de tabla."""
    nuevo_modo = st.session_state.get(source_key, "individual")
    cot_obj = st.session_state["apu_state"]["cot"]
    cot_obj["modoTablaOferta"] = nuevo_modo
    for k in MODO_TABLA_KEYS:
        st.session_state[k] = nuevo_modo

    intro_act = cot_obj.get("ofertaEconomicaIntro", "").strip()
    if nuevo_modo == "consolidada" and intro_act == INTRO_ECO_INDIVIDUAL:
        cot_obj["ofertaEconomicaIntro"] = INTRO_ECO_CONSOLIDADA
        st.session_state["fa_eco_intro"] = INTRO_ECO_CONSOLIDADA
    elif nuevo_modo == "individual" and intro_act == INTRO_ECO_CONSOLIDADA:
        cot_obj["ofertaEconomicaIntro"] = INTRO_ECO_INDIVIDUAL
        st.session_state["fa_eco_intro"] = INTRO_ECO_INDIVIDUAL


def render_selector_modo_tabla(state_obj: dict, suffix: str):
    """Selector sincronizado sin st.rerun() para elegir tablas individuales o una misma tabla consolidada."""
    cot_obj = state_obj["cot"]
    modo_actual = cot_obj.get("modoTablaOferta", "individual")
    if modo_actual not in ("individual", "consolidada"):
        modo_actual = "individual"
        cot_obj["modoTablaOferta"] = "individual"

    widget_key = f"modo_tabla_oferta_{suffix}"
    if st.session_state.get(widget_key) != modo_actual:
        st.session_state[widget_key] = modo_actual

    etiquetas_modo = {
        "individual": "📋 En tablas individuales (Cada ítem con su propia tabla de subtotal, IVA y retenciones)",
        "consolidada": "📊 En la misma tabla (Agrupar todos los ítems en una sola tabla antes de impuestos y retenciones)",
    }
    st.radio(
        "Disposición de los ítems en la tabla de cotización (Oferta Económica):",
        options=["individual", "consolidada"],
        format_func=lambda x: etiquetas_modo[x],
        horizontal=True,
        key=widget_key,
        on_change=_on_modo_tabla_change,
        args=(widget_key,),
    )


# ================= TAB 4: ÍTEMS / APU =================
with tabs[3]:
    with st.container(border=True):
        col_btn1, col_btn2, col_modo = st.columns([1.4, 1.4, 4.2])
        with col_btn1:
            if st.button("+ Nuevo ítem a cotizar", type="primary", use_container_width=True):
                nuevo = {
                    "id": next_id(),
                    "nombre": f"Ítem {len(state['items']) + 1}",
                    "cantidad": 1,
                    "unidadEntrega": "GLB",
                    "tiempoTexto": "1 día",
                    "filas": [],
                }
                state["items"].append(nuevo)
                state["activeItem"] = nuevo["id"]
                st.rerun()
        with col_btn2:
            if state["items"] and st.button("✕ Eliminar ítem actual", use_container_width=True):
                state["items"] = [i for i in state["items"] if i["id"] != state["activeItem"]]
                state["activeItem"] = state["items"][0]["id"] if state["items"] else None
                st.rerun()
        with col_modo:
            render_selector_modo_tabla(state, "tab_apu")

    if state["items"]:
        item_names = {it["id"]: f"{it['nombre']} ({it['unidadEntrega']})" for it in state["items"]}
        if state.get("activeItem") not in item_names:
            state["activeItem"] = state["items"][0]["id"]

        selected_id = st.selectbox(
            "Seleccionar ítem a editar",
            options=list(item_names.keys()),
            index=list(item_names.keys()).index(state["activeItem"]),
            format_func=lambda x: item_names[x],
        )
        state["activeItem"] = selected_id
        active_item = next(i for i in state["items"] if i["id"] == selected_id)

        h1, h2, h3, h4 = st.columns([3, 1, 1, 1.5])
        active_item["nombre"] = h1.text_input("Nombre del ítem", value=active_item["nombre"], key=f"it_nom_{active_item['id']}")
        active_item["cantidad"] = h2.number_input("Cantidad proyecto", value=float(active_item["cantidad"]), min_value=0.0, step=1.0, key=f"it_can_{active_item['id']}")
        active_item["unidadEntrega"] = h3.text_input("Unidad entrega", value=active_item["unidadEntrega"], key=f"it_und_{active_item['id']}")
        active_item["tiempoTexto"] = h4.text_input("Tiempo (ej. 1 día)", value=active_item.get("tiempoTexto", ""), key=f"it_tmp_{active_item['id']}")

        opciones_ref = ["manual"]
        labels_ref = {"manual": "✏️ Manual..."}
        for p_rrhh in state["rrhh"]:
            k = f"rrhh:{p_rrhh['id']}"
            opciones_ref.append(k)
            labels_ref[k] = f"👷 {p_rrhh['nombre']}"
        for p_rec in state["recursos"]:
            k = f"recurso:{p_rec['id']}"
            opciones_ref.append(k)
            sec_tag = p_rec.get("seccion", "EQUIPOS")
            labels_ref[k] = f"🧰 [{sec_tag}] {p_rec['nombre']}"

        calc = calc_item(active_item, state)
        for cat in CATS:
            filas_cat = [f for f in active_item["filas"] if f["cat"] == cat]
            tot_cat = calc["porCat"][cat]
            with st.expander(f"{cat} — Venta: {fmt_cop(tot_cat['venta'])}", expanded=len(filas_cat) > 0):
                for f in list(filas_cat):
                    rc = st.columns([2.5, 1.8, 1.0, 0.9, 0.9, 1.0, 1.4, 1.8, 0.5])
                    current_key = "manual" if f["tipo"] == "manual" else f"{f['tipo']}:{f['ref']}"
                    if current_key not in opciones_ref:
                        current_key = "manual"
                    sel = rc[0].selectbox(
                        "Recurso",
                        options=opciones_ref,
                        index=opciones_ref.index(current_key),
                        format_func=lambda x: labels_ref.get(x, x),
                        key=f"f_sel_{f['id']}",
                    )
                    if sel == "manual":
                        f["tipo"] = "manual"
                        f["ref"] = None
                        f["nombreManual"] = rc[1].text_input("Descripción", value=f.get("nombreManual", ""), key=f"f_man_{f['id']}")
                    else:
                        t_part, r_part = sel.split(":")
                        f["tipo"] = t_part
                        f["ref"] = int(r_part)
                        rc[1].caption(labels_ref.get(sel, ""))

                    f["unidad"] = rc[2].selectbox("Unidad", UNIDADES, index=UNIDADES.index(f["unidad"]) if f["unidad"] in UNIDADES else 0, key=f"f_und_{f['id']}")
                    f["tiempo"] = rc[3].number_input("Tiempo", value=float(f["tiempo"]), step=1.0, key=f"f_tmp_{f['id']}")
                    f["cant"] = rc[4].number_input("Cant.", value=float(f["cant"]), step=1.0, key=f"f_cnt_{f['id']}")
                    f["dedic"] = rc[5].number_input("Dedic. %", value=float(f["dedic"] * 100), step=10.0, key=f"f_ded_{f['id']}") / 100.0

                    res_f = calc_row(f, state)
                    if f["tipo"] == "manual":
                        f["costoManual"] = rc[6].number_input("Costo Unit.", value=int(f.get("costoManual", 0)), step=10000, key=f"f_cman_{f['id']}")
                        res_f = calc_row(f, state)
                    else:
                        rc[6].markdown(f"**Unit.:**  \n{fmt_cop(res_f['cu'])}")

                    rc[7].markdown(f"**Total:** {fmt_cop(res_f['total'])}  \n**Venta:** {fmt_cop(res_f['venta'])}")
                    if rc[8].button("✕", key=f"del_f_{f['id']}"):
                        active_item["filas"].remove(f)
                        st.rerun()

                if st.button(f"+ Agregar recurso en {cat}", key=f"add_f_{active_item['id']}_{cat}"):
                    active_item["filas"].append({
                        "id": next_id(),
                        "cat": cat,
                        "tipo": "rrhh" if state["rrhh"] else "manual",
                        "ref": state["rrhh"][0]["id"] if state["rrhh"] else None,
                        "nombreManual": "",
                        "costoManual": 0,
                        "unidad": "DIA",
                        "tiempo": 1,
                        "cant": 1,
                        "dedic": 1.0,
                    })
                    st.rerun()

        calc = calc_item(active_item, state)
        m_ef_apu = calc_margen_efectivo(state["p"])
        m_c1, m_c2, m_c3 = st.columns(3)
        m_c1.metric("Costo Directo Base del Ítem", fmt_cop(calc["total"]))
        m_c2.metric(
            f"Margen ({m_ef_apu['margenBase']*100:.2f}%) + Impuestos ({m_ef_apu['impuestos']*100:.3f}%)",
            fmt_cop(calc["venta"] - calc["total"]),
            delta=f"Total: {m_ef_apu['totalPct']*100:.3f}%",
        )
        m_c3.metric("Costo Total / Venta del Ítem en APU", fmt_cop(calc["venta"]))

# ================= TAB 5: RESUMEN Y OFERTA =================
with tabs[4]:
    res = calc_resumen_general(state)
    with st.container(border=True):
        render_selector_modo_tabla(state, "tab_resumen")

    modo_tabla_res = state["cot"].get("modoTablaOferta", "individual")
    iva_pct_res = float(state["p"].get("iva", 0.19) or 0)
    rte_pct_res = float(state["p"].get("rte", 0.11) or 0)

    if res["items"]:
        if modo_tabla_res == "individual":
            st.subheader("Vista de Oferta Económica — Tablas Individuales por Ítem")
            for it in res["items"]:
                sub_i = it["valorTotal"]
                iva_i = round(sub_i * iva_pct_res)
                rte_i = round(sub_i * rte_pct_res)
                tot_i = sub_i + iva_i - rte_i
                with st.container(border=True):
                    st.markdown(f"**Tabla Ítem {it['idx']}: {it['nombre']}**")
                    df_ind = pd.DataFrame([
                        {
                            "ITEM": str(it["idx"]),
                            "ITEM DE PAGO": it["nombre"],
                            "Tiempo": it["tiempoTexto"],
                            "Cant": it["cantidad"],
                            "Und": it["unidadEntrega"],
                            "Valor Unidad": fmt_cop(it["valorUnitario"]),
                            "Valor Total": fmt_cop(sub_i),
                        },
                        {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": "Valor antes de IVA", "Valor Total": fmt_cop(sub_i)},
                        {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": f"IVA ({fmt_pct(iva_pct_res)})", "Valor Total": fmt_cop(iva_i)},
                        {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": f"RETEFUENTE ({fmt_pct(rte_pct_res)})", "Valor Total": fmt_cop(rte_i)},
                        {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": "Valor total de la oferta", "Valor Total": fmt_cop(tot_i)},
                    ])
                    st.dataframe(df_ind, use_container_width=True, hide_index=True)
        else:
            st.subheader("Vista de Oferta Económica — Todos los Ítems en la Misma Tabla (Antes de Impuestos y Retenciones)")
            filas_cons = [
                {
                    "ITEM": str(it["idx"]),
                    "ITEM DE PAGO": it["nombre"],
                    "Tiempo": it["tiempoTexto"],
                    "Cant": str(it["cantidad"]),
                    "Und": it["unidadEntrega"],
                    "Valor Unidad": fmt_cop(it["valorUnitario"]),
                    "Valor Total": fmt_cop(it["valorTotal"]),
                }
                for it in res["items"]
            ]
            filas_cons.extend([
                {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": "Valor antes de IVA", "Valor Total": fmt_cop(res["subtotal"])},
                {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": f"IVA ({fmt_pct(iva_pct_res)})", "Valor Total": fmt_cop(res["iva"])},
                {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": f"RETEFUENTE ({fmt_pct(rte_pct_res)})", "Valor Total": fmt_cop(res["rte"])},
                {"ITEM": "", "ITEM DE PAGO": "", "Tiempo": "", "Cant": "", "Und": "", "Valor Unidad": "Valor total de la oferta", "Valor Total": fmt_cop(res["neto"])},
            ])
            st.dataframe(pd.DataFrame(filas_cons), use_container_width=True, hide_index=True)

    st.subheader("Totales Generales del Proyecto")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Subtotal (Antes de IVA)", fmt_cop(res["subtotal"]))
    m2.metric(f"IVA ({fmt_pct(state['p']['iva'])})", fmt_cop(res["iva"]))
    m3.metric("Total a Facturar (Con IVA)", fmt_cop(res["conIva"]))
    m4.metric("Neto Estimado (Tras Retefuente)", fmt_cop(res["neto"]))

    st.download_button(
        "⬇️ Exportar Proyecto (.json)",
        data=json.dumps(state, indent=2, ensure_ascii=False),
        file_name="cotizador_apu_datos.json",
        mime="application/json",
    )

def _on_upload_img(uploader_key: str, target_field: str):
    up_file = st.session_state.get(uploader_key)
    if up_file is not None:
        b64_str = base64.b64encode(up_file.getvalue()).decode("ascii")
        mime_str = up_file.type or "image/png"
        st.session_state["apu_state"]["cot"][target_field] = f"data:{mime_str};base64,{b64_str}"


def _on_sync_cot_field(source_key: str, field_name: str, mirror_key: str):
    val = st.session_state.get(source_key, "")
    st.session_state["apu_state"]["cot"][field_name] = val
    st.session_state[mirror_key] = val


def render_membrete_uploader(cot: dict, suffix: str):
    """Bloque reutilizable para cargar imágenes de Encabezado y Pie de página para los informes PDF."""
    with st.expander("🖼️ Configurar imágenes de Encabezado y Pie de página del PDF (Aplica a Formato A y Formato B)", expanded=True):
        u1, u2 = st.columns(2)
        with u1:
            st.markdown("**Imagen de Encabezado (Header)**")
            hdr_key = f"up_hdr_{suffix}"
            st.file_uploader(
                "Cargar imagen de encabezado (PNG, JPG)",
                type=["png", "jpg", "jpeg"],
                key=hdr_key,
                on_change=_on_upload_img,
                args=(hdr_key, "headerImgB64"),
            )
            if cot.get("headerImgB64"):
                st.image(cot["headerImgB64"], caption="Vista previa de Encabezado actual", use_container_width=True)
                if st.button("🗑️ Quitar imagen de encabezado", key=f"clr_hdr_{suffix}"):
                    cot["headerImgB64"] = ""
                    st.rerun()
            else:
                st.caption("Usando encabezado predeterminado (SEYEP SAS).")

        with u2:
            st.markdown("**Imagen de Pie de Página (Footer)**")
            ftr_key = f"up_ftr_{suffix}"
            st.file_uploader(
                "Cargar imagen de pie de página (PNG, JPG)",
                type=["png", "jpg", "jpeg"],
                key=ftr_key,
                on_change=_on_upload_img,
                args=(ftr_key, "footerImgB64"),
            )
            if cot.get("footerImgB64"):
                st.image(cot["footerImgB64"], caption="Vista previa de Pie de página actual", use_container_width=True)
                if st.button("🗑️ Quitar imagen de pie de página", key=f"clr_ftr_{suffix}"):
                    cot["footerImgB64"] = ""
                    st.rerun()
            else:
                st.caption("Usando pie de página predeterminado (SEYEP SAS).")


# ================= TAB 6: PDF PROPUESTA (FORMATO A) =================
with tabs[5]:
    st.subheader("Propuesta Técnica y Económica Completa (Formato A)")
    c = state["cot"]
    render_membrete_uploader(c, "fmt_a")

    with st.container(border=True):
        st.markdown("#### Cuadro de identificación de la oferta")
        col1, col2, col3, col4 = st.columns(4)
        c["cliente"] = col1.text_input("CLIENTE", value=c["cliente"], key="fa_cli")
        c["ofertaTitulo"] = col2.text_input("OFERTA", value=c["ofertaTitulo"], key="fa_tit")
        if st.session_state.get("fa_ref") != c["referencia"]:
            st.session_state["fa_ref"] = c["referencia"]
        col3.text_input(
            "REFERENCIA",
            key="fa_ref",
            on_change=_on_sync_cot_field,
            args=("fa_ref", "referencia", "fb_ref"),
        )
        if st.session_state.get("fa_fec") != c["fecha"]:
            st.session_state["fa_fec"] = c["fecha"]
        col4.text_input(
            "FECHA DE LA OFERTA",
            key="fa_fec",
            on_change=_on_sync_cot_field,
            args=("fa_fec", "fecha", "fb_fec"),
        )

    with st.expander("📌 1. OBJETO y 1.1. EXCLUSIONES", expanded=True):
        t1, t2 = st.columns(2)
        c["objeto"] = t1.text_area("1. OBJETO (Usa '-' al inicio de línea para viñetas)", value=c["objeto"], height=160)
        c["exclusiones"] = t2.text_area("1.1. EXCLUSIONES", value=c["exclusiones"], height=160)

    with st.expander("📚 2. DOCUMENTOS DE REFERENCIA", expanded=True):
        c["documentosRefIntro"] = st.text_input(
            "Párrafo introductorio (Sección 2)",
            value=c.get("documentosRefIntro", ""),
        )
        c["documentosRef"] = st.text_area(
            "Lista de documentos de referencia (1 línea por viñeta •)",
            value=c["documentosRef"],
            height=130,
        )

    with st.expander("🛠️ 3. OFERTA TÉCNICA (Servicios 3.1, 3.2, Insumos y Entregables)", expanded=True):
        c["ofertaTecnica"] = st.text_area(
            "Párrafo introductorio (3. OFERTA TÉCNICA)",
            value=c["ofertaTecnica"],
            height=75,
        )
        secciones_tec = c.setdefault("seccionesTecnicas", [])
        for idx_s, sec in enumerate(list(secciones_tec), start=1):
            with st.container(border=True):
                sc1, sc2 = st.columns([5, 1])
                sec["titulo"] = sc1.text_input(
                    f"Título subsección 3.{idx_s}.",
                    value=sec.get("titulo", ""),
                    key=f"sec_tit_{sec['id']}",
                )
                if sc2.button("🗑️ Eliminar 3." + str(idx_s), key=f"del_sec_tec_{sec['id']}"):
                    secciones_tec.remove(sec)
                    st.rerun()

                sec["descripcion"] = st.text_area(
                    f"3.{idx_s}. Descripción / Alcance del servicio",
                    value=sec.get("descripcion", ""),
                    height=100,
                    key=f"sec_des_{sec['id']}",
                )
                ic1, ic2 = st.columns(2)
                with ic1:
                    st.markdown(f"**3.{idx_s}.1. INSUMOS DEL CLIENTE**")
                    sec["insumosIntro"] = st.text_input(
                        "Texto introductorio de insumos",
                        value=sec.get("insumosIntro", ""),
                        key=f"sec_in_int_{sec['id']}",
                    )
                    sec["insumos"] = st.text_area(
                        "Lista de insumos del cliente (1 línea por guion '-')",
                        value=sec.get("insumos", ""),
                        height=120,
                        key=f"sec_in_lst_{sec['id']}",
                    )
                with ic2:
                    st.markdown(f"**3.{idx_s}.2. ENTREGABLES**")
                    sec["entregablesIntro"] = st.text_area(
                        "Párrafo principal de entregables",
                        value=sec.get("entregablesIntro", ""),
                        height=80,
                        key=f"sec_en_int_{sec['id']}",
                    )
                    sec["entregablesLista"] = st.text_area(
                        "Lista de entregables (1 línea por guion '-', opcional)",
                        value=sec.get("entregablesLista", ""),
                        height=95,
                        key=f"sec_en_lst_{sec['id']}",
                    )
                    sec["entregablesCierre"] = st.text_area(
                        "Párrafo final / Tiempo de entrega / Recomendación",
                        value=sec.get("entregablesCierre", ""),
                        height=80,
                        key=f"sec_en_cie_{sec['id']}",
                    )

        if st.button("+ Agregar nueva subsección técnica (3.X)", key="btn_add_sec_tec"):
            secciones_tec.append({
                "id": next_id(),
                "titulo": f"NUEVO SERVICIO TÉCNICO 3.{len(secciones_tec) + 1}",
                "descripcion": "Descripción del servicio ofertado...",
                "insumosIntro": "Para la presente oferta el cliente deberá entregar la información correspondiente a:",
                "insumos": "Información técnica del proyecto",
                "entregablesIntro": "Se entregarán los siguientes análisis recopilados en un informe técnico:",
                "entregablesLista": "Informe técnico detallado.",
                "entregablesCierre": "El tiempo de entrega es de máximo 5 días hábiles.",
            })
            st.rerun()

    with st.expander("🏢 4. ORGANIZACIÓN (4.1. Medios: Personal, Equipos, Transparencia y Ética)", expanded=False):
        o1, o2 = st.columns(2)
        with o1:
            c["orgPersonal"] = st.text_area("4.1.1. PERSONAL", value=c.get("orgPersonal", ""), height=100)
            c["orgEquiposIntro"] = st.text_input("4.1.2. EQUIPOS (Intro)", value=c.get("orgEquiposIntro", ""))
            c["orgEquipos"] = st.text_area("4.1.2. EQUIPOS (1 línea por guion '-')", value=c.get("orgEquipos", ""), height=90)
        with o2:
            c["orgEticaIntro"] = st.text_input("4.1.3. TRANSPARENCIA, ÉTICA Y CUMPLIMIENTO LEGAL (Intro)", value=c.get("orgEticaIntro", ""))
            c["orgEticaLista"] = st.text_area("4.1.3. Compromisos (1 línea por guion '-')", value=c.get("orgEticaLista", ""), height=130)
            c["orgEticaCierre"] = st.text_area("4.1.3. Párrafos de confidencialidad y cierre", value=c.get("orgEticaCierre", ""), height=110)

    with st.expander("💲 5. OFERTA ECONÓMICA, NOTAS, VALIDEZ Y FORMA DE PAGO", expanded=True):
        render_selector_modo_tabla(state, "tab_fmt_a")
        if "fa_eco_intro" not in st.session_state:
            st.session_state["fa_eco_intro"] = c.get("ofertaEconomicaIntro", "")
        c["ofertaEconomicaIntro"] = st.text_area(
            "5. OFERTA ECONÓMICA (Párrafo introductorio antes de las tablas)",
            height=65,
            key="fa_eco_intro",
        )
        c["notas"] = st.text_area("NOTAS (1 línea por viñeta •)", value=c["notas"], height=130)
        v1, v2 = st.columns(2)
        c["validez"] = v1.text_area("5.1. VALIDEZ DE LA OFERTA", value=c["validez"], height=75)
        c["formaPago"] = v2.text_area("5.2. FORMAS Y PROGRAMA DE PAGO", value=c["formaPago"], height=75)

    pdf_bytes_a = generar_pdf_formato_a(state)
    st.download_button(
        label="📥 Descargar PDF Propuesta Completa (Formato A)",
        data=pdf_bytes_a,
        file_name=f"Propuesta_{c['referencia'] or 'SEYEP'}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

# ================= TAB 7: PDF RÁPIDO (FORMATO B) =================
with tabs[6]:
    st.subheader("Cotización Rápida de 1 Página (Formato B)")
    c = state["cot"]
    render_membrete_uploader(c, "fmt_b")
    with st.container(border=True):
        render_selector_modo_tabla(state, "tab_fmt_b")

        st.markdown("#### 1. Encabezado y Datos de la Cotización")
        col1, col2, col3, col4 = st.columns(4)
        if st.session_state.get("fb_ref") != c["referencia"]:
            st.session_state["fb_ref"] = c["referencia"]
        col1.text_input(
            "Cotización / Referencia",
            key="fb_ref",
            on_change=_on_sync_cot_field,
            args=("fb_ref", "referencia", "fa_ref"),
        )
        if st.session_state.get("fb_fec") != c["fecha"]:
            st.session_state["fb_fec"] = c["fecha"]
        col2.text_input(
            "Fecha",
            key="fb_fec",
            on_change=_on_sync_cot_field,
            args=("fb_fec", "fecha", "fa_fec"),
        )
        c["senores"] = col3.text_input("Señores (Empresa / Cliente)", value=c.get("senores", ""), key="fb_sen")
        c["nit"] = col4.text_input("NIT del Cliente", value=c.get("nit", ""), key="fb_nit")

        c["trabajo"] = st.text_input(
            "Nombre del trabajo (DATOS DE LA COTIZACIÓN)",
            value=c.get("trabajo", ""),
            key="fb_tra",
        )

        st.markdown("#### 2. Alcance de la Propuesta, Observaciones y Tabla Económica")
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            c["alcanceRapido"] = st.text_area(
                "ALCANCE DE LA PROPUESTA (Párrafo principal)",
                value=c.get("alcanceRapido", ""),
                height=105,
                key="fb_alc",
            )
        with a_col2:
            c["observacionesRapido"] = st.text_area(
                "Observaciones (1 línea por viñeta •)",
                value=c.get("observacionesRapido", ""),
                height=105,
                key="fb_obs",
            )

        t_col1, t_col2, t_col3 = st.columns([2.2, 1.5, 2.3])
        with t_col1:
            c["tituloTablaRapido"] = st.text_input(
                "Título del encabezado azul de la tabla económica",
                value=c.get("tituloTablaRapido", "OFERTA ECONÓMICA RUTA ACOMETIDA No.2"),
                key="fb_tit_tab",
            )
        with t_col2:
            st.write("")
            c["mostrarReteRapido"] = st.checkbox(
                "Mostrar fila RETEFUENTE en tabla Formato B",
                value=bool(c.get("mostrarReteRapido", False)),
                key="fb_chk_rete",
            )
        with t_col3:
            c["costosNotaRapido"] = st.text_input(
                "Texto bajo fila COSTOS (Opcional — vacío por defecto)",
                value=c.get("costosNotaRapido", ""),
                key="fb_cos_nota",
            )

        st.markdown("#### 3. Condiciones de la Oferta")
        c["condicionesRapido"] = st.text_area(
            "CONDICIONES DE LA OFERTA (1 línea por ítem numerado 1., 2., ...)",
            value=c.get("condicionesRapido", ""),
            height=85,
            key="fb_cond",
        )

        pdf_bytes_b = generar_pdf_formato_b(state)
        st.download_button(
            label="📥 Descargar PDF Cotización Rápida (Formato B)",
            data=pdf_bytes_b,
            file_name=f"Cotizacion_Rapida_{c['referencia'] or 'SEYEP'}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

# ================= TAB 8: INFORME (1.1 GM: ESCENARIO EJERCICIO LINEAL) =================
with tabs[7]:
    inf = calc_informe_gm(state)
    iva_lbl_pct = f"{inf['ivaPct'] * 100:.0f}%"

    informe_html = f"""
    <style>
      .gm-sheet {{
        max-width: 920px;
        margin: 8px auto 24px auto;
        background: #ffffff;
        padding: 28px 36px 36px 36px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-family: Calibri, 'Segoe UI', Arial, sans-serif;
        color: #000000;
        font-size: 13px;
      }}
      .gm-main-title {{
        font-size: 14px;
        margin-bottom: 16px;
      }}
      .gm-sec-title {{
        font-size: 13.5px;
        font-weight: 700;
        font-style: italic;
        margin: 18px 0 8px 0;
      }}
      .gm-row {{
        display: grid;
        grid-template-columns: 68% 10% 22%;
        align-items: stretch;
        margin-bottom: 5px;
      }}
      .gm-box-peach {{
        background-color: #FCD5B4;
        border-right: 2px solid #A6A6A6;
        border-bottom: 2px solid #A6A6A6;
        padding: 4px 10px;
        font-weight: 700;
        display: flex;
        align-items: center;
      }}
      .gm-box-grey {{
        background-color: #D9D9D9;
        border-right: 2px solid #A6A6A6;
        border-bottom: 2px solid #A6A6A6;
        padding: 4px 10px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }}
      .gm-box-grey-lbl {{
        max-width: 66%;
        line-height: 1.25;
      }}
      .gm-box-grey-pct {{
        width: 34%;
        text-align: left;
        font-weight: 700;
      }}
      .gm-box-olive {{
        background-color: #C4BD97;
        border-right: 2px solid #A6A6A6;
        border-bottom: 2px solid #A6A6A6;
        padding: 6px 10px;
        font-weight: 700;
        display: flex;
        align-items: center;
      }}
      .gm-olive-lbl {{
        width: 48%;
        text-align: center;
        color: #000000;
      }}
      .gm-olive-pct {{
        width: 52%;
        text-align: center;
        color: #2F5597;
        font-weight: 700;
      }}
      .gm-val-dotted {{
        border-bottom: 1px dotted #7f7f7f;
        padding: 4px 8px;
        text-align: right;
        font-weight: 700;
        display: flex;
        align-items: flex-end;
        justify-content: flex-end;
        font-variant-numeric: tabular-nums;
      }}
      .gm-val-total-box {{
        border: 1px solid #808080;
        border-bottom: 3px double #595959;
        padding: 5px 8px;
        text-align: right;
        font-weight: 700;
        color: #0070C0;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        font-variant-numeric: tabular-nums;
        background: #ffffff;
      }}
      .gm-blue {{
        color: #0070C0;
      }}
      .gm-black {{
        color: #000000;
      }}
    </style>

    <div class="gm-sheet">
      <div class="gm-main-title">1.1 GM: <i>Escenario ejercicio lineal</i></div>

      <div class="gm-sec-title">a. Valor Venta - Perído inicial</div>

      <div class="gm-row">
        <div class="gm-box-peach">VALOR MENSUAL ANTES DE IVA</div>
        <div></div>
        <div class="gm-val-dotted gm-blue">{fmt_num_informe(inf['valorMensualAntesIva'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-peach">TOTAL MESES</div>
        <div></div>
        <div class="gm-val-dotted gm-blue">{inf['totalMesesStr']}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-peach">VALOR TOTAL ANTES DE IVA</div>
        <div></div>
        <div class="gm-val-dotted gm-blue">{fmt_num_informe(inf['valorTotalAntesIva'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-peach">IVA({iva_lbl_pct})</div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['ivaVal'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-peach">VALOR &nbsp;CON IVA</div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['valorConIva'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-sec-title" style="margin-top: 24px;">b. GROSS MARGIN- Utilidad Operacional</div>

      <div class="gm-row">
        <div class="gm-box-peach">INGRESOS OPERACIONALES (VALOR TOTAL OFERTA ANTES DE IVA -VENTA)</div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['ingresosOp'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-peach" style="padding: 7px 10px; line-height: 1.3;">
          COSTO OPERACIONALES TOTAL PROYECTO (costo venta+ gtos operaciones+admon+ amortización)
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['costoOpTotal'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-row" style="margin-top: 8px;">
        <div class="gm-box-olive">
          <span class="gm-olive-lbl">GM</span>
          <span class="gm-olive-pct">{fmt_pct_informe(inf['gmPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-total-box">{fmt_num_informe(inf['gmVal'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-sec-title" style="margin-top: 28px; margin-bottom: 14px;">
        c. Pólizas - Impuestos Departamentales, otros gastos.
      </div>

      <div class="gm-row">
        <div class="gm-box-grey">
          <span class="gm-box-grey-lbl">POLIZAS</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['polizasPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['polizasVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey" style="padding: 7px 10px;">
          <span class="gm-box-grey-lbl">OTRO GASTOS (ICA -CREE-4X100)</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['otrosGastosPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['otrosGastosVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey">
          <span class="gm-box-grey-lbl">INTERESES DE FINANCIACIÓN</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['interesesPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['interesesVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey" style="padding: 6px 10px;">
          <span class="gm-box-grey-lbl">Impuesto de Renta+ Impuesto renta Equidad CREE</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['impRentaPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['impRentaVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey" style="padding: 6px 10px;">
          <span class="gm-box-grey-lbl">OTROS IMPUESTOS DEPARTAMENTALES/MUNICIPALES</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['otrosImpPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['otrosImpVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey">
          <span class="gm-box-grey-lbl">ESTRUCTURA DIV</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['estructuraPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['estructuraVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey">
          <span class="gm-box-grey-lbl">GESTIÓN COMERCIAL</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['gestionPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">{fmt_num_informe(inf['gestionVal'])}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey" style="padding: 9px 10px;">
          <span class="gm-box-grey-lbl">AMORTIZACIÓN</span>
          <span class="gm-box-grey-pct">{fmt_pct_informe(inf['amortizacionPct'])}</span>
        </div>
        <div></div>
        <div style="padding: 4px 8px;"></div>
      </div>

      <div class="gm-row" style="margin-top: 6px; margin-bottom: 34px;">
        <div class="gm-box-olive" style="padding: 10px;">
          <span class="gm-olive-lbl">Utilidad</span>
          <span class="gm-olive-pct">{fmt_pct_informe(inf['utilidadPct'])}</span>
        </div>
        <div></div>
        <div class="gm-val-total-box" style="padding: 10px 8px;">{fmt_num_informe(inf['utilidadVal'], dash_if_zero=False)}</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey">
          <span class="gm-box-grey-lbl">PRESUPUESTO TOTAL (CLIENTE)</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">&nbsp;</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey" style="padding: 6px 10px;">
          <span class="gm-box-grey-lbl">INGRESOS OPERACIONALES (VALOR TOTAL OFERTA ANTES DE IVA -VENTA)</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">&nbsp;</div>
      </div>

      <div class="gm-row">
        <div class="gm-box-grey">
          <span class="gm-box-grey-lbl">K OFERTADO</span>
        </div>
        <div></div>
        <div class="gm-val-dotted gm-black">&nbsp;</div>
      </div>
    </div>
    """
    st.markdown(informe_html, unsafe_allow_html=True)


