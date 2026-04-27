import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data_loader import (
    load_data, get_categorias, get_jugadores_por_categoria,
    get_vars_rendimiento, get_vars_pfza, get_available_months,
    filter_by_month_smart
)

# ---- Funciones de utilidad -------------------------------------------------
def _filtrar_mes_estricto(df, mes_str):
    """
    Filtra DataFrame por mes YYYY-MM usando SIEMPRE la columna 'Fecha'.
    Versión corregida que evita confundir 'Fecha de nacimiento' con 'Fecha'.
    """
    # REGLA 1: Si existe columna llamada exactamente 'Fecha', usarla siempre
    if 'Fecha' in df.columns:
        fecha_col = 'Fecha'
    else:
        # Fallback: buscar columna de fecha que NO sea de nacimiento
        fecha_col = None
        for col in df.columns:
            col_lower = col.lower().strip()
            # Excluir explícitamente columnas de nacimiento
            if 'nacimiento' in col_lower or 'nac' in col_lower:
                continue
            if any(kw in col_lower for kw in ['fecha', 'date', 'mes', 'period']):
                fecha_col = col
                break

    if fecha_col is None:
        return df.iloc[0:0]   # DataFrame vacío del mismo schema

    try:
        periodos = (
            pd.to_datetime(df[fecha_col], errors='coerce')
            .dt.to_period('M')
            .astype(str)
        )
        df_filtrado = df[periodos == mes_str].copy()
        return df_filtrado
    except Exception:
        return df.iloc[0:0]

def _norm_cat(c):
    """
    Normaliza categoría igual que data_loader._normalizar_categoria.
    DEBE ser idéntica para que los filtros coincidan.
    """
    if c is None or (isinstance(c, float) and pd.isna(c)):
        return ''
    return ' '.join(str(c).strip().split()).title()

def calcular_swc_jugador(pre, post, sd_grupo):
    """
    Calcula SWC y magnitud para un jugador.
    Retorna dict o None si faltan datos.
    """
    if pd.isna(pre) or pd.isna(post) or pd.isna(sd_grupo) or sd_grupo == 0:
        return None
    SWC = 0.2 * sd_grupo
    TE  = sd_grupo * np.sqrt(1 - ICC)
    cambio = post - pre
    es     = cambio / sd_grupo
    return {
        'pre': pre, 'post': post,
        'cambio': cambio,
        'es': es,
        'SWC': SWC,
        'TE': TE,
        'sd_grupo': sd_grupo,
        'magnitud': get_magnitude_label(es),
        'color': get_magnitude_color(es),
        'color_texto': get_magnitude_text_color(es),
    }

def get_var_series(data, var, categoria=None, dni=None, mes=None):
    """
    Obtiene la serie de una variable desde rendimiento o pfza.
    Si mes=None devuelve toda la historia.
    """
    # Usar variables dinámicas como en mbd_page.py
    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    sheet = 'rendimiento' if var in vars_rend else 'pfza'
    df = data[sheet].copy()
    if var not in df.columns:
        return pd.Series(dtype=float)
    if categoria:
        cat_norm = _norm_cat(categoria)
        df = df[df['Categoria'].apply(_norm_cat) == cat_norm]
    if dni:
        df = df[df['DNI'] == dni]
    if mes:
        df = filter_by_month_smart(df, mes, categoria)
    return df[var].dropna()


# ---- Constantes ---------------------------------------------------------------
ICC = 0.90

# ── MAPEO: nombre_en_dropdown → nombre_exacto_en_columna_excel ─────────────
# IMPORTANTE: los VALUES del dropdown deben coincidir EXACTAMENTE 
# con los nombres de columna del DataFrame
# Verificar con el Prompt 1 cuáles son los nombres reales y ajustar aquí

# ── MAPEO: nombre_en_dropdown → nombre_exacto_en_columna_excel ─────────────
# IMPORTANTE: los VALUES del dropdown deben coincidir EXACTAMENTE 
VARS_RENDIMIENTO_EXCEL = ['VO2 max', 'Vmax', 'F0', 'V0', 'Pmax', 'RF', 'DRF']

VARS_PFZA_EXCEL = [
    'Fuerza', 'Potencia Pico', 'Altura Salto',
    'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250'
]

# Nombres para mostrar en dropdown (label) — pueden ser diferentes al Excel
DISPLAY_NAMES = {
    'VO2 max':       'VO2 max',
    'F0':            'F0',
    'V0':            'V0',
    'Pmax':          'Pmax',
    'Vmax':          'Vmax',
    'RF':            'RF',
    'DRF':           'DRF',
    'Fuerza':        'Fuerza CMJ',
    'Potencia Pico': 'Pot. Pico',
    'Altura Salto':  'Altura Salto',
    'Fuerza IMTP':   'F. IMTP',
    'RFD Dec':       'RFD Dec',
    'RFD 100':       'RFD 100',
    'RFD 150':       'RFD 150',
    'RFD 250':       'RFD 250',
}
TODAS_VARS = VARS_RENDIMIENTO_EXCEL + VARS_PFZA_EXCEL

# ---- Helpers de color ---------------------------------------------------------
def get_magnitude_label(es):
    """Etiqueta de magnitud según Hopkins (en unidades SD)."""
    a = abs(es)
    if a < 0.2:   return 'Trivial'
    if a < 0.6:   return 'Small'
    if a < 1.2:   return 'Moderate'
    return 'Large'

def get_magnitude_color(es):
    """
    Color según dirección y magnitud (Hopkins).
    Positivo = verde, Negativo = rojo, Trivial = gris.
    """
    a = abs(es)
    if a < 0.2:
        return '#adb5bd'          # Trivial - gris
    if es > 0:
        if a < 0.6:  return '#c3e6cb'   # Small beneficioso
        if a < 1.2:  return '#28a745'   # Moderate beneficioso
        return '#155724'                 # Large beneficioso
    else:
        if a < 0.6:  return '#f5c6cb'   # Small perjudicial
        if a < 1.2:  return '#dc3545'   # Moderate perjudicial
        return '#721c24'                 # Large perjudicial

def get_magnitude_text_color(es):
    """Color de texto: blanco para fondos oscuros, oscuro para claros."""
    a = abs(es)
    if a < 0.2:  return '#495057'        # gris oscuro sobre gris claro
    if a < 0.6:  return '#155724' if es > 0 else '#721c24'  # oscuro sobre claro
    return '#ffffff'                      # blanco sobre oscuro

def calcular_swc_jugador(pre, post, sd_grupo):
    """
    Calcula SWC y magnitud para un jugador.
    Retorna dict o None si faltan datos.
    """
    if pd.isna(pre) or pd.isna(post) or pd.isna(sd_grupo) or sd_grupo == 0:
        return None
    SWC = 0.2 * sd_grupo
    TE  = sd_grupo * np.sqrt(1 - ICC)
    cambio = post - pre
    es     = cambio / sd_grupo
    return {
        'pre': pre, 'post': post,
        'cambio': cambio,
        'es': es,
        'SWC': SWC,
        'TE': TE,
        'sd_grupo': sd_grupo,
        'magnitud': get_magnitude_label(es),
        'color': get_magnitude_color(es),
        'color_texto': get_magnitude_text_color(es),
    }

