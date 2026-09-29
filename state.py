"""
state.py — Gestión de estado inicial y constantes para el Cotizador APU en Streamlit.
Incluye catálogo base de Dotación y EPP (Operativos, Administrativos y por perfil RRHH)
y la estructura completa editable del Informe Formato A según plantilla corporativa SEYEP SAS.
"""
import streamlit as st

CATS = [
    "ADMINISTRACIÓN (RRHH)",
    "PERSONAL (RRHH)",
    "EQUIPOS Y SOFTWARE",
    "HERRAMIENTAS Y EPP",
    "VIÁTICOS Y ALOJAMIENTO",
    "TRANSPORTE",
    "MATERIALES Y CONSUMIBLES",
    "SERVICIOS EXTERNOS",
    "DOCUMENTACIÓN",
    "OTROS",
]

SECCIONES_RECURSOS = [
    "EQUIPOS Y SOFTWARE",
    "HERRAMIENTAS Y EPP",
    "VIÁTICOS Y ALOJAMIENTO",
    "TRANSPORTE",
    "MATERIALES Y CONSUMIBLES",
    "SERVICIOS EXTERNOS",
    "DOCUMENTACIÓN",
    "OTROS",
]

UNIDADES = ["MES", "DIA", "HORA", "UNIDAD"]

LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAABQCAYAAAD/YAtfAAAC70lEQVR4nO3Zza3UShCA0cmCwBwXmZAO8XDFAgmhQRrb9dftc6TaXvrVuL7Ne70AAAAAAAAAAAAAAAAG+fb68Wvn6d4vLKX7YAUBBuk+WEGAQboPVhBgkO6DXSkI1W+bsJ/one60hynfZajqA62eybua8NtceUP0Dlfdw5TvMlT1gVbP5F1N+G2uvCF6h6vuYcp3Gar6QKtn8q4m/DZX3hC9w1X3MOW7DFV9oNUzeVcTfpsrb4je4ap7mPJdhqo+0OqJ3Evs5p/5hqhjvPOGKybsoUT3wQrCs94gCDl/L0z3wQrCs94gCDl/L0z3wQrCs94gCDl/L0z3wQrCs94gCDl/L0z3wQrC7De88+m7ot4/YQ+CsMlE7iV282u84R1BEIRlJ3IvsZtf4w3vCIIgLDuRe4nd/BpveEcQBGHZidxL7ObXeMM7giAIy86UXU34bSJ38clbM/+23yJJ98FmzvH9pyAUfYSZ/96EPUx4Q4nuo82a3zEQBEF44m9xS/fhZsyfGAiCIDzxt7il+3ij5+8YCIIgPPG3uKX7gCPn3xhEB+GOKx/FSh9SdRCi/vZKbyjRfcSZMRCEOoKwie5DzoyBINQRhE10H3NmDAShjiBsovugM2MgCHUEYRPdR50ZA0GoIwib6D7szBgIQh1B2ET3cWfGQBDqCMImug88MwaCUEcQNtF95JkxEIQ6grCJ7kPPjMGdIET/N0x4w6pHO2EPgjBk7sRAEARBEE7qPvjMGAiCIAjCSd1HnxkDQRAEQTip+/AzYyAIgiAIJ3Uff2YMJv1fBlhCdwAyYyAIcFJ3BDJjIAhwUncIMmMgCHDSzjEQBDhp5xgIApy0cwwEAU7aOQZ3glD5RmP+N7HX/oGdY3Bnod0fgjHH7kFYaaHdH4Ixx85BWG2h3R+CMceuQVhxod0fgjHHjkFYdaHd7zbm2C0I3cu8s9Dudxtz7BSE7kW2LRRWtnMMBAFO2jkGggAAAAAAAAAAAAAAAAB9vgAQtwYk5L6KAAAAAABJRU5ErkJggg=="