def get_var_series(data, var, categoria=None, dni=None, mes=None):
    """
    Obtiene la serie de una variable desde rendimiento o pfza.
    Si mes=None devuelve toda la historia.
    """
    # Usar variables dinámicas como en mbd_page.py
    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    sheet = 'rendimiento' if var in vars_rend else 'pfza'
    df = data[sheet].copy()
    if var not in df.columns:
        return pd.Series(dtype=float)
    if categoria:
        cat_norm = _norm_cat(categoria)
        df = df[df['Categoria'].apply(_norm_cat) == cat_norm]
    if dni:
        df = df[df['DNI'] == dni]
    if mes:
        df = filter_by_month_smart(df, mes, categoria)
    return df[var].dropna()


# ---- LAYOUT --------------------------------------------------------------------
def layout():
    data = load_data()
    if data is None:
        return dbc.Alert("Error cargando AMS.xlsx", color="danger")

    categorias  = get_categorias(data)
    cat_options = [{'label': c, 'value': c} for c in categorias]
    primera_cat = categorias[0] if categorias else None

    # Detectar TODAS las fechas de evaluación disponibles (sin restricciones por categoría)
    meses_set = set()
    
    # Para hoja 'rendimiento': usar solo columna 'Fecha' (no 'Fecha de nacimiento')
    if 'rendimiento' in data:
        df_rend = data['rendimiento']
        if 'Fecha' in df_rend.columns:
            try:
                m = (pd.to_datetime(df_rend['Fecha'], errors='coerce')
                     .dt.to_period('M')
                     .astype(str)
                     .dropna())
                meses_set.update(m[m != 'NaT'].tolist())
            except Exception:
                pass
    
    # Para hoja 'pfza' (mapeada a 'Plat de fuerza'): usar columna 'Fecha'
    if 'pfza' in data:
        df_pfza = data['pfza']
        if 'Fecha' in df_pfza.columns:
            try:
                m = (pd.to_datetime(df_pfza['Fecha'], errors='coerce')
                     .dt.to_period('M')
                     .astype(str)
                     .dropna())
                meses_set.update(m[m != 'NaT'].tolist())
            except Exception:
                pass

    meses = sorted([m for m in meses_set if m and m != 'NaT'])
    if not meses:
        meses = get_available_months(data)   # fallback al método original

    mes_options = [{'label': m, 'value': m} for m in meses]
    
    # Validar que hay al menos 2 meses
    if len(meses) < 2:
        # Si solo hay 1 mes, no se puede hacer comparación
        mes_options = [{'label': f"{m} (unico mes disponible)", 'value': m} 
                       for m in meses]
    default_pre  = meses[-2] if len(meses) >= 2 else (meses[0] if meses else None)
    default_post = meses[-1] if meses else None

    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    todas_vars = vars_rend + vars_pfza
    var_options = [
        {'label': DISPLAY_NAMES.get(v, v), 'value': v} 
        for v in todas_vars
    ]
    # Valor por defecto: primera variable de fuerza disponible
    default_var = vars_pfza[0] if vars_pfza else (vars_rend[0] if vars_rend else None)

    return html.Div([

        # ---- Título ---------------------------------------------------------------
        html.Div([
            html.H3("SWC - Smallest Worthwhile Change", style={
                'fontFamily': 'Rajdhani, sans-serif', 'fontWeight': '700',
                'color': '#1a1a2e', 'marginBottom': '4px', 'letterSpacing': '1px'
            }),
            html.P(
                "Hopkins (2006) | SWC = 0.2 x SD grupo | "
                "Small: 0.2-0.6 SD | Moderate: 0.6-1.2 SD | Large: >1.2 SD",
                style={'color': '#6c757d', 'fontSize': '12px', 'marginBottom': '20px'}
            ),
        ]),

        # ---- Botones de vista -----------------------------------------------------
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button(
                        "Squad SWC", id='swc-btn-squad',
                        color="primary", outline=False,
                        style={'fontWeight': '600', 'letterSpacing': '0.5px'}
                    ),
                    dbc.Button(
                        "SWC Individual", id='swc-btn-individual',
                        color="primary", outline=True,
                        style={'fontWeight': '600', 'letterSpacing': '0.5px'}
                    ),
                ], size="md"),
            ], width=12, className="mb-4"),
        ]),

        # ---- Store para vista activa ------------------------------------------------
        dcc.Store(id='swc-vista', data='squad'),

        # ---- Filtros comunes --------------------------------------------------------
        dbc.Row([
            dbc.Col([
                html.Label("Categoria", style={
                    'fontSize': '11px', 'textTransform': 'uppercase',
                    'color': '#6c757d', 'fontWeight': '600'
                }),
                dcc.Dropdown(
                    id='swc-categoria', options=cat_options,
                    value=primera_cat, clearable=False
                ),
            ], width=3),

            dbc.Col([
                html.Label("Variable", style={
                    'fontSize': '11px', 'textTransform': 'uppercase',
                    'color': '#6c757d', 'fontWeight': '600'
                }),
                dcc.Dropdown(
                    id='swc-variable', options=var_options,
                    value='Altura Salto', clearable=False
                ),
            ], width=3),

            dbc.Col([
                html.Label("Mes Pre (baseline)", style={
                    'fontSize': '11px', 'textTransform': 'uppercase',
                    'color': '#6c757d', 'fontWeight': '600'
                }),
                dcc.Dropdown(
                    id='swc-mes-pre', options=mes_options,
                    value=default_pre, clearable=False
                ),
            ], width=2),

            dbc.Col([
                html.Label("Mes Post", style={
                    'fontSize': '11px', 'textTransform': 'uppercase',
                    'color': '#6c757d', 'fontWeight': '600'
                }),
                dcc.Dropdown(
                    id='swc-mes-post', options=mes_options,
                    value=default_post, clearable=False
                ),
            ], width=2),

            # Filtro jugador - solo visible en vista Individual
            dbc.Col([
                html.Label("Jugador", style={
                    'fontSize': '11px', 'textTransform': 'uppercase',
                    'color': '#6c757d', 'fontWeight': '600'
                }),
                dcc.Dropdown(
                    id='swc-jugador', options=[],
                    value=None, clearable=False,
                    placeholder="Selecciona jugador..."
                ),
            ], width=2, id='swc-col-jugador', style={'display': 'none'}),

        ], className="mb-4"),

        # ---- Leyenda de magnitudes -------------------------------------------------
        html.Div([
            html.Div([
                html.Span("Trivial (<0.2 SD)", style={'fontSize': '11px', 'color': '#6c757d', 'marginRight': '14px'}),
                html.Span("Small Ben (0.2-0.6)", style={'fontSize': '11px', 'color': '#6c757d', 'marginRight': '14px'}),
                html.Span("Moderate Ben (0.6-1.2)", style={'fontSize': '11px', 'color': '#6c757d', 'marginRight': '14px'}),
                html.Span("Large Ben (>1.2)", style={'fontSize': '11px', 'color': '#6c757d', 'marginRight': '14px'}),
                html.Span("Small/Mod/Large Per", style={'fontSize': '11px', 'color': '#6c757d'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '2px'})
        ], style={
            'backgroundColor': '#f8f9fa', 'padding': '8px 14px',
            'borderRadius': '6px', 'marginBottom': '16px',
            'border': '1px solid #e0e0e0'
        }),

        # ---- Contenido principal — SOLO GRÁFICO (sin tabla lateral) --------
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='swc-grafico')
                    ])
                ], style={
                    'backgroundColor': '#ffffff',
                    'border': '1px solid #e0e0e0',
                    'boxShadow': '0 1px 4px rgba(0,0,0,0.06)'
                }),
            ], width=12),   # ← width=12 ocupa todo el ancho
        ], className="mb-3"),

        # ---- Tabla debajo del gráfico (solo para Individual) ----------------
        dbc.Row([
            dbc.Col([
                html.Div(id='swc-tabla')
            ], width=12),
        ]),

    ], style={'padding': '20px'})


# ---- CALLBACKS -----------------------------------------------------------------

@callback(
    Output('swc-vista', 'data'),
    Output('swc-btn-squad', 'outline'),
    Output('swc-btn-individual', 'outline'),
    Input('swc-btn-squad', 'n_clicks'),
    Input('swc-btn-individual', 'n_clicks'),
    prevent_initial_call=False,
)
def cambiar_vista(n_squad, n_ind):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else ''
    if 'individual' in triggered:
        return 'individual', True, False
    return 'squad', False, True


@callback(
    Output('swc-col-jugador', 'style'),
    Output('swc-jugador', 'options'),
    Output('swc-jugador', 'value'),
    Input('swc-vista', 'data'),
    Input('swc-categoria', 'value'),
)
def actualizar_jugador_dropdown(vista, categoria):
    data = load_data()
    if data is None or not categoria:
        return {'display': 'none'}, [], None
    jugadores = get_jugadores_por_categoria(data, categoria)
    options   = [{'label': j['NombreCompleto'], 'value': j['DNI']} for j in jugadores]
    primer    = jugadores[0]['DNI'] if jugadores else None
    style     = {'display': 'block'} if vista == 'individual' else {'display': 'none'}
    return style, options, primer




# Cache para evitar recargas innecesarias
_cache_callback = {'last_params': None, 'last_result': None}

@callback(
    Output('swc-grafico', 'children'),
    Output('swc-tabla', 'children'),
    Input('swc-vista', 'data'),
    Input('swc-categoria', 'value'),
    Input('swc-variable', 'value'),
    Input('swc-mes-pre', 'value'),
    Input('swc-mes-post', 'value'),
    Input('swc-jugador', 'value'),
    Input('auto-reload', 'n_intervals'),
)
def actualizar_contenido(vista, categoria, variable, mes_pre, mes_post, dni_jugador, n_intervals):
    # Cache rápido: si los parámetros no cambiaron, devolver resultado cacheado
    current_params = (vista, categoria, variable, mes_pre, mes_post, dni_jugador)
    if _cache_callback['last_params'] == current_params and _cache_callback['last_result']:
        return _cache_callback['last_result']
    
    vacio = html.Div("Selecciona todos los parametros",
                     style={'textAlign': 'center', 'color': '#888', 'padding': '30px'})
    if not all([vista, categoria, variable, mes_pre, mes_post]):
        return vacio, ""

    # Validar que Pre y Post son distintos
    if mes_pre == mes_post:
        result = html.Div([
            html.P("Mes Pre y Mes Post deben ser distintos.",
                   style={'color': '#856404', 'fontWeight': '700'}),
            html.P(
                f"Seleccionaste '{mes_pre}' para ambos. "
                f"El grafico muestra el CAMBIO entre dos periodos diferentes.",
                style={'fontSize': '12px', 'color': '#666'}
            ),
        ], style={
            'padding': '20px', 'backgroundColor': '#fff3cd',
            'borderRadius': '6px', 'margin': '10px 0'
        }), ""
        _cache_callback['last_params'] = current_params
        _cache_callback['last_result'] = result
        return result

    # Carga diferida: solo forzar recarga si es necesario
    import data_loader as _dl
    import os
    try:
        current_mtime = os.path.getmtime('../AMS.xlsx')
        if _dl._cache['mtime'] != current_mtime:
            _dl._cache = {'data': None, 'mtime': 0.0}
    except:
        pass
    
    data = load_data()
    if data is None:
        result = html.Div("Error cargando datos", style={'color': '#dc3545'}), ""
        _cache_callback['last_params'] = current_params
        _cache_callback['last_result'] = result
        return result

    # Intentar generar el gráfico y manejar errores específicos
    try:
        if vista == 'squad':
            return crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        else:
            if not dni_jugador:
                return vacio, ""
            return crear_individual_swc(data, categoria, variable, mes_pre, mes_post, dni_jugador)
    except Exception as e:
        # Manejar errores específicos de datos no encontrados
        error_msg = str(e).lower()
        if "sin datos" in error_msg or "no hay datos" in error_msg:
            result = html.Div([
                html.H4("Sin datos para la selección", style={'color': '#dc3545', 'marginBottom': '10px'}),
                html.P(f"No se encontraron datos para {categoria} en los períodos seleccionados.", 
                      style={'color': '#6c757d'}),
                html.P("Intenta con otras fechas o categorías.", style={'color': '#6c757d', 'fontSize': '14px'})
            ], style={'textAlign': 'center', 'padding': '40px'}), ""
        else:
            result = html.Div([
                html.H4("Error inesperado", style={'color': '#dc3545', 'marginBottom': '10px'}),
                html.P(f"Error: {str(e)}", style={'color': '#6c757d'})
            ], style={'textAlign': 'center', 'padding': '40px'}), ""
        
        # Cache del resultado
        _cache_callback['last_params'] = current_params
        _cache_callback['last_result'] = result
        return result