def get_catalogo_base_dotacion() -> list[dict]:
    """
    Catálogo maestro de Dotación y EPP basado en el cuadro de Excel:
    DETALLE - EPP - COLABORADORES OPERATIVOS / ADMINISTRATIVOS.
    """
    return [
        {"id": 2001, "nombre": "Camisas", "precioUnitario": 80000, "cantOperativo": 4, "cantAdministrativo": 4, "descripcion": "Camisa Terreno", "esCarne": False},
        {"id": 2002, "nombre": "Camisetas", "precioUnitario": 7000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Camiseta", "esCarne": False},
        {"id": 2003, "nombre": "Chaqueta", "precioUnitario": 50000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Chaqueta", "esCarne": False},
        {"id": 2004, "nombre": "Pantalón", "precioUnitario": 24500, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Pantalón Jean", "esCarne": False},
        {"id": 2005, "nombre": "Botas", "precioUnitario": 125000, "cantOperativo": 1, "cantAdministrativo": 1, "descripcion": "Bota Dieléctrica tipo ingeniero", "esCarne": False},
        {"id": 2006, "nombre": "Gafas", "precioUnitario": 11000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Gafa de seguridad gris ref. AR-277 G", "esCarne": False},
        {"id": 2007, "nombre": "Gafa de seguridad gris ref. AR-277 G", "precioUnitario": 11000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Gafa de seguridad gris ref. AR-277 G", "esCarne": False},
        {"id": 2008, "nombre": "Mascarilla", "precioUnitario": 2365, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Mascarilla desechable ó Respirador ref.1830", "esCarne": False},
        {"id": 2009, "nombre": "Casco", "precioUnitario": 45000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Casco de seguridad dielectrico con racthet certificado ref. 10-096AR", "esCarne": False},
        {"id": 2010, "nombre": "Visor Anti arco", "precioUnitario": 200000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Visor Anti arco", "esCarne": False},
        {"id": 2011, "nombre": "Protector auditivo desechable en esponja tipo NORTH", "precioUnitario": 12000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Protector auditivo desechable en esponja tipo NORTH", "esCarne": False},
        {"id": 2012, "nombre": "Protector auditivo de copa", "precioUnitario": 11000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Protector auditivo de Copa", "esCarne": False},
        {"id": 2013, "nombre": "Guantes", "precioUnitario": 9625, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Guante en vaqueta tipo ingeniero reforzado en la palma y dedos", "esCarne": False},
        {"id": 2014, "nombre": "Bota Pantanera", "precioUnitario": 45000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Bota Pantanera", "esCarne": False},
        {"id": 2015, "nombre": "Impermeables", "precioUnitario": 47000, "cantOperativo": 0, "cantAdministrativo": 0, "descripcion": "Impermeables", "esCarne": False},
        {"id": 2016, "nombre": "Carné", "precioUnitario": 50000, "cantOperativo": 1, "cantAdministrativo": 1, "descripcion": "Carné", "esCarne": True},
    ]


def build_dotacion_perfil_from_catalogo(catalogo: list[dict], tipo: str = "operativo") -> dict[int, float]:
    """Construye el diccionario {id_dotacion: cantidad_anual} según el tipo ('operativo' o 'administrativo')."""
    key = "cantOperativo" if tipo == "operativo" else "cantAdministrativo"
    return {int(item["id"]): float(item.get(key, 0) or 0) for item in catalogo}


def get_default_secciones_tecnicas() -> list[dict]:
    """Subsecciones predeterminadas de la sección 3. OFERTA TÉCNICA (3.1, 3.2, ...)."""
    return [
        {
            "id": 3001,
            "titulo": "ESTUDIOS SIMPLIFICADOS DE CONEXIÓN",
            "descripcion": (
                "El estudio entregado se rige bajo los requisitos del CNO2233 para los GD de hasta "
                "990kW para nivel de tensión 2, en el que se realizarán todos los análisis requeridos "
                "en el acuerdo bajo los lineamientos establecidos en el mismo."
            ),
            "insumosIntro": "Para la presente oferta el cliente deberá entregar la información correspondiente a:",
            "insumos": (
                "Generación proyectada mensual del primer año y anual de los 30 años siguientes\n"
                "Insumos suministrados por el OR (equivalentes de red, diagrama del circuito, información de la red, información de protecciones, y en general todo lo que el OR entregue para la simulación del sistema)\n"
                "Información detallada del sistema a instalar, tal como las fichas técnicas, ubicación del proyecto, nombre del proyecto, diagramas de media y baja del diseño del GD"
            ),
            "entregablesIntro": (
                "Se correrá un flujo de carga AC balanceado para condiciones normales de operación, "
                "un estudio de corto circuito trifásico y monofásico, se entregarán los análisis citados "
                "a continuación recopilados en un informe técnico:"
            ),
            "entregablesLista": (
                "Análisis del flujo de carga y perfiles de tensión.\n"
                "Análisis de pérdidas.\n"
                "Análisis de corto circuito\n"
                "Análisis de Armónicos\n"
                "Estudio de coordinación de protecciones."
            ),
            "entregablesCierre": (
                "El tiempo de entrega del estudio es de máximo 5 días hábiles a partir de que el cliente "
                "suministre la información correspondiente."
            ),
        },
        {
            "id": 3002,
            "titulo": "ESTUDIOS DE PREFACTIBILIDAD",
            "descripcion": (
                "El estudio consiste en el análisis previo a un estudio simplificado de conexión, el "
                "cual se rige bajo los requisitos del CNO2223 para los GD de hasta 990kW para nivel "
                "de tensión 2, en el que se realizarán todos los análisis requeridos en el acuerdo bajo "
                "los lineamientos establecidos en el mismo.\n"
                "Este estudio es un análisis resumido que se realiza con el objetivo de analizar si el "
                "punto escogido es óptimo para la conexión de un GD antes de realizar todos los "
                "análisis detallados para entregar al OR, y permitirá al cliente tener conocimiento si "
                "es viable continuar con la evaluación técnica completa para el proyecto o si lo mejor "
                "es descartar el proyecto y buscar un nuevo terreno, antes de realizar una inversión "
                "considerable."
            ),
            "insumosIntro": "Para la presente oferta el cliente deberá entregar la información correspondiente a:",
            "insumos": (
                "Insumos suministrados por el OR (equivalentes de red, diagrama del circuito, información de la red, información de protecciones, y en general todo lo que el OR entregue para la simulación del sistema)\n"
                "Información detallada del sistema a instalar, tal como las fichas técnicas, ubicación del proyecto, nombre del proyecto, diagramas de media y baja del diseño del GD"
            ),
            "entregablesIntro": (
                "Se correrá un flujo de carga AC balanceado para condiciones normales de operación "
                "y se entregará un informe reducido en el que se le indicará al cliente si el punto es "
                "óptimo para construir un GD en cuanto a perfiles de tensión y cargabilidad de las "
                "líneas del circuito, se le indicará al cliente en dicho informe la cantidad de proyectos "
                "de hasta 990kW que se pueden construir, y se realizarán recomendaciones si es "
                "necesario en cuanto a repotenciación de líneas para que los proyectos sean viables, "
                "en caso de que se requiera."
            ),
            "entregablesLista": "",
            "entregablesCierre": (
                "Como recomendación inicial para el desarrollo del Estudio de Conexión (ESC), se "
                "sugiere la ejecución previa de un estudio de prefactibilidad. Este análisis preliminar "
                "permitirá evaluar anticipadamente los conceptos de protecciones y la disponibilidad "
                "de la red, así como los perfiles de tensión y la calidad de operación, garantizando así "
                "la optimización de recursos y la mitigación de riesgos técnicos en las siguientes "
                "etapas del proyecto."
            ),
        },
    ]


INTRO_ECO_INDIVIDUAL = (
    "A continuación, se presentarán por separado las tablas de costos para cada ítem "
    "ofertado, ya que cada ítem se manejará con una OC separada."
)

INTRO_ECO_CONSOLIDADA = (
    "A continuación, se presenta la tabla de costos con los ítems ofertados antes de "
    "impuestos y retenciones:"
)


def get_default_cot() -> dict:
    """Contenido predeterminado completo para los informes Formato A y Formato B."""
    return {
        "cliente": "VOLTNOVA",
        "ofertaTitulo": "ESTUDIO DE CONEXIÓN ELÉCTRICA SISTEMA SOLAR",
        "referencia": "260923-0904",
        "fecha": "Septiembre 23 2026",
        "modoTablaOferta": "individual",  # "individual" (tablas separadas por ítem) o "consolidada" (todos en la misma tabla)
        # 1. OBJETO
        "objeto": (
            "La presente oferta, constituye la mejor oferta técnica/económica que Servicios "
            "Eléctricos Y Electrónica de Potencia S.A.S, en adelante SEYEP, presenta a la "
            "empresa VOLTNOVA, en adelante El Cliente, para los siguientes servicios:\n"
            "- Estudios simplificados de conexión\n"
            "- Estudios de prefactibilidad\n"
            "Los servicios anteriormente mencionados son válidos para proyectos de hasta "
            "990kW, para nivel 2 de energía, a continuación, se explicará el alcance de cada "
            "servicio y sus condiciones técnicas y comerciales."
        ),
        # 1.1. EXCLUSIONES
        "exclusiones": (
            "El estudio abarca la coordinación de protecciones hasta N-1, si en el análisis se "
            "detecta que se deben coordinar los elementos aguas arriba del operador de red, el "
            "equipo de SEYEP emitirá un comunicado al cliente para reevaluar el costo del "
            "estudio de coordinación de protecciones.\n"
            "Los análisis y estudios acá descritos son únicamente para las condiciones "
            "establecidas, para cambios en las condiciones para la realización de un estudio se "
            "deberá considerar una cotización puntual para el caso."
        ),
        # 2. DOCUMENTOS DE REFERENCIA
        "documentosRefIntro": (
            "Para la realización de los trabajos se tendrá en cuenta las siguientes disposiciones "
            "legislativas y documentos de referencia:"
        ),
        "documentosRef": (
            "Los manuales de los equipos a instalar.\n"
            "Acuerdo CNO 2233 con las recomendaciones de protecciones y sus anexos.\n"
            "Resolución CREG 174 del 2021.\n"
            "Los manuales de los procedimientos establecidos por el operador de red para este tipo de trámites.\n"
            "El reglamento técnico RETIE."
        ),
        # 3. OFERTA TÉCNICA
        "ofertaTecnica": (
            "En el presente documento se explicará claramente el alcance de cada servicio que "
            "SEYEP oferta para el cliente, con los insumos que el cliente debe entregar, el alcance "
            "de cada ítem y los entregables que se dejarán para cada caso."
        ),
        "seccionesTecnicas": get_default_secciones_tecnicas(),
        # 4. ORGANIZACIÓN
        "organizacion": "",
        "orgPersonal": (
            "SEYEP dispone actualmente de personal altamente calificado y avalado por años de experiencia.\n"
            "SEYEP se reserva el derecho de emplear cuanto personal técnico considere oportuno para la realización óptima de los trabajos sin costo añadido para el cliente."
        ),
        "orgEquiposIntro": "Para la realización del trabajo se utilizarán los siguientes equipos:",
        "orgEquipos": (
            "Un (1) computador portátil.\n"
            "Herramientas básicas.\n"
            "Licencias de software especializados requeridos."
        ),
        "orgEticaIntro": "SEYEP como empresa y su personal en concreto, asumen un compromiso de:",
        "orgEticaLista": (
            "Transparencia: Asegurando independencia, imparcialidad y ausencia de conflictos de interés en sus acciones y decisiones como parte de aseguramiento de los servicios prestados.\n"
            "Ética: Asegurando la implementación y cumplimiento del Código Ético organizacional, incluyendo en ello la prevención de la corrupción, el lavado de activos, el soborno nacional y transnacional y la financiación del terrorismo.\n"
            "Protección de datos: Garantizando el control y confidencialidad de la información personal del cliente, proveedores y partes interesadas en la gestión, acorde con lo establecido en la ley.\n"
            "Respecto a los Recursos Humanos: Mediante una gestión basada en el respeto a la individualidad y la prevención de cualquier forma de discriminación, confidencialidad de los datos, informes y documentos y certificados del cliente o proporcionados por el cliente."
        ),
        "orgEticaCierre": (
            "El acceso a equipos y programas informáticos, la distribución de informes, certificados y el compromiso de confidencialidad de los responsables y consultores encargados del trabajo, estarán comprendidos en el alcance de la confidencialidad.\n\n"
            "Todos los datos e informes manejados y originados en el transcurso de los trabajos sólo serán facilitados a aquellas personas u organismos previamente designados por el cliente bajo estricto control."
        ),
        # 5. OFERTA ECONÓMICA
        "ofertaEconomicaIntro": (
            "A continuación, se presentarán por separado las tablas de costos para cada ítem "
            "ofertado, ya que cada ítem se manejará con una OC separada."
        ),
        "notas": (
            "Todos los valores están en pesos colombianos.\n"
            "Estos valores son para un solo estudio de conexión, en caso de que el cliente realice una orden de compra por más de 5 estudios, se otorgará un descuento del 10%.\n"
            "Estos valores son para un solo estudio de prefactibilidad, en caso de que el cliente realice una orden de compra por más de 10 estudios, se otorgará un descuento del 10%.\n"
            "Para los casos en los que se realicen orden de compra de más de un estudio, el cliente deberá indicar la prioridad de cada uno para darle mayor prontitud a los que el cliente requiera con mayor urgencia.\n"
            "Los precios de esta oferta ya incluyen las asesorías remotas, reuniones aclaratorias, reuniones con el OR y los reprocesos que el OR solicite."
        ),
        "validez": "La presente oferta es válida por 30 días calendario más unos días de gracia",
        "formaPago": (
            "El pago se realizará máximo a 15 días calendario después de la entrega y aprobación "
            "de la recepción por parte del cliente del estudio."
        ),
        # FORMATO B (Rápido)
        "senores": "ERCO ENERGIA S.A.S",
        "nit": "900570286-9",
        "trabajo": "Instalación de cargador eléctrico vehicular para proyecto ME Harvey Martinez",
        "alcanceRapido": (
            "La propuesta contempla la instalación de un cargador eléctrico vehicular, el cual suministrará el cliente, "
            "basado en la ruta propuesta en el pdf. No se contempla el suministro de los materiales necesarios para la "
            "instalación."
        ),
        "observacionesRapido": (
            "Esta cotización no contempla actividades de obra civil.\n"
            "Para la coordinación de los trabajos, el cliente deberá informar con una anticipación de al menos "
            "una semana, para la requisición de materiales y la coordinación del personal."
        ),
        "tituloTablaRapido": "OFERTA ECONÓMICA RUTA ACOMETIDA No.2",
        "mostrarReteRapido": False,
        "costosNotaRapido": "",
        "condicionesRapido": (
            "Los valores son en COP\n"
            "La oferta tiene una validez de 30 días calendario, y solo es válida para el punto específico de instalación."
        ),
        "web": "www.seyep.com.co",
        "tel": "320 9398839",
        "ig": "@seyepsas",
        "headerImgB64": "",
        "footerImgB64": "",
    }


def get_catalogo_base_recursos() -> list[dict]:
    return [
        # ================= 1. EQUIPOS Y SOFTWARE =================
        {"id": 1003, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "ALQUILERES Y SUBCONTRATOS", "nombre": "Celular Plan 1", "descripcion": "", "unidadMedida": "UN", "costo": 43000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1004, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "ALQUILERES Y SUBCONTRATOS", "nombre": "Celular Plan 2", "descripcion": "", "unidadMedida": "UN", "costo": 0, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1005, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "ALQUILERES Y SUBCONTRATOS", "nombre": "Celular Plan 3", "descripcion": "", "unidadMedida": "UN", "costo": 0, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1006, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "ALQUILERES Y SUBCONTRATOS", "nombre": "Celular Plan Ilimitado + datos 4 GB", "descripcion": "Aún no se contrata plan celular", "unidadMedida": "UN", "costo": 0, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1007, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "ALQUILERES Y SUBCONTRATOS", "nombre": "Equipo celular", "descripcion": "Sin costo por ahora", "unidadMedida": "EQ", "costo": 1000000, "meses": 24, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1008, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Argolladora", "descripcion": "Los propios por ahora, valores estimados", "unidadMedida": "EQ", "costo": 1400000, "meses": 72, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1009, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Maquina de laminación", "descripcion": "Los propios por ahora, valores estimados", "unidadMedida": "EQ", "costo": 1200000, "meses": 72, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1010, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Inkjet", "descripcion": "Los propios por ahora, valores estimados", "unidadMedida": "EQ", "costo": 900000, "meses": 72, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1011, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Laser", "descripcion": "Aún no aplica", "unidadMedida": "EQ", "costo": 6500000, "meses": 72, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1012, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Impresora B/N", "descripcion": "Pendiente por comprar", "unidadMedida": "EQ", "costo": 4500000, "meses": 72, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1013, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Computador portátil", "descripcion": "Los propios por ahora, valores estimados", "unidadMedida": "EQ", "costo": 3000000, "meses": 72, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1014, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Modem Internet", "descripcion": "", "unidadMedida": "EQ", "costo": 0, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1015, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Impresora multifuncional", "descripcion": "", "unidadMedida": "UN", "costo": 0, "meses": 10, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1016, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia Project", "descripcion": "", "unidadMedida": "EQ", "costo": 7200000, "meses": 36, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1017, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia Autocad", "descripcion": "", "unidadMedida": "EQ", "costo": 0, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1018, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia NEPLAN", "descripcion": "", "unidadMedida": "EQ", "costo": 0, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1019, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia ETAP", "descripcion": "", "unidadMedida": "EQ", "costo": 0, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1020, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia Digsilent", "descripcion": "", "unidadMedida": "EQ", "costo": 1000000, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1021, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia Office", "descripcion": "", "unidadMedida": "EQ", "costo": 0, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1022, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia software contable", "descripcion": "", "unidadMedida": "EQ", "costo": 2500000, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1023, "seccion": "EQUIPOS Y SOFTWARE", "subgrupo": "AMORTIZABLES", "nombre": "Licencia Omicron", "descripcion": "", "unidadMedida": "EQ", "costo": 0, "meses": 12, "mtto": 0.0, "factorUso": 1.0},
        # ================= 2. HERRAMIENTAS Y EPP =================
        {"id": 1024, "seccion": "HERRAMIENTAS Y EPP", "subgrupo": "AMORTIZABLES", "nombre": "Herramientas", "descripcion": "", "unidadMedida": "EQ", "costo": 185000, "meses": 18, "mtto": 0.0, "factorUso": 1.0},
        # ================= 3. VIÁTICOS Y ALOJAMIENTO =================
        {"id": 1025, "seccion": "VIÁTICOS Y ALOJAMIENTO", "subgrupo": "", "nombre": "Dieta 1", "descripcion": "Ciudad Pequeña (3 a $18.000 C/u)", "unidadMedida": "DIA", "costo": 54000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1026, "seccion": "VIÁTICOS Y ALOJAMIENTO", "subgrupo": "", "nombre": "Dieta 2", "descripcion": "Ciudad Mediana (3 a $21.000 C/u)", "unidadMedida": "DIA", "costo": 63000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1027, "seccion": "VIÁTICOS Y ALOJAMIENTO", "subgrupo": "", "nombre": "Dieta 3", "descripcion": "Ciudad Grande (3 a $25.000 C/u)", "unidadMedida": "DIA", "costo": 75000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1028, "seccion": "VIÁTICOS Y ALOJAMIENTO", "subgrupo": "", "nombre": "Hospedaje", "descripcion": "Valor por dia", "unidadMedida": "DIA", "costo": 90000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1029, "seccion": "VIÁTICOS Y ALOJAMIENTO", "subgrupo": "", "nombre": "Arriendo", "descripcion": "", "unidadMedida": "MES", "costo": 1050000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        # ================= 4. TRANSPORTE =================
        {"id": 1030, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "Gastos de transporte (peajes y gasolina)", "descripcion": "", "unidadMedida": "GLB", "costo": 800000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1031, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "Peajes", "descripcion": "Se calculan dependiendo del desplazamiento", "unidadMedida": "GLB", "costo": 0, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1032, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Cali", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 400000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1033, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Barranquilla", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 700000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1034, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Pereira", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 400000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1035, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Bogota", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 400000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1036, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Popayan", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 1300000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1037, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Bucaramanga", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 800000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1038, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Cucuta", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 700000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1039, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Cartagena", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 700000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1040, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "TKT Medellín - Riohacha", "descripcion": "Ida y regreso - Promedio", "unidadMedida": "UN", "costo": 900000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1041, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "Transporte equipos", "descripcion": "fletes, depende del trayecto, se pondrá un promedio", "unidadMedida": "GLB", "costo": 400000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1042, "seccion": "TRANSPORTE", "subgrupo": "", "nombre": "Gastos transporte", "descripcion": "Taxis para el desplazamiento", "unidadMedida": "GLB", "costo": 200000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        # ================= 5. MATERIALES Y CONSUMIBLES =================
        {"id": 1043, "seccion": "MATERIALES Y CONSUMIBLES", "subgrupo": "", "nombre": "Papeleria Oferta", "descripcion": "", "unidadMedida": "GLB", "costo": 12000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1044, "seccion": "MATERIALES Y CONSUMIBLES", "subgrupo": "", "nombre": "Papeleria", "descripcion": "", "unidadMedida": "GLB", "costo": 300000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        # ================= 6. SERVICIOS EXTERNOS =================
        {"id": 1045, "seccion": "SERVICIOS EXTERNOS", "subgrupo": "", "nombre": "Alquiler Omicron", "descripcion": "", "unidadMedida": "DIA", "costo": 2000000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1046, "seccion": "SERVICIOS EXTERNOS", "subgrupo": "", "nombre": "Ingeniero para pruebas", "descripcion": "Andrés", "unidadMedida": "DIA", "costo": 4000000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        # ================= 8. OTROS =================
        {"id": 1047, "seccion": "OTROS", "subgrupo": "", "nombre": "Costo de Rotatividad de Personal", "descripcion": "2,8% - Dotación, Capacitación, exámenes ingreso/egreso (7 mensuales por cada 250)", "unidadMedida": "MES", "costo": 6231, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1048, "seccion": "OTROS", "subgrupo": "", "nombre": "Peaje", "descripcion": "Gabriel recomienda relacionar 1 indemnización", "unidadMedida": "GLB", "costo": 9000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1049, "seccion": "OTROS", "subgrupo": "", "nombre": "Costos x Ausentismo", "descripcion": "0,5% - 368 horas/mes de 92, depende de factores de salud, promedio mensual 212 H/H mes", "unidadMedida": "MES", "costo": 72858, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
        {"id": 1050, "seccion": "OTROS", "subgrupo": "", "nombre": "Imprevistos", "descripcion": "", "unidadMedida": "GLB", "costo": 250000, "meses": 1, "mtto": 0.0, "factorUso": 1.0},
    ]


def get_default_state() -> dict:
    cat_dotacion = get_catalogo_base_dotacion()
    return {
        "uid": 3100,
        "p": {
            "proyecto": {
                "nombre": "ESTUDIO DE CONEXIÓN ELÉCTRICA SISTEMA SOLAR",
                "contratante": "VOLTNOVA",
                "contratista": "SEYEP SAS",
                "plazoMeses": 1,
                "anticipoPct": 0.40,
                "formaPagoDias": 15,
            },
            "iva": 0.19,
            "rte": 0.11,
            "aplicaRte": True,
            "salMin": 1750905,
            "auxTrans": 249095,
            "factDirecto": 0.43,
            "factSub": 0.57,
            "factAlto": 0.567,
            "factIntegral": 0.41,
            "arl": {
                1: 0.00522,
                2: 0.01044,
                3: 0.02436,
                4: 0.0435,
                5: 0.0696,
            },
            "diasMes": 22,
            "horasDia": 8,
            "margen": 0.17,
            "ica": 0.00966,
            "aplicaIca": False,
            "reteIva": 0.0285,
            "aplicaReteIva": False,
            "reteIca": 0.00966,
            "aplicaReteIca": False,
            "cuatroPorMil": 0.004,
            "aplica4x1000": True,
            "dotacionMes": 41250,
            "dotacionMesesAnio": 12,
        },
        "dotacionCatalogo": cat_dotacion,
        "rrhh": [
            {
                "id": 1001,
                "nombre": "Jefe de Proyectos",
                "salario": 4000000,
                "auxFijo": 0,
                "bono": 0,
                "contrato": "directo",
                "prestacional": True,
                "arlNivel": 2,
                "dotacion": False,
                "tipoDotacion": "administrativo",
                "dotacionMeses": 12,
                "dotacionCantidades": build_dotacion_perfil_from_catalogo(cat_dotacion, "administrativo"),
                "util": 1.0,
            },
            {
                "id": 1002,
                "nombre": "Técnico de Campo",
                "salario": 1750905,
                "auxFijo": 0,
                "bono": 0,
                "contrato": "directo",
                "prestacional": True,
                "arlNivel": 4,
                "dotacion": True,
                "tipoDotacion": "operativo",
                "dotacionMeses": 12,
                "dotacionCantidades": build_dotacion_perfil_from_catalogo(cat_dotacion, "operativo"),
                "util": 1.0,
            },
        ],
        "recursos": get_catalogo_base_recursos(),
        "items": [
            {
                "id": 1005,
                "nombre": "ESTUDIO DE CONEXIÓN PARA SFV 990 kW - NIVEL II",
                "cantidad": 1,
                "unidadEntrega": "GLB",
                "tiempoTexto": "5 días hábiles",
                "redondear": False,
                "modoRedondeo": "valor",
                "valorRedondeado": 0,
                "multiploRedondeo": 10000,
                "direccionRedondeo": "cercano",
                "filas": [],
            },
            {
                "id": 1006,
                "nombre": "ESTUDIO DE PREFACTIBILIDAD PARA SFV 990 kW - NIVEL II",
                "cantidad": 1,
                "unidadEntrega": "GLB",
                "tiempoTexto": "3 días hábiles",
                "redondear": False,
                "modoRedondeo": "valor",
                "valorRedondeado": 0,
                "multiploRedondeo": 10000,
                "direccionRedondeo": "cercano",
                "filas": [],
            },
        ],
        "activeItem": 1005,
        "cot": get_default_cot(),
    }


def normalize_loaded_state(raw_state: dict) -> dict:
    """
    Normaliza y valida un diccionario de estado (cargado desde un archivo .json o en memoria),
    restaurando claves enteras en diccionarios de ARL y dotación y completando valores por defecto.
    """
    defaults = get_default_state()
    if not isinstance(raw_state, dict):
        return defaults

    state = raw_state
    state.setdefault("uid", defaults["uid"])

    p_def = defaults["p"]
    p = state.setdefault("p", p_def)
    proy_def = p_def["proyecto"]
    proy = p.setdefault("proyecto", proy_def)
    for k, v in proy_def.items():
        proy.setdefault(k, v)

    for k, v in p_def.items():
        if k != "proyecto" and k != "arl":
            p.setdefault(k, v)

    raw_arl = p.get("arl", p_def["arl"])
    if isinstance(raw_arl, dict):
        p["arl"] = {int(k): float(v or 0.0) for k, v in raw_arl.items()}
    else:
        p["arl"] = dict(p_def["arl"])

    cot_defaults = get_default_cot()
    cot = state.setdefault("cot", {})
    for k, v in cot_defaults.items():
        cot.setdefault(k, v)

    if "dotacionCatalogo" not in state or not state["dotacionCatalogo"]:
        state["dotacionCatalogo"] = get_catalogo_base_dotacion()

    cat_dot = state["dotacionCatalogo"]
    for r in state.get("rrhh", []):
        r.setdefault("tipoDotacion", "operativo" if r.get("dotacion") else "administrativo")
        r.setdefault("dotacionMeses", int(p.get("dotacionMesesAnio", 12) or 12))
        if "dotacionCantidades" not in r or not isinstance(r["dotacionCantidades"], dict):
            r["dotacionCantidades"] = build_dotacion_perfil_from_catalogo(
                cat_dot, r["tipoDotacion"] if r["tipoDotacion"] in ("operativo", "administrativo") else "operativo"
            )
        else:
            norm_cant = {int(k): float(v or 0) for k, v in r["dotacionCantidades"].items()}
            for item in cat_dot:
                norm_cant.setdefault(int(item["id"]), 0.0)
            r["dotacionCantidades"] = norm_cant

    recs = state.get("recursos", [])
    if not recs:
        state["recursos"] = get_catalogo_base_recursos()
    for r in state.get("recursos", []):
        if not r.get("seccion") or r.get("seccion") == "EQUIPOS":
            r["seccion"] = "EQUIPOS Y SOFTWARE"
        elif r.get("seccion") == "SERVICIOS EXTERNOS/INTERNOS":
            r["seccion"] = "SERVICIOS EXTERNOS"
        r.setdefault("subgrupo", "")
        r.setdefault("descripcion", "")
        r.setdefault("unidadMedida", "UN")

    if "items" not in state or not isinstance(state["items"], list) or len(state["items"]) == 0:
        state["items"] = defaults["items"]
    state.setdefault("activeItem", state["items"][0]["id"])

    return state


def init_session_state():
    if "apu_state" not in st.session_state:
        st.session_state["apu_state"] = get_default_state()
    else:
        st.session_state["apu_state"] = normalize_loaded_state(st.session_state["apu_state"])


def next_id() -> int:
    st.session_state["apu_state"]["uid"] += 1
    return st.session_state["apu_state"]["uid"]


if __name__ == "__main__":
    try:
        st.warning(
            "⚠️ Estás ejecutando `state.py` directamente. "
            "Para abrir el Cotizador APU debes ejecutar **`app.py`** "
            "(y verificar que cada archivo `.py` tenga su propio contenido y esté guardado con Ctrl + S)."
        )
    except Exception:
        pass