def crear_squad_swc(data, categoria, variable, mes_pre, mes_post):
    """
    Squad SWC — réplica del video Action Apps (minuto 7:35):
    Scatter plot: X = resultado actual (Post), Y = cambio vs baseline (Pre)
    Bandas horizontales de color por zona de magnitud SWC.
    """
    jugadores = get_jugadores_por_categoria(data, categoria)
    if not jugadores:
        return html.Div("Sin jugadores para esta categoria",
                        style={'color': '#888', 'padding': '20px'}), ""

    # Detectar sheet correcto
    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    sheet = 'rendimiento' if variable in vars_rend else 'pfza'
    df = data[sheet]
    variable_actual = variable   # el nombre es exactamente el de la columna

    # Validar que la variable existe en el sheet
    if variable_actual not in df.columns:
        # Intentar búsqueda flexible por similitud
        cols_similares = [c for c in df.columns 
                         if variable_actual.lower().replace(' ', '') in c.lower().replace(' ', '')]
        msg = (
            f"Variable '{variable}' (mapeada a '{variable_actual}') no encontrada en sheet '{sheet}'.<br>"
            f"Columnas disponibles: {df.columns.tolist()}"
        )
        if cols_similares:
            msg += f"<br>Columnas similares encontradas: {cols_similares}"
        return html.Div([
            html.P(f"Variable '{variable}' no encontrada en '{sheet}'.",
                   style={'fontWeight': '700', 'color': '#dc3545'}),
            html.P(f"Columnas disponibles: {', '.join(df.columns.tolist())}",
                   style={'fontSize': '11px', 'color': '#666'}),
        ], style={'padding': '20px', 'backgroundColor': '#fff3cd',
                  'borderRadius': '6px', 'border': '1px solid #ffc107'}), ""
    
    # Validar que la variable tenga datos válidos
    valores_variable = df[variable_actual].dropna()
    if len(valores_variable) == 0:
        return html.Div([
            html.P(f"La variable '{variable}' no tiene valores válidos.",
                   style={'fontWeight': '700', 'color': '#dc3545'}),
            html.P("Todos los valores son NaN o vacíos.",
                   style={'fontSize': '11px', 'color': '#666'}),
        ], style={'padding': '20px', 'backgroundColor': '#fff3cd',
                  'borderRadius': '6px', 'border': '1px solid #ffc107'}), ""

    # ── Filtrar por categoría Y mes ───────────────────────────────────────
    cat_norm = _norm_cat(categoria)
    df_cat = df[df['Categoria'].apply(_norm_cat) == cat_norm].copy() if 'Categoria' in df.columns else df.copy()

    # Filtro ESTRICTO por mes sin fallback para que los dropdowns 
    # reflejen exactamente lo que el usuario seleccionó
    pre_cat  = _filtrar_mes_estricto(df_cat, mes_pre)
    post_cat = _filtrar_mes_estricto(df_cat, mes_post)

    # Filtro de categoría mejorado - manejar nombres exactos y coincidencias
    if 'Categoria' in pre_cat.columns:
        pre_cat  = pre_cat[pre_cat['Categoria'].apply(_norm_cat) == cat_norm]
    if 'Categoria' in post_cat.columns:
        post_cat = post_cat[post_cat['Categoria'].apply(_norm_cat) == cat_norm]

    # Validaciones
    if pre_cat.empty:
        return html.Div(
            f"Sin datos Pre ({mes_pre}) para '{categoria}'. "
            f"Meses con datos: verificá el Excel.",
            style={'color': '#856404', 'padding': '20px',
                   'backgroundColor': '#fff3cd', 'borderRadius': '6px'}
        ), ""

    if post_cat.empty:
        return html.Div(
            f"Sin datos Post ({mes_post}) para '{categoria}'.",
            style={'color': '#856404', 'padding': '20px',
                   'backgroundColor': '#fff3cd', 'borderRadius': '6px'}
        ), ""

    vals_pre = pre_cat[variable_actual].dropna()
    vals_post = post_cat[variable_actual].dropna()
    
    if len(vals_pre) < 2:
        return html.Div(
            f"Solo {len(vals_pre)} dato(s) en Pre ({mes_pre}). Minimo: 2.",
            style={'color': '#856404', 'padding': '20px',
                   'backgroundColor': '#fff3cd', 'borderRadius': '6px'}
        ), ""

    # Corrección para variables de fuerza con valores inconsistentes
    # Usar SD más conservadora entre Pre y Post para evitar ES extremos
    sd_pre = float(vals_pre.std(ddof=1))
    sd_post = float(vals_post.std(ddof=1))
    
    # Para variables de fuerza, usar la SD más pequeña y estable
    if variable_actual in ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250']:
        # Detectar valores inconsistentes (diferencia > 10x entre medias)
        media_pre = vals_pre.mean()
        media_post = vals_post.mean()
        
        if abs(media_post - media_pre) > max(media_pre, media_post) * 10:
            # Hay inconsistencia grave - usar SD más conservadora
            sd_grupo = min(sd_pre, sd_post, max(sd_pre, sd_post) * 0.3)
        else:
            # Datos consistentes - usar SD combinada ponderada
            sd_grupo = (sd_pre + sd_post) / 2
    else:
        # Para variables de rendimiento, usar SD estándar del Pre
        sd_grupo = sd_pre

    # Diagnóstico: verificar que sd_grupo tiene sentido
    if sd_grupo == 0:
        # Todos los jugadores tienen el mismo valor en el pre-test
        valor_unico = float(vals_pre.iloc[0])
        return html.Div([
            html.P(f"SD del grupo = 0 para '{variable}' en {mes_pre}.",
                   style={'fontWeight': '700', 'color': '#856404'}),
            html.P(
                f"Todos los jugadores tienen el mismo valor: {valor_unico:.2f}. "
                f"No es posible calcular SWC con SD = 0.",
                style={'fontSize': '12px', 'color': '#666'}
            ),
        ], style={'padding': '20px', 'backgroundColor': '#fff3cd',
                  'borderRadius': '6px'}), ""

    SWC = 0.2 * sd_grupo
    TE  = sd_grupo * np.sqrt(1 - ICC)

    # ── Calcular por jugador ──────────────────────────────────────────────
    resultados = []
    for j in jugadores:
        dni    = j['DNI']
        nombre = j['NombreCompleto']

        # Buscar datos por DNI primero
        fp = pre_cat[pre_cat['DNI'] == dni][variable_actual].dropna()
        fpo = post_cat[post_cat['DNI'] == dni][variable_actual].dropna()

        # Si no hay datos por DNI, buscar por nombre de jugador (flexible)
        if fp.empty or fpo.empty:
            # Extraer apellido del nombre completo
            partes_nombre = nombre.split()
            apellido = partes_nombre[-1] if partes_nombre else nombre
            
            # Buscar en pre por apellido
            if fp.empty:
                match_pre = pre_cat[pre_cat['Apellido'].str.strip().str.lower() == apellido.strip().lower()]
                if not match_pre.empty:
                    fp = match_pre[variable_actual].dropna()
                else:
                    # Búsqueda más flexible
                    for idx, row in pre_cat.iterrows():
                        apellido_pre = str(row['Apellido']).strip().lower()
                        apellido_busqueda = apellido.strip().lower()
                        if apellido_busqueda in apellido_pre or apellido_pre in apellido_busqueda:
                            fp = pd.Series([row[variable_actual]]).dropna()
                            break
            
            # Buscar en post por apellido
            if fpo.empty:
                match_post = post_cat[post_cat['Apellido'].str.strip().str.lower() == apellido.strip().lower()]
                if not match_post.empty:
                    fpo = match_post[variable_actual].dropna()
                else:
                    # Búsqueda más flexible
                    for idx, row in post_cat.iterrows():
                        apellido_post = str(row['Apellido']).strip().lower()
                        apellido_busqueda = apellido.strip().lower()
                        if apellido_busqueda in apellido_post or apellido_post in apellido_busqueda:
                            fpo = pd.Series([row[variable_actual]]).dropna()
                            break

        if fp.empty or fpo.empty:
            continue

        pre_val  = float(fp.iloc[0])
        post_val = float(fpo.iloc[0])
        cambio   = post_val - pre_val
        es       = cambio / sd_grupo

        # Umbral generoso: solo eliminar datos absolutamente imposibles
        # Con pfza ya agregado, los ES deberían ser razonables
        if abs(es) > 100.0:
            continue

        abs_es = abs(es)
        
        # Clasificación basada en ES (Effect Size) según referencias estándar
        if abs_es < 0.2:
            magnitud = 'Trivial'
        elif abs_es < 0.6:
            magnitud = 'Small'
        elif abs_es < 1.2:
            magnitud = 'Moderate'
        else:
            magnitud = 'Large'
        
        # Agregar Ben/Per según el signo
        if es >= 0:
            magnitud = magnitud + ' Ben'
        else:
            magnitud = magnitud + ' Per'

        # Paleta de colores para magnitudes estándar (verde arriba, colores cálidos abajo)
        CPOS = {'Trivial Ben':'#e8f5e8', 'Small Ben':'#c8e6c9',
                'Moderate Ben':'#81c784', 'Large Ben':'#2e7d32'}
        CNEG = {'Trivial Per':'#fff8e1', 'Small Per':'#ffecb3',
                'Moderate Per':'#ffb74d', 'Large Per':'#d84315'}
        color = CPOS[magnitud] if es >= 0 else CNEG[magnitud]

        # Nombre corto para label en el punto
        partes = nombre.split()
        label_corto = ' '.join(partes[:2]) if len(partes) >= 2 else nombre

        resultados.append({
            'nombre': nombre, 'label': label_corto,
            'pre': pre_val, 'post': post_val,
            'cambio': cambio, 'es': es,
            'magnitud': magnitud, 'color': color,
        })

    if not resultados:
        # Diagnóstico detallado
        detalles = []
        for j in jugadores:
            dni = j['DNI']
            fp  = pre_cat[pre_cat['DNI'] == dni][variable_actual].dropna()
            fpo = post_cat[post_cat['DNI'] == dni][variable_actual].dropna()
            if not fp.empty and not fpo.empty:
                pre_v  = float(fp.iloc[0])
                post_v = float(fpo.iloc[0])
                cambio_v = post_v - pre_v
                es_v = cambio_v / sd_grupo if sd_grupo != 0 else 0
                detalles.append(
                    f"{j['NombreCompleto']}: pre={pre_v:.2f} post={post_v:.2f} "
                    f"cambio={cambio_v:+.2f} ES={es_v:+.2f}"
                )
        return html.Div([
            html.P(
                f"Sin resultados para '{variable}' en '{categoria}'.",
                style={'fontWeight': '700', 'color': '#856404'}
            ),
            html.P(
                f"SD={sd_grupo:.4f} | SWC={SWC:.4f} | "
                f"Jugadores con datos en ambos meses: {len(detalles)}/{len(jugadores)}",
                style={'fontSize': '12px', 'color': '#666'}
            ),
            html.Ul([
                html.Li(d, style={'fontSize': '11px', 'color': '#888'})
                for d in detalles
            ]) if detalles else html.P(
                "Ningun jugador tiene datos en ambos meses para esta combinacion.",
                style={'fontSize': '11px', 'color': '#888'}
            ),
        ], style={
            'padding': '20px', 'backgroundColor': '#fff3cd',
            'borderRadius': '6px', 'border': '1px solid #ffc107'
        }), ""

    # ── Rangos ───────────────────────────────────────────────────
    todos_post   = [r['post']   for r in resultados]
    todos_cambio = [r['cambio'] for r in resultados]
    x_min = min(todos_post) * 0.96
    x_max = max(todos_post) * 1.04
    
    # Rangos del gráfico - SIMÉTRICO y basado en ES (Effect Size)
    todos_es = [r['es'] for r in resultados]
    es_min = min(todos_es)
    es_max = max(todos_es)
    
    # Para simetría automática: usar el valor absoluto más grande
    max_es_abs = max(abs(es_min), abs(es_max))
    
    # Margen del 20% para visualización clara
    margen_es = max_es_abs * 0.2
    
    # Rango simétrico centrado en 0
    y_plot_min = -(max_es_abs + margen_es)
    y_plot_max = (max_es_abs + margen_es)
    
    # Asegurar que las líneas SWC sean visibles (±1 ES)
    y_plot_min = min(y_plot_min, -1.0)
    y_plot_max = max(y_plot_max, 1.0)

    y_range = [y_plot_min, y_plot_max]

    # Ajustar las bandas de fondo al rango real (no a y_max_abs fijo)
    y_banda_min = y_plot_min
    y_banda_max = y_plot_max

    # ── Figura ────────────────────────────────────────────────────
    fig = go.Figure()

    # Bandas horizontales basadas en ES estándar (verde arriba, colores cálidos abajo)
    bandas = [
        # Positivas (arriba del cero - beneficio)
        (1.2,      y_banda_max, 'rgba(46,125,50,0.20)'),    # Large Ben (>1.2)
        (0.6,      1.2,         'rgba(129,199,132,0.22)'),  # Moderate Ben (0.6-1.2)
        (0.2,      0.6,         'rgba(200,230,201,0.25)'),  # Small Ben (0.2-0.6)
        (0,        0.2,         'rgba(232,245,232,0.30)'),  # Trivial Ben (<0.2)
        # Negativas (debajo del cero - perjuicio)
        (-0.2,     0,           'rgba(255,248,225,0.35)'),  # Trivial Per (<-0.2)
        (-0.6,     -0.2,        'rgba(255,236,179,0.30)'),  # Small Per (-0.6 a -0.2)
        (-1.2,     -0.6,        'rgba(255,183,77,0.25)'),   # Moderate Per (-1.2 a -0.6)
        (y_banda_min, -1.2,     'rgba(216,67,21,0.20)'),    # Large Per (<-1.2)
    ]
    for y0, y1, color_fill in bandas:
        y0c = max(y0, y_banda_min)
        y1c = min(y1, y_banda_max)
        if y0c < y1c:
            fig.add_hrect(y0=y0c, y1=y1c,
                          fillcolor=color_fill, line_width=0, layer='below')

    # Línea Y=0
    fig.add_hline(y=0, line_color='rgba(0,0,0,0.35)',
                  line_width=2, line_dash='solid')

    # Líneas de referencia ES estándar
    fig.add_hline(y=0.2,  line_dash='dash',
                  line_color='rgba(40,167,69,0.6)', line_width=1.2,
                  annotation_text='Small (0.2)',
                  annotation_font_color='#28a745', annotation_font_size=9,
                  annotation_position='right')
    fig.add_hline(y=0.6,  line_dash='dash',
                  line_color='rgba(40,167,69,0.6)', line_width=1.2,
                  annotation_text='Moderate (0.6)',
                  annotation_font_color='#28a745', annotation_font_size=9,
                  annotation_position='right')
    fig.add_hline(y=1.2,  line_dash='dash',
                  line_color='rgba(40,167,69,0.6)', line_width=1.2,
                  annotation_text='Large (1.2)',
                  annotation_font_color='#28a745', annotation_font_size=9,
                  annotation_position='right')
    fig.add_hline(y=-0.2, line_dash='dash',
                  line_color='rgba(220,53,69,0.6)', line_width=1.2,
                  annotation_text='Small (-0.2)',
                  annotation_font_color='#dc3545', annotation_font_size=9,
                  annotation_position='right')
    fig.add_hline(y=-0.6, line_dash='dash',
                  line_color='rgba(220,53,69,0.6)', line_width=1.2,
                  annotation_text='Moderate (-0.6)',
                  annotation_font_color='#dc3545', annotation_font_size=9,
                  annotation_position='right')
    fig.add_hline(y=-1.2, line_dash='dash',
                  line_color='rgba(220,53,69,0.6)', line_width=1.2,
                  annotation_text='Large (-1.2)',
                  annotation_font_color='#dc3545', annotation_font_size=9,
                  annotation_position='right')

    # Puntos + labels - CORREGIDO: Usar ES en el eje Y
    fig.add_trace(go.Scatter(
        x=[r['post']   for r in resultados],
        y=[r['es'] for r in resultados],  # CORRECCIÓN: Usar ES en lugar de cambio
        mode='markers+text',
        marker=dict(
            color=[r['color'] for r in resultados],
            size=16,
            line=dict(color='rgba(0,0,0,0.5)', width=1.5),
            symbol='circle',
        ),
        text=[r['label'] for r in resultados],
        textposition='top center',
        textfont=dict(size=10, color='#1a1a2e',
                      family='IBM Plex Sans, sans-serif'),
        customdata=[[r['nombre'], r['pre'], r['cambio'],
                     r['es'], r['magnitud']] for r in resultados],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Resultado actual: %{x:.2f}<br>"
            "Cambio vs Pre: %{customdata[2]:+.2f}<br>"
            "ES: %{y:+.2f} SD<br>"
            "Magnitud: %{customdata[4]}<br>"
            "<extra></extra>"
        ),
        name='Jugadores'
    ))

    # Etiquetas de zona (derecha, FUERA del gráfico con xref='paper')
    zonas = [
        (y_banda_max * 0.88, 'Large Ben',      '#2e7d32'),
        (0.9,                'Moderate Ben',   '#2e7d32'),
        (0.4,                'Small Ben',      '#00796b'),
        (0.1,                'Trivial',        '#6c757d'),
        (-0.1,               'Trivial',        '#6c757d'),
        (-0.4,               'Small Per',      '#e65100'),
        (-0.9,               'Moderate Per',   '#bf360c'),
        (y_banda_min * 0.88, 'Large Per',      '#b71c1c'),
    ]
    for y_pos, label, color_txt in zonas:
        if y_banda_min * 0.98 <= y_pos <= y_banda_max * 0.98:
            fig.add_annotation(
                x=1.01, xref='paper',
                y=y_pos, yref='y',
                text=label,
                showarrow=False,
                xanchor='left', yanchor='middle',
                font=dict(size=9, color=color_txt,
                          family='IBM Plex Sans, sans-serif'),
            )

    var_display = DISPLAY_NAMES.get(variable, variable)

    # Altura adaptiva: mínimo 450, más espacio si hay muchos jugadores
    altura_grafico = max(450, len(resultados) * 35 + 200)
    
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,0.98)',
        title=dict(
            text=(f"Squad SWC - {var_display}  |  "
                  f"{mes_pre}  >  {mes_post}  |  "
                  f"SWC = {SWC:.2f}   TE = {TE:.2f}   "
                  f"SD grupo = {sd_grupo:.2f}"),
            font=dict(family='Rajdhani, sans-serif',
                      size=15, color='#1a1a2e'),
        ),
        xaxis=dict(
            title=dict(text=f"Resultado actual  -  {var_display}",
                       font=dict(size=12, color='#555')),
            range=[x_min, x_max],
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False,
            tickfont=dict(size=11),
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="Cambio vs Pre-test",
                       font=dict(size=12, color='#555')),
            range=y_range,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False,
            tickfont=dict(size=11),
            fixedrange=True,
        ),
        height=altura_grafico,
        margin=dict(l=80, r=180, t=90, b=80),  # más espacio para etiquetas
    )

    # Squad SWC: NO tabla (solo gráfico, como en el video)
    return dcc.Graph(figure=fig, config={'displayModeBar': False}), ""


def crear_individual_swc(data, categoria, variable, mes_pre, mes_post, dni):
    """
    SWC Individual: gráfico de línea temporal para UN jugador.
    Muestra TODOS los meses disponibles del jugador con bandas SWC.
    Si solo hay 2 puntos (pre y post), los usa directamente.
    El baseline siempre es mes_pre.
    """
    vars_rend = get_vars_rendimiento(data)
    sheet = 'rendimiento' if variable in vars_rend else 'pfza'
    df = data[sheet]

    if variable not in df.columns:
        return html.Div(
            f"Variable '{variable}' no encontrada.",
            style={'color': '#dc3545', 'padding': '20px'}
        ), ""

    # Nombre del jugador
    nombre_row = data['base'][data['base']['DNI'] == dni]['NombreCompleto'].values
    nombre = nombre_row[0] if len(nombre_row) > 0 else str(dni)

    # ---- Detectar columna de fecha -------------------------------------------
    # Usar SIEMPRE 'Fecha' si existe - evitar 'Fecha de nacimiento'
    if 'Fecha' in df.columns:
        fecha_col = 'Fecha'
    else:
        fecha_col = None
        for col in df.columns:
            if 'nacimiento' in col.lower() or 'nac' in col.lower():
                continue
            if any(kw in col.lower() for kw in ['fecha', 'date', 'mes', 'period']):
                fecha_col = col
                break

    if fecha_col is None:
        return html.Div(
            "No se encontro columna 'Fecha' en los datos.",
            style={'color': '#dc3545', 'padding': '20px'}
        ), ""

    # ---- Historial completo del jugador ----------------------------------------
    df_jug = df[df['DNI'] == dni][[fecha_col, variable]].dropna().copy()
    df_jug['periodo'] = (
        pd.to_datetime(df_jug[fecha_col], errors='coerce')
        .dt.to_period('M')
        .astype(str)
    )
    df_jug = (
        df_jug.groupby('periodo')[variable]
        .mean()
        .reset_index()
        .sort_values('periodo')
    )

    # ---- Si no hay historial suficiente, usar solo Pre y Post -----------------
    if df_jug.empty or len(df_jug) < 2:
        # Construir manualmente con Pre y Post
        pre_df  = _filtrar_mes_estricto(df, mes_pre)
        post_df = _filtrar_mes_estricto(df, mes_post)

        fila_pre  = pre_df[pre_df['DNI'] == dni][variable].dropna()
        fila_post = post_df[post_df['DNI'] == dni][variable].dropna()

        if fila_pre.empty and fila_post.empty:
            return html.Div(
                f"Sin datos para {nombre} en los períodos seleccionados.",
                style={'color': '#888', 'padding': '20px'}
            ), ""

        # Armar el DataFrame mínimo con los datos disponibles
        filas = []
        if not fila_pre.empty:
            filas.append({'periodo': mes_pre,  variable: float(fila_pre.iloc[0])})
        if not fila_post.empty and mes_post != mes_pre:
            filas.append({'periodo': mes_post, variable: float(fila_post.iloc[0])})

        df_jug = pd.DataFrame(filas).sort_values('periodo')

    # ---- Verificar que mes_pre está en el historial, si no agregar ------------
    periodos_existentes = df_jug['periodo'].tolist()
    if mes_pre not in periodos_existentes:
        pre_df = _filtrar_mes_estricto(df, mes_pre)
        fila_pre = pre_df[pre_df['DNI'] == dni][variable].dropna()
        if not fila_pre.empty:
            nueva_fila = pd.DataFrame([{
                'periodo': mes_pre,
                variable: float(fila_pre.iloc[0])
            }])
            df_jug = pd.concat([df_jug, nueva_fila]).sort_values('periodo').reset_index(drop=True)

    # Verificar que mes_post está en el historial, si no agregar
    if mes_post not in df_jug['periodo'].tolist():
        post_df = _filtrar_mes_estricto(df, mes_post)
        fila_post = post_df[post_df['DNI'] == dni][variable].dropna()
        if not fila_post.empty:
            nueva_fila = pd.DataFrame([{
                'periodo': mes_post,
                variable: float(fila_post.iloc[0])
            }])
            df_jug = pd.concat([df_jug, nueva_fila]).sort_values('periodo').reset_index(drop=True)

    if len(df_jug) < 2:
        return html.Div(
            f"Solo hay 1 medicion para {nombre}. "
            f"Se necesitan datos en al menos 2 periodos distintos.",
            style={'color': '#888', 'padding': '20px'}
        ), ""

    periodos = df_jug['periodo'].tolist()
    valores  = df_jug[variable].tolist()

    # ---- SD del grupo en el mes baseline (pre) --------------------------------
    cat_norm = _norm_cat(categoria)
    df_cat   = df[df['Categoria'].apply(_norm_cat) == cat_norm].copy()
    pre_cat  = _filtrar_mes_estricto(df_cat, mes_pre)
    pre_cat  = pre_cat[pre_cat['Categoria'].apply(_norm_cat) == cat_norm]
    vals_grp = pre_cat[variable].dropna()

    if len(vals_grp) >= 2:
        sd_grupo = float(vals_grp.std(ddof=1))
    else:
        # Fallback: SD del jugador a lo largo del tiempo
        sd_grupo = float(pd.Series(valores).std(ddof=1)) if len(valores) >= 2 else 1.0

    if sd_grupo == 0:
        sd_grupo = 1.0

    SWC = 0.2 * sd_grupo
    TE  = sd_grupo * np.sqrt(1 - ICC)

    # ---- Valor baseline del jugador -------------------------------------------
    baseline_row = df_jug[df_jug['periodo'] == mes_pre]
    if not baseline_row.empty:
        baseline = float(baseline_row[variable].iloc[0])
    else:
        baseline = float(df_jug[variable].iloc[0])

    # ES y colores para cada punto
    es_vals        = [(v - baseline) / sd_grupo for v in valores]
    colores_puntos = [get_magnitude_color(es) for es in es_vals]

    # ---- Figura ---------------------------------------------------------------
    fig = go.Figure()

    # Bandas de magnitud basadas en ES estándar (centradas en 0)
    bandas_es = [
        (0.0,  0.2,  'rgba(232,245,232,0.30)', 'rgba(255,248,225,0.35)'),  # Trivial
        (0.2,  0.6,  'rgba(200,230,201,0.30)', 'rgba(255,236,179,0.30)'),  # Small
        (0.6,  1.2,  'rgba(129,199,132,0.25)', 'rgba(255,183,77,0.25)'),   # Moderate
        (1.2,  2.5,  'rgba(46,125,50,0.20)',    'rgba(216,67,21,0.20)'),   # Large
    ]
    for low, high, color_pos, color_neg in bandas_es:
        fig.add_hrect(y0=low, y1=high,
                      fillcolor=color_pos, line_width=0, layer='below')
        fig.add_hrect(y0=-high, y1=-low,
                      fillcolor=color_neg, line_width=0, layer='below')

    # Línea de baseline (ES = 0)
    fig.add_hline(
        y=0, line_color='rgba(0,0,0,0.35)',
        line_width=2, line_dash='solid',
        annotation_text=f"Baseline: {baseline:.2f} ({mes_pre})",
        annotation_font_color='#333',
        annotation_font_size=10,
        annotation_position='right',
    )

    # Líneas de referencia ES estándar
    fig.add_hline(
        y=0.2, line_dash='dash',
        line_color='rgba(40,167,69,0.6)', line_width=1.2,
        annotation_text='Small (0.2)',
        annotation_font_color='#28a745',
        annotation_font_size=9,
        annotation_position='right',
    )
    fig.add_hline(
        y=0.6, line_dash='dash',
        line_color='rgba(40,167,69,0.6)', line_width=1.2,
        annotation_text='Moderate (0.6)',
        annotation_font_color='#28a745',
        annotation_font_size=9,
        annotation_position='right',
    )
    fig.add_hline(
        y=1.2, line_dash='dash',
        line_color='rgba(40,167,69,0.6)', line_width=1.2,
        annotation_text='Large (1.2)',
        annotation_font_color='#28a745',
        annotation_font_size=9,
        annotation_position='right',
    )
    fig.add_hline(
        y=-0.2, line_dash='dash',
        line_color='rgba(220,53,69,0.6)', line_width=1.2,
        annotation_text='Small (-0.2)',
        annotation_font_color='#dc3545',
        annotation_font_size=9,
        annotation_position='right',
    )
    fig.add_hline(
        y=-0.6, line_dash='dash',
        line_color='rgba(220,53,69,0.6)', line_width=1.2,
        annotation_text='Moderate (-0.6)',
        annotation_font_color='#dc3545',
        annotation_font_size=9,
        annotation_position='right',
    )
    fig.add_hline(
        y=-1.2, line_dash='dash',
        line_color='rgba(220,53,69,0.6)', line_width=1.2,
        annotation_text='Large (-1.2)',
        annotation_font_color='#dc3545',
        annotation_font_size=9,
        annotation_position='right',
    )

    # Resaltar mes_pre y mes_post con líneas verticales
    if mes_pre in periodos:
        fig.add_vline(
            x=periodos.index(mes_pre),
            line_color='rgba(0,100,200,0.3)',
            line_width=1.5, line_dash='dot',
        )
    if mes_post in periodos and mes_post != mes_pre:
        fig.add_vline(
            x=periodos.index(mes_post),
            line_color='rgba(200,100,0,0.3)',
            line_width=1.5, line_dash='dot',
        )

    # Línea de tendencia (ES)
    fig.add_trace(go.Scatter(
        x=list(range(len(periodos))),
        y=es_vals,
        mode='lines',
        line=dict(color='rgba(26,26,46,0.20)', width=1.5, dash='dot'),
        showlegend=False, hoverinfo='none',
    ))

    # Puntos coloreados (ES)
    fig.add_trace(go.Scatter(
        x=list(range(len(periodos))),
        y=es_vals,
        mode='markers+text',
        marker=dict(
            color=colores_puntos, size=13,
            line=dict(color='white', width=2),
            symbol='circle',
        ),
        text=[f"{es:+.2f}" for es in es_vals],
        textposition='top center',
        textfont=dict(size=9, color='#333'),
        customdata=[[
            periodos[i],
            es_vals[i],
            get_magnitude_label(es_vals[i]),
            baseline,
            SWC,
            valores[i] - baseline,
        ] for i in range(len(valores))],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Valor: %{customdata[6]:.2f}<br>"
            "Cambio vs baseline: %{customdata[5]:+.2f}<br>"
            "ES: %{y:+.2f} SD<br>"
            "Magnitud: %{customdata[2]}<br>"
            "Baseline: %{customdata[3]:.2f}<br>"
            "SWC: +/-%{customdata[4]:.2f}<br>"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    var_display = DISPLAY_NAMES.get(variable, variable)

    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,0.98)',
        title=dict(
            text=(
                f"SWC Individual - {nombre}  |  {var_display}  |  "
                f"Baseline: {mes_pre}   SWC = +/-{SWC:.2f}   TE = {TE:.2f}"
            ),
            font=dict(family='Rajdhani, sans-serif', size=14, color='#1a1a2e'),
        ),
        xaxis=dict(
            title=dict(text="Periodo", font=dict(size=11, color='#555')),
            tickvals=list(range(len(periodos))),
            ticktext=periodos,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False,
            tickfont=dict(size=10),
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text=f"{var_display}", font=dict(size=11, color='#555')),
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False,
            tickfont=dict(size=11),
            fixedrange=True,
        ),
        height=440,
        margin=dict(l=20, r=140, t=70, b=60),
        showlegend=False,
    )

    tabla = _tabla_individual(periodos, valores, es_vals, baseline, SWC, TE, sd_grupo)
    return dcc.Graph(figure=fig, config={'displayModeBar': False}), tabla


# ---- TABLAS --------------------------------------------------------------------

def _tabla_squad(resultados, SWC):
    # Colores de magnitud del video
    COLORES_MAG = {
        'Large':   {'pos': ('#1b5e20', '#ffffff'), 'neg': ('#b71c1c', '#ffffff')},
        'Medium':  {'pos': ('#2e7d32', '#ffffff'), 'neg': ('#bf360c', '#ffffff')},
        'Small':   {'pos': ('#80cbc4', '#1a1a2e'), 'neg': ('#ffa726', '#1a1a2e')},
        'Minimal': {'pos': ('#e8f5e9', '#1a1a2e'), 'neg': ('#fff9c4', '#1a1a2e')},
    }

    encabezado = html.Thead(html.Tr([
        html.Th(col, style={
            'fontSize': '10px', 'fontWeight': '700', 'color': '#1a1a2e',
            'padding': '6px 6px', 'textAlign': 'center',
            'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #dee2e6',
            'whiteSpace': 'nowrap',
        }) for col in ['Jugador', 'Pre', 'Post', 'Cambio', 'ES (SD)', 'SWC', 'Magnitud']
    ]))

    # Ordenar por ES descendente (mayor beneficio arriba)
    resultados_ord = sorted(resultados, key=lambda r: r['es'], reverse=True)

    filas = []
    for r in resultados_ord:
        direccion = 'pos' if r['cambio'] >= 0 else 'neg'
        mag = r['magnitud']
        bg_color, txt_color = COLORES_MAG.get(mag, COLORES_MAG['Minimal'])[direccion]

        filas.append(html.Tr([
            # Jugador
            html.Td(r['nombre'], style={
                'fontSize': '11px', 'fontWeight': '600',
                'color': '#1a1a2e', 'padding': '5px 8px',
                'whiteSpace': 'nowrap',
            }),
            # Pre
            html.Td(f"{r['pre']:.1f}", style={
                'fontSize': '11px', 'textAlign': 'center',
                'padding': '5px 4px', 'color': '#555',
            }),
            # Post
            html.Td(f"{r['post']:.1f}", style={
                'fontSize': '11px', 'textAlign': 'center',
                'padding': '5px 4px', 'fontWeight': '600', 'color': '#1a1a2e',
            }),
            # Cambio
            html.Td(f"{r['cambio']:+.2f}", style={
                'fontSize': '11px', 'textAlign': 'center', 'padding': '5px 4px',
                'color': '#28a745' if r['cambio'] > 0 else '#dc3545',
                'fontWeight': '700',
            }),
            # ES (SD) - Effect Size estandarizado
            html.Td(f"{r['es']:+.2f}", style={
                'fontSize': '11px', 'textAlign': 'center', 'padding': '5px 4px',
                'color': '#28a745' if r['es'] > 0 else '#dc3545',
            }),
            # SWC (en unidades originales)
            html.Td(f"+/-{SWC:.2f}", style={
                'fontSize': '10px', 'textAlign': 'center',
                'padding': '5px 4px', 'color': '#888',
            }),
            # Magnitud - badge de color
            html.Td(
                html.Div(
                    mag,
                    style={
                        'backgroundColor': bg_color,
                        'color':           txt_color,
                        'borderRadius':    '4px',
                        'padding':         '3px 7px',
                        'fontSize':        '10px',
                        'fontWeight':      '700',
                        'textAlign':       'center',
                        'whiteSpace':      'nowrap',
                    }
                ),
                style={'padding': '3px 4px'}
            ),
        ], style={'borderBottom': '1px solid #f0f0f0'}))

    return html.Div(
        html.Table(
            [encabezado, html.Tbody(filas)],
            style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'fontSize': '11px',
            }
        ),
        style={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': '480px',
        }
    )


def _tabla_individual(periodos, valores, es_vals, baseline, SWC, TE, sd_grupo):
    encabezado = html.Thead(html.Tr([
        html.Th(h, style={
            'fontSize': '10px', 'fontWeight': '700', 'color': '#1a1a2e',
            'padding': '6px 4px', 'textAlign': 'center',
            'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #dee2e6'
        }) for h in ['Periodo', 'Valor', 'vs Baseline', 'ES (SD)', 'Magnitud']
    ]))

    filas = []
    for i, (p, v, es) in enumerate(zip(periodos, valores, es_vals)):
        cambio = v - baseline
        mag = get_magnitude_label(es)
        col = get_magnitude_color(es)
        col_txt = get_magnitude_text_color(es)
        filas.append(html.Tr([
            html.Td(p, style={
                'fontSize': '10px', 'fontWeight': '600',
                'padding': '5px 4px', 'textAlign': 'center'
            }),
            html.Td(f"{v:.2f}", style={
                'fontSize': '10px', 'padding': '5px 4px', 'textAlign': 'center'
            }),
            html.Td(f"{cambio:+.2f}", style={
                'fontSize': '10px', 'padding': '5px 4px', 'textAlign': 'center',
                'color': '#28a745' if cambio > 0 else '#dc3545', 'fontWeight': '600'
            }),
            html.Td(f"{es:+.2f}", style={
                'fontSize': '10px', 'padding': '5px 4px', 'textAlign': 'center'
            }),
            html.Td(
                html.Div(mag, style={
                    'backgroundColor': col, 'color': col_txt,
                    'borderRadius': '4px', 'padding': '2px 5px',
                    'fontSize': '9px', 'fontWeight': '700', 'textAlign': 'center'
                }),
                style={'padding': '2px 3px'}
            ),
        ], style={'borderBottom': '1px solid #f0f0f0'}))

    return html.Div(
        html.Table(
            [encabezado, html.Tbody(filas)],
            style={'width': '100%', 'borderCollapse': 'collapse'}
        ),
        style={'overflowX': 'auto', 'overflowY': 'auto', 'maxHeight': '420px'}
    )
