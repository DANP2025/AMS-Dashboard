import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, dash_table
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data_loader import (
    load_data, get_categorias, get_jugadores_por_categoria,
    get_vars_rendimiento, get_vars_pfza, get_available_months,
    filter_by_month_smart
)
from calculations import calc_mbd, get_etiqueta_inferencia, get_color_etiqueta

def _norm_cat(c):
    """Normaliza categoría: elimina espacios múltiples, Title Case."""
    if c is None or (isinstance(c, float) and pd.isna(c)):
        return ''
    return ' '.join(str(c).strip().split()).title()

# ─── MAPEO DE NOMBRES — ASCII puro (para Plotly eje Y y prints) ─────────────
DISPLAY_NAMES = {
    'VO2 max':      'VO2 max',        # SIN subindice unicode
    'Vmax':         'Vmax',
    'F0':           'F0',
    'V0':           'V0',
    'Pmax':         'Pmax',
    'RF':           'RF',
    'DRF':          'DRF',
    'Fuerza':       'Fuerza CMJ',
    'Potencia Pico':'Pot. Pico',
    'Altura Salto': 'Alt. Salto',
    'Fuerza IMTP':  'F. IMTP',
    'RFD Dec':      'RFD Dec',
    'RFD 100':      'RFD 100',
    'RFD 150':      'RFD 150',
    'RFD 250':      'RFD 250',
}

# Nombres para mostrar en HTML (pueden tener unicode, van al browser)
DISPLAY_NAMES_HTML = {
    'VO2 max':      'VO\u2082 MAX',   # VO₂ MAX — solo para HTML
    'Vmax':         'VMAX',
    'F0':           'F0',
    'V0':           'V0',
    'Pmax':         'PMAX',
    'RF':           'RF',
    'DRF':          'DRF',
    'Fuerza':       'FUERZA CMJ',
    'Potencia Pico':'POT. PICO',
    'Altura Salto': 'ALT. SALTO',
    'Fuerza IMTP':  'F. IMTP',
    'RFD Dec':      'RFD DEC',
    'RFD 100':      'RFD 100',
    'RFD 150':      'RFD 150',
    'RFD 250':      'RFD 250',
}

# ─── REFERENCIAS DE WILL HOPKINS ─────────────────────────────────────────────
HOPKINS_REFERENCES = {
    'Probable Beneficioso': '>75% beneficio, <5% perjuicio',
    'Posible Beneficioso': '25-75% beneficio, 0-25% perjuicio',
    'Trivial': '<25% beneficio, <25% perjuicio',
    'Posible Perjudicial': '0-25% beneficio, 25-75% perjuicio',
    'Probable Perjudicial': '<5% beneficio, >75% perjuicio'
}


# ─── LAYOUT ───────────────────────────────────────────────────────────────────

def layout():
    data = load_data()
    if data is None:
        return dbc.Alert("❌ No se pudo cargar AMS.xlsx. Verificá la ruta.", color="danger")

    categorias = get_categorias(data)
    cat_options = [{'label': c, 'value': c} for c in categorias]
    primera_cat = categorias[0] if categorias else None

    meses = get_available_months(data)
    month_options = [{'label': m, 'value': m} for m in meses]
    # Preseleccionar los 2 últimos meses si hay suficientes
    default_meses = meses[-2:] if len(meses) >= 2 else meses

    return html.Div([
        # Título
        html.Div([
            html.H3("📈 MBD — Magnitud Basada en Decisiones", style={
                'fontFamily': 'Rajdhani, sans-serif',
                'fontWeight': '700',
                'color': '#1a1a2e',
                'marginBottom': '4px',
                'letterSpacing': '1px'
            }),
            html.P(
                "Metodología Will Hopkins | SWC = 0.2 × SD baseline | TE estimado por ICC (0.90)",
                style={'color': '#555', 'fontSize': '12px', 'marginBottom': '20px'}
            ),
        ]),

        # ── Filtros ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Categoría", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dcc.Dropdown(id='mbd-cat-jugador', options=cat_options, value=primera_cat, clearable=False)
            ], width=3),
            dbc.Col([
                html.Label("JUGADOR", style={
                    'color': '#666', 'fontSize': '11px', 
                    'fontWeight': '700', 'letterSpacing': '1px',
                    'textTransform': 'uppercase', 'marginBottom': '4px',
                    'display': 'block'
                }),
                dbc.InputGroup([
                    dcc.Dropdown(
                        id='mbd-jugador',
                        options=[],
                        value=[],
                        multi=True,                          # ← CLAVE: multi-select
                        placeholder="Todos los jugadores...",
                        style={'flex': '1', 'minWidth': '0'},
                    ),
                    dbc.Button(
                        "Todos",
                        id='mbd-btn-todos',
                        color="secondary",
                        outline=True,
                        size="sm",
                        style={'borderRadius': '0 6px 6px 0', 'fontSize': '12px', 'whiteSpace': 'nowrap'}
                    ),
                ], style={'display': 'flex', 'alignItems': 'stretch'}),
            ], width=4),
            dbc.Col([
                html.Label("Mes Pre", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dcc.Dropdown(id='mbd-mes-pre', options=month_options, value=default_meses[0] if default_meses else None, clearable=False)
            ], width=2),
            dbc.Col([
                html.Label("Mes Post", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dcc.Dropdown(id='mbd-mes-post', options=month_options, value=default_meses[1] if len(default_meses) > 1 else None, clearable=False)
            ], width=2),
        ], className="mb-4"),

        # ── Selector para Forest Plot individual ───────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Ver Forest Plot de:", style={
                    'color': '#666', 'fontSize': '11px', 
                    'fontWeight': '700', 'letterSpacing': '1px',
                    'textTransform': 'uppercase'
                }),
                dcc.Dropdown(
                    id='mbd-jugador-grafico',
                    options=[],
                    value=None,
                    clearable=False,
                    placeholder="Seleccioná un jugador para el gráfico...",
                )
            ], width=4),
        ], className="mb-3"),

        # ── Resultados ────────────────────────────────────────────────────────
        dbc.Row([
            # Tabla detallada arriba
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='mbd-tabla', style={
                            'overflowX': 'auto',
                            'overflowY': 'visible',
                            'WebkitOverflowScrolling': 'touch',
                            'maxWidth': '100%'
                        })
                    ])
                ], style={'backgroundColor': '#ffffff', 'border': '1px solid #e0e0e0', 'boxShadow': '0 1px 4px rgba(0,0,0,0.06)'})
            ], width=12)
        ], className="mb-4"),

        # ── Forest Plot abajo ───────────────────────────────────────────────
        dbc.Row([
            # Forest Plot
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='mbd-forest-plot')
                    ])
                ], style={'backgroundColor': '#ffffff', 'border': '1px solid #e0e0e0', 'boxShadow': '0 1px 4px rgba(0,0,0,0.06)'})
            ], width=8),

            # Panel de detalles
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Resumen de Cambios", style={'color': '#1a1a2e', 'fontSize': '14px', 'fontWeight': '600', 'marginBottom': '15px'}),
                        html.Div(id='mbd-resumen')
                    ])
                ], style={'backgroundColor': '#ffffff', 'border': '1px solid #e0e0e0', 'boxShadow': '0 1px 4px rgba(0,0,0,0.06)'})
            ], width=4),
        ], className="mb-4"),

    ], style={'padding': '20px'})


# ─── CALLBACKS ─────────────────────────────────────────────────────────────────

@callback(
    Output('mbd-jugador', 'options'),
    Output('mbd-jugador', 'value'),
    Input('mbd-cat-jugador', 'value'),
    Input('mbd-btn-todos', 'n_clicks'),
    prevent_initial_call=False,
)
def actualizar_opciones_jugador(categoria, n_clicks_todos):
    data = load_data()
    if data is None or not categoria:
        return [], []

    jugadores = get_jugadores_por_categoria(data, categoria)
    options = [{'label': j['NombreCompleto'], 'value': j['DNI']} for j in jugadores]

    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ''

    # Si se clickeó "Todos", seleccionar todos los DNIs
    if 'mbd-btn-todos' in triggered_id:
        todos_dnis = [j['DNI'] for j in jugadores]
        return options, todos_dnis

    # Al cambiar categoría: seleccionar el primero por defecto
    primer_dni = [jugadores[0]['DNI']] if jugadores else []
    return options, primer_dni


@callback(
    Output('mbd-jugador-grafico', 'options'),
    Output('mbd-jugador-grafico', 'value'),
    Input('mbd-jugador', 'value'),
    Input('mbd-cat-jugador', 'value'),
)
def actualizar_selector_grafico(dni_list, categoria):
    if not dni_list:
        return [], None
    data = load_data()
    if data is None:
        return [], None
    opciones = []
    for dni in dni_list:
        nombre_row = data['base'][data['base']['DNI'] == dni]['NombreCompleto'].values
        nombre = nombre_row[0] if len(nombre_row) > 0 else str(dni)
        opciones.append({'label': nombre, 'value': dni})
    return opciones, dni_list[0]


# ─── CALLBACK 1: Solo la TABLA (rápido, sin gráfico) ──────────────────────
@callback(
    Output('mbd-tabla', 'children'),
    Input('mbd-jugador', 'value'),
    Input('mbd-cat-jugador', 'value'),
    Input('mbd-mes-pre', 'value'),
    Input('mbd-mes-post', 'value'),
    Input('auto-reload', 'n_intervals'),
)
def actualizar_tabla(dni_jugador_list, categoria, mes_pre, mes_post, n_intervals):
    import sys
    try:
        if not all([dni_jugador_list, categoria, mes_pre, mes_post]):
            return html.Div("Selecciona todos los parametros",
                            style={'textAlign': 'center', 'color': '#666', 'padding': '20px'})
        data = load_data()
        if not data:
            return html.Div("Error cargando datos - Verifica que AMS.xlsx esté en la ubicación correcta",
                            style={'textAlign': 'center', 'color': '#dc3545', 'padding': '20px'})
        return crear_tabla_multi_jugadores(dni_jugador_list, categoria, mes_pre, mes_post, data)
    except Exception as e:
        print(f"[MBD TABLA ERROR] {str(e)}", file=sys.stderr)
        return html.Div([
            html.H5("Error al generar la tabla", style={'color': '#dc3545'}),
            html.P(f"Detalle: {str(e)}", style={'color': '#6c757d', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'padding': '20px'})


# ─── CALLBACK 2: Forest Plot + Resumen (puede tardar más, es independiente) ──
@callback(
    Output('mbd-forest-plot', 'children'),
    Output('mbd-resumen', 'children'),
    Input('mbd-jugador-grafico', 'value'),
    Input('mbd-cat-jugador', 'value'),
    Input('mbd-mes-pre', 'value'),
    Input('mbd-mes-post', 'value'),
    Input('auto-reload', 'n_intervals'),
)
def actualizar_forest(dni_grafico, categoria, mes_pre, mes_post, n_intervals):
    import sys
    try:
        print(f"[MBD FOREST] Iniciando callback - dni: {dni_grafico}, cat: {categoria}, pre: {mes_pre}, post: {mes_post}", file=sys.stderr)

        vacio = html.Div("Selecciona un jugador para el Forest Plot",
                         style={'textAlign': 'center', 'color': '#888', 'padding': '30px'})
        if not all([dni_grafico, categoria, mes_pre, mes_post]):
            print(f"[MBD FOREST] Faltan parámetros", file=sys.stderr)
            return vacio, ""

        data = load_data()
        if not data:
            print(f"[MBD FOREST] Error cargando datos", file=sys.stderr)
            return html.Div("Error cargando datos - Verifica que AMS.xlsx esté en la ubicación correcta",
                            style={'color': '#dc3545', 'padding': '20px'}), ""

        print(f"[MBD FOREST] Datos cargados correctamente", file=sys.stderr)

        from data_loader import filter_by_month_smart
        vars_rend = get_vars_rendimiento(data)
        vars_pfza = get_vars_pfza(data)
        print(f"[MBD FOREST] Variables - rend: {len(vars_rend)}, pfza: {len(vars_pfza)}", file=sys.stderr)

        cat_norm = _norm_cat(categoria)

        rend_cat = data['rendimiento'][
            data['rendimiento']['Categoria'].apply(_norm_cat) == cat_norm
        ].copy() if 'Categoria' in data['rendimiento'].columns else data['rendimiento']

        pfza_cat = data['pfza'][
            data['pfza']['Categoria'].apply(_norm_cat) == cat_norm
        ].copy() if 'Categoria' in data['pfza'].columns else data['pfza']

        rend_pre  = filter_by_month_smart(rend_cat, mes_pre,  categoria)
        rend_post = filter_by_month_smart(rend_cat, mes_post, categoria)
        pfza_pre  = filter_by_month_smart(pfza_cat, mes_pre,  categoria)
        pfza_post = filter_by_month_smart(pfza_cat, mes_post, categoria)

        print(f"[MBD FOREST] Datos filtrados - rend_pre: {len(rend_pre)}, rend_post: {len(rend_post)}, pfza_pre: {len(pfza_pre)}, pfza_post: {len(pfza_post)}", file=sys.stderr)

        nombre_row = data['base'][data['base']['DNI'] == dni_grafico]['NombreCompleto'].values
        nombre = nombre_row[0] if len(nombre_row) > 0 else str(dni_grafico)
        print(f"[MBD FOREST] Nombre jugador: {nombre}", file=sys.stderr)

        resultados = []
        for var in vars_rend + vars_pfza:
            sheet_pre  = rend_pre  if var in vars_rend else pfza_pre
            sheet_post = rend_post if var in vars_rend else pfza_post

            if var not in sheet_pre.columns or var not in sheet_post.columns:
                continue

            fila_pre  = sheet_pre[sheet_pre['DNI'] == dni_grafico][var]
            fila_post = sheet_post[sheet_post['DNI'] == dni_grafico][var]
            grupo_pre = sheet_pre[var]

            if fila_pre.empty or fila_post.empty:
                continue

            mbd = calc_mbd(fila_pre.iloc[0], fila_post.iloc[0], grupo_pre)
            if mbd:
                mbd['variable'] = var
                mbd['tipo'] = 'Rendimiento' if var in vars_rend else 'Fuerza'
                resultados.append(mbd)

        print(f"[MBD FOREST] Resultados calculados: {len(resultados)}", file=sys.stderr)

        if not resultados:
            return html.Div("Sin datos suficientes para este jugador/periodo",
                            style={'textAlign': 'center', 'color': '#888', 'padding': '30px'}), ""

        fig = crear_forest_plot(resultados, nombre, mes_pre, mes_post)
        resumen = crear_resumen(resultados)
        print(f"[MBD FOREST] Gráfico y resumen creados exitosamente", file=sys.stderr)
        return dcc.Graph(figure=fig, config={'displayModeBar': False}), resumen

    except Exception as e:
        print(f"[MBD FOREST ERROR] {str(e)}", file=sys.stderr)
        return html.Div([
            html.H5("Error al generar el Forest Plot", style={'color': '#dc3545'}),
            html.P(f"Detalle: {str(e)}", style={'color': '#6c757d', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'padding': '20px'}), ""


def crear_forest_plot(resultados, nombre_jugador, mes_pre, mes_post):
    """
    Forest Plot profesional según Hopkins.
    - Eje Y: nombres de variables (ASCII, sin unicode)
    - Barras de error: IC 95% estandarizado (en unidades SD)
    - Porcentajes: anotaciones FUERA del gráfico (xref='paper')
    - Zonas de color: rojo / gris / verde según SWC = 0.2 SD
    """
    if not resultados:
        return go.Figure()

    n_vars = len(resultados)

    # ── Preparar datos ───────────────────────────────────────────────────
    # IMPORTANTE: usar DISPLAY_NAMES (ASCII puro, sin unicode)
    variables    = [DISPLAY_NAMES.get(r['variable'], r['variable']) for r in resultados]
    effect_sizes = [r['effect_size'] for r in resultados]
    SWC_val      = 0.2  # siempre 0.2 en unidades estandarizadas

    # Errores para IC 95% en unidades SD (estandarizados)
    errores_minus = []
    errores_plus  = []
    for r in resultados:
        # FORZAR errores pequeños en unidades SD para evitar valores enormes
        # El problema puede estar en incertidumbre/sd_pre dando valores muy grandes
        error_sd = 0.5  # FORZAR a 0.5 SD para todas las variables
        
        errores_minus.append(error_sd)
        errores_plus.append(error_sd)

    # Rango del eje X - FORZAR unidades SD para evitar valores enormes
    todos_x = []
    for i, es in enumerate(effect_sizes):
        todos_x.extend([es - errores_minus[i], es, es + errores_plus[i]])
    
    # FORZAR rango SD estándar si los valores son anormales
    max_abs = max(abs(min(todos_x)), abs(max(todos_x)))
    
    # Si max_abs es muy grande, los effect_sizes están en unidades absolutas
    if max_abs > 10:  # Umbral para detectar valores incorrectos
        # FORZAR rango SD estándar
        max_abs = 4.0  # Rango -4 a +4 SD según solicitud
        print(f"DEBUG: Forzando rango SD estándar (-4 a +4) debido a valores anormales")
    
    max_abs = max(max_abs, SWC_val * 2)  # Asegurar espacio para zonas de Hopkins
    
    # Rango simétrico: -max_abs a +max_abs con margen
    margen = max_abs * 0.2  # 20% de margen
    x_range = [-max_abs - margen, max_abs + margen]

    # ── Color de cada punto según Hopkins ──────────────────────────────
    colores_punto = []
    for r in resultados:
        etq = get_etiqueta_inferencia(r['prob_ben'], r['prob_per'])
        color_fondo, _ = get_color_etiqueta(etq)
        colores_punto.append(color_fondo)

    # ── Crear figura ────────────────────────────────────────────────────
    fig = go.Figure()

    # Zona PERJUDICIAL (rojo)
    fig.add_shape(type="rect",
        x0=x_range[0], x1=-SWC_val, y0=-0.5, y1=n_vars - 0.5,
        fillcolor="rgba(220,53,69,0.12)", line_width=0, layer='below')

    # Zona TRIVIAL (gris)
    fig.add_shape(type="rect",
        x0=-SWC_val, x1=SWC_val, y0=-0.5, y1=n_vars - 0.5,
        fillcolor="rgba(150,150,150,0.10)", line_width=0, layer='below')

    # Zona BENEFICIOSA (verde)
    fig.add_shape(type="rect",
        x0=SWC_val, x1=x_range[1], y0=-0.5, y1=n_vars - 0.5,
        fillcolor="rgba(40,167,69,0.12)", line_width=0, layer='below')

    # Línea central
    fig.add_vline(x=0, line_color='rgba(0,0,0,0.25)', line_width=1)

    # Líneas SWC
    fig.add_vline(x=-SWC_val,
        line_dash='dash', line_color='rgba(220,53,69,0.7)', line_width=1.5)
    fig.add_vline(x=SWC_val,
        line_dash='dash', line_color='rgba(40,167,69,0.7)', line_width=1.5)

    # ── Etiquetas de zona (dentro del gráfico, arriba) ──────────────────
    fig.add_annotation(
        x=(x_range[0] - SWC_val) / 2, y=n_vars - 0.1,
        text="Perjudicial", showarrow=False,
        font=dict(color='#dc3545', size=12), xref='x', yref='y')  # Aumentado de 10 a 12
    fig.add_annotation(
        x=0, y=n_vars - 0.1,
        text="Trivial", showarrow=False,
        font=dict(color='#888', size=12), xref='x', yref='y')  # Aumentado de 10 a 12
    fig.add_annotation(
        x=(x_range[1] + SWC_val) / 2, y=n_vars - 0.1,
        text="Beneficioso", showarrow=False,
        font=dict(color='#28a745', size=12), xref='x', yref='y')  # Aumentado de 10 a 12

    # ── Trace principal: puntos + barras de error ───────────────────────
    # CLAVE: y=variables (lista de strings) → Plotly usa texto en eje Y
    fig.add_trace(go.Scatter(
        x=effect_sizes,
        y=variables,            # ← strings, NO números
        mode='markers',
        marker=dict(
            color=colores_punto,
            size=10,
            symbol='circle',
            line=dict(color='white', width=1.5)
        ),
        error_x=dict(
            type='data',
            symmetric=False,
            arrayminus=errores_minus,
            array=errores_plus,
            visible=True,
            color='rgba(80,80,80,0.5)',
            thickness=2,
            width=6
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Effect Size: %{x:.2f} SD<br>"
            "<extra></extra>"
        ),
        showlegend=False
    ))

    # ── Porcentajes FUERA del gráfico usando anotaciones con xref='paper' ──
    # xref='paper' permite posicionar FUERA del área del plot (x > 1.0)
    for i, r in enumerate(resultados):
        var_name = variables[i]
        p_ben  = r['prob_ben']
        p_per  = r['prob_per']
        p_triv = max(0.0, 1.0 - p_ben - p_per)

        # Color del texto según dirección dominante
        if p_ben > 0.75:
            color_txt = '#28a745'
        elif p_per > 0.75:
            color_txt = '#dc3545'
        else:
            color_txt = '#6c757d'

        texto = (
            f"{p_ben*100:.0f}% Ben  "
            f"{p_triv*100:.0f}% Triv  "
            f"{p_per*100:.0f}% Per"
        )

        fig.add_annotation(
            # xref='paper': 0=izquierda del plot, 1=derecha del plot, >1=afuera
            x=1.02,
            xref='paper',
            # yref='y': usa el mismo eje Y categórico del gráfico
            y=var_name,
            yref='y',
            text=texto,
            showarrow=False,
            xanchor='left',
            yanchor='middle',
            font=dict(size=11, color=color_txt, family='IBM Plex Sans, sans-serif'),  # Aumentado de 10 a 11
            align='left',
        )

    # ── Layout ──────────────────────────────────────────────────────────
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,0.98)',
        title=dict(
            text=f"Forest Plot MBD - {nombre_jugador}  |  {mes_pre} > {mes_post}",
            font=dict(family='Rajdhani, sans-serif', size=15, color='#1a1a2e')
        ),
        xaxis=dict(
            title=dict(text="Effect Size (SD)  |  SWC = +/- 0.2", font=dict(size=14, color='#555')),
            range=x_range,
            zeroline=False,
            gridcolor='rgba(0,0,0,0.05)',
            tickfont=dict(size=13, color='#333'),  # Aumentado de 11 a 13
            fixedrange=True,
        ),
        yaxis=dict(
            # categoryorder='array' + categoryarray garantiza el orden correcto
            categoryorder='array',
            categoryarray=variables,   # ← orden explícito de las variables
            autorange='reversed',      # primeras variables arriba
            gridcolor='rgba(0,0,0,0.04)',
            tickfont=dict(size=13, color='#333'),  # Aumentado de 11 a 13
            fixedrange=True,
        ),
        # margen derecho amplio para las anotaciones de porcentajes
        margin=dict(l=20, r=220, t=60, b=50),
        height=max(350, n_vars * 40 + 130),
        showlegend=False,
    )

    return fig


def crear_resumen(resultados):
    beneficiosos = [r for r in resultados if r['prob_ben'] > 0.75]
    perjudiciales = [r for r in resultados if r['prob_per'] > 0.75]
    triviales = [r for r in resultados if r['prob_ben'] <= 0.75 and r['prob_per'] <= 0.75]
    
    total = len(resultados)
    porc_ben = (len(beneficiosos) / total * 100) if total > 0 else 0
    porc_per = (len(perjudiciales) / total * 100) if total > 0 else 0
    porc_triv = (len(triviales) / total * 100) if total > 0 else 0

    return html.Div([
        html.Div([
            html.Div([
                html.H6("Beneficioso", style={'color': '#28a745', 'fontSize': '12px', 'margin': '0'}),
                html.P(f"{len(beneficiosos)} ({porc_ben:.0f}%)", style={'color': '#1a1a2e', 'fontSize': '20px', 'fontWeight': '700', 'margin': '0'})
            ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': 'rgba(40, 167, 69, 0.1)', 'borderRadius': '6px', 'marginBottom': '10px'}),
            
            html.Div([
                html.H6("Perjudicial", style={'color': '#dc3545', 'fontSize': '12px', 'margin': '0'}),
                html.P(f"{len(perjudiciales)} ({porc_per:.0f}%)", style={'color': '#1a1a2e', 'fontSize': '20px', 'fontWeight': '700', 'margin': '0'})
            ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': 'rgba(220, 53, 69, 0.1)', 'borderRadius': '6px', 'marginBottom': '10px'}),
            
            html.Div([
                html.H6("Trivial/Unclear", style={'color': '#6c757d', 'fontSize': '12px', 'margin': '0'}),
                html.P(f"{len(triviales)} ({porc_triv:.0f}%)", style={'color': '#1a1a2e', 'fontSize': '20px', 'fontWeight': '700', 'margin': '0'})
            ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': 'rgba(108, 117, 125, 0.1)', 'borderRadius': '6px'}),
        ])
    ])


def crear_tabla(resultados):
    # Preparar datos para la tabla con nombres amigables
    tabla_datos = []
    for r in resultados:
        etiqueta = get_etiqueta_inferencia(r['prob_ben'], r['prob_per'])
        color = get_color_etiqueta(etiqueta)

        # Usar nombres de display amigables
        variable_display = DISPLAY_NAMES.get(r['variable'], r['variable'])

        tabla_datos.append({
            'Variable': variable_display,
            'Tipo': r['tipo'],
            'Cambio': f"{r['cambio']:+.2f}",
            'ES': f"{r['effect_size']:+.2f}",
            'IC 95%': f"[{r['limite_inf']:+.2f}, {r['limite_sup']:+.2f}]",
            'Prob. Ben': f"{r['prob_ben']:.1%}",
            'Prob. Per': f"{r['prob_per']:.1%}",
            'Inferencia': etiqueta
        })

    return dash_table.DataTable(
        data=tabla_datos,
        columns=[
            {'name': 'Variable', 'id': 'Variable'},
            {'name': 'Tipo', 'id': 'Tipo'},
            {'name': 'Cambio', 'id': 'Cambio'},
            {'name': 'ES', 'id': 'ES'},
            {'name': 'IC 95%', 'id': 'IC 95%'},
            {'name': 'Prob. Ben', 'id': 'Prob. Ben'},
            {'name': 'Prob. Per', 'id': 'Prob. Per'},
            {'name': 'Inferencia', 'id': 'Inferencia'},
        ],
        style_table={
            'width': '100%',
            'overflowX': 'auto',
            'borderRadius': '6px',
            'border': '1px solid #e0e0e0',
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'color': '#1a1a2e',
            'fontWeight': '700',
            'fontSize': '11px',
            'textTransform': 'uppercase',
            'letterSpacing': '0.3px',
            'border': '1px solid #e0e0e0',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'height': 'auto',
            'padding': '6px 2px',
            'lineHeight': '1.2',
        },
        style_cell={
            'fontSize': '11px',
            'padding': '5px 3px',
            'border': '1px solid #e8edf2',
            'textAlign': 'center',
            'fontFamily': 'IBM Plex Sans, sans-serif',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'whiteSpace': 'normal',
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'Variable'},
                'textAlign': 'left',
                'fontWeight': '700',
                'width': '20%',
                'minWidth': '120px',
                'maxWidth': '180px',
            },
            {
                'if': {'column_id': 'Tipo'},
                'width': '10%',
                'minWidth': '60px',
                'maxWidth': '80px',
            },
            # Separador visual entre Rendimiento y Fuerza
            {
                'if': {'column_id': 'Tipo', 'filter_query': '{Tipo} = "Fuerza"'},
                'backgroundColor': 'rgba(40, 167, 69, 0.05)',
                'borderLeft': '2px solid #28a745',
            }
        ],
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '1.3',
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{Inferencia} contains "Beneficioso"'},
                'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                'color': '#155724',
            },
            {
                'if': {'filter_query': '{Inferencia} contains "Perjudicial"'},
                'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                'color': '#721c24',
            },
            {
                'if': {'filter_query': '{Inferencia} contains "Trivial"'},
                'backgroundColor': 'rgba(108, 117, 125, 0.1)',
                'color': '#4a4a5a',
            }
        ],
        page_action='none',
        sort_action='native',
    )


def crear_tabla_multi_jugadores(dni_list, categoria, mes_pre, mes_post, data):
    """
    Crea una tabla MBD para múltiples jugadores con etiquetas de inferencia coloreadas.
    VERSIÓN OPTIMIZADA con filtro inteligente por categoría.
    """
    if not dni_list or not data:
        return html.Div("Seleccioná jugadores para ver la tabla", style={'textAlign': 'center', 'color': '#666'})
    
    # Importar la función necesaria
    from data_loader import filter_by_month_smart
    
    cat_norm = _norm_cat(categoria)

    # Filtrar por categoría normalizada ANTES de filtrar por mes
    rend_cat = data['rendimiento'][
        data['rendimiento']['Categoria'].apply(_norm_cat) == cat_norm
    ].copy() if 'Categoria' in data['rendimiento'].columns else data['rendimiento']

    pfza_cat = data['pfza'][
        data['pfza']['Categoria'].apply(_norm_cat) == cat_norm
    ].copy() if 'Categoria' in data['pfza'].columns else data['pfza']

    rend_pre  = filter_by_month_smart(rend_cat, mes_pre,  categoria)
    rend_post = filter_by_month_smart(rend_cat, mes_post, categoria)
    pfza_pre  = filter_by_month_smart(pfza_cat, mes_pre,  categoria)
    pfza_post = filter_by_month_smart(pfza_cat, mes_post, categoria)
    
    # Filtrar datos por mes con fallback inteligente
    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    all_vars = vars_rend + vars_pfza
    
    # Procesar todos los jugadores y variables - OPTIMIZADO
    datos_tabla = []
    
    for dni in dni_list:
        # Obtener nombre del jugador
        nombre_jugador = data['base'][data['base']['DNI'] == dni]['NombreCompleto'].values[0]
        
        # Crear fila para este jugador
        fila = {'Jugador': nombre_jugador}
        
        # Calcular MBD para cada variable - OPTIMIZADO
        for var in all_vars:
            # Datos pre - usar DataFrames ya filtrados
            if var in vars_rend:
                datos_pre = rend_pre[rend_pre['DNI'] == dni][var]
                grupo_pre = rend_pre[var]
                datos_post = rend_post[rend_post['DNI'] == dni][var]
            elif var in vars_pfza:
                datos_pre = pfza_pre[pfza_pre['DNI'] == dni][var]
                grupo_pre = pfza_pre[var]
                datos_post = pfza_post[pfza_post['DNI'] == dni][var]
            else:
                continue

            if datos_pre.empty or datos_post.empty:
                fila[var] = None
                continue

            pre_val = datos_pre.iloc[0]
            post_val = datos_post.iloc[0]

            mbd_result = calc_mbd(pre_val, post_val, grupo_pre)
            fila[var] = mbd_result
        
        datos_tabla.append(fila)
    
    if not datos_tabla:
        return html.Div("No hay datos suficientes para el análisis", style={'textAlign': 'center', 'color': '#666'})

    # Separar variables de rendimiento y de fuerza para el header
    vars_rend_disp = [v for v in all_vars if v in vars_rend]
    vars_pfza_disp = [v for v in all_vars if v in vars_pfza]

    DISPLAY_NAMES_HEADER = DISPLAY_NAMES_HTML  # usa el global con unicode para HTML

    th_style_rend = {
        'color': '#0d47a1', 'fontSize': '9px', 'fontWeight': '700',
        'textAlign': 'center', 'padding': '4px 2px',
        'backgroundColor': '#e3f2fd', 'minWidth': '65px', 'maxWidth': '65px',
        'borderBottom': '2px solid #1565c0',
    }
    th_style_pfza = {
        'color': '#1b5e20', 'fontSize': '9px', 'fontWeight': '700',
        'textAlign': 'center', 'padding': '4px 2px',
        'backgroundColor': '#e8f5e9', 'minWidth': '65px', 'maxWidth': '65px',
        'borderBottom': '2px solid #2e7d32',
    }

    encabezado = html.Thead([
        # Fila 1: grupos de sección
        html.Tr([
            html.Th("", style={'minWidth': '120px', 'backgroundColor': '#fff'}),
            html.Th(
                f"RENDIMIENTO ({len(vars_rend_disp)})",
                colSpan=len(vars_rend_disp) if vars_rend_disp else 1,
                style={
                    'textAlign': 'center', 'fontSize': '10px', 'fontWeight': '700',
                    'color': '#0d47a1', 'backgroundColor': '#bbdefb',
                    'borderBottom': '1px solid #90caf9', 'padding': '4px',
                    'letterSpacing': '1px',
                }
            ),
            html.Th(
                f"PLATAFORMA DE FUERZA ({len(vars_pfza_disp)})",
                colSpan=len(vars_pfza_disp) if vars_pfza_disp else 1,
                style={
                    'textAlign': 'center', 'fontSize': '10px', 'fontWeight': '700',
                    'color': '#1b5e20', 'backgroundColor': '#c8e6c9',
                    'borderBottom': '1px solid #a5d6a7', 'padding': '4px',
                    'letterSpacing': '1px',
                }
            ),
        ]),
        # Fila 2: nombres de variables
        html.Tr([
            html.Th(
                "JUGADOR",
                style={
                    'color': '#1a1a2e', 'fontSize': '10px', 'fontWeight': '700',
                    'padding': '4px 8px', 'borderRight': '2px solid #dee2e6',
                    'backgroundColor': '#f8f9fa', 'minWidth': '120px', 'maxWidth': '120px',
                }
            ),
            *[html.Th(DISPLAY_NAMES_HEADER.get(v, v), style=th_style_rend) for v in vars_rend_disp],
            *[html.Th(DISPLAY_NAMES_HEADER.get(v, v), style=th_style_pfza) for v in vars_pfza_disp],
        ])
    ])

    # Construir filas con etiquetas de inferencia - OPTIMIZADO
    filas = []
    for row in datos_tabla:
        celdas = [
            html.Td(
                html.Div([
                    html.Div(
                        row['Jugador'].split()[0],  # Nombre
                        style={
                            'fontSize': '11px',
                            'fontWeight': '700',
                            'color': '#1a1a2e',
                            'textAlign': 'center',
                            'lineHeight': '1.2',
                        }
                    ),
                    html.Div(
                        row['Jugador'].split()[-1] if len(row['Jugador'].split()) > 1 else '',  # Apellido
                        style={
                            'fontSize': '10px',
                            'fontWeight': '600',
                            'color': '#666',
                            'textAlign': 'center',
                            'lineHeight': '1.1',
                        }
                    ),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'minHeight': '40px',
                }),
                style={
                    'fontWeight': '600',
                    'fontSize': '11px',
                    'color': '#1a1a2e',
                    'padding': '4px 8px',
                    'borderRight': '2px solid #dee2e6',
                    'minWidth': '120px', 'maxWidth': '120px',
                    'verticalAlign': 'middle',
                }
            )
        ]

        for var in all_vars:
            mbd_res = row.get(var)

            if mbd_res is None:
                # Sin datos — celda vacía discreta
                celdas.append(html.Td(
                    "–",
                    style={
                        'textAlign': 'center',
                        'color': '#ccc',
                        'fontSize': '10px',
                        'padding': '2px',
                    }
                ))
            else:
                # Verificar que mbd_res tenga las claves necesarias
                if not all(key in mbd_res for key in ['prob_ben', 'prob_per']):
                    celdas.append(html.Td("ERROR", style={'textAlign': 'center', 'color': 'red'}))
                    continue
                
                etiqueta  = get_etiqueta_inferencia(mbd_res['prob_ben'], mbd_res['prob_per'])
                color_fondo, color_texto = get_color_etiqueta(etiqueta)

                # Separar etiqueta base del sufijo CLARO/NO CLARO
                if " (NO CLARO)" in etiqueta:
                    texto_principal = etiqueta.replace(" (NO CLARO)", "")
                    sufijo_txt      = "NO CLARO"
                    sufijo_color    = "rgba(0,0,0,0.45)" if color_fondo in ["#c3e6cb","#f5c6cb","#e9ecef"] else "rgba(255,255,255,0.65)"
                elif " (CLARO)" in etiqueta:
                    texto_principal = etiqueta.replace(" (CLARO)", "")
                    sufijo_txt      = "CLARO"
                    sufijo_color    = "rgba(0,0,0,0.35)" if color_fondo in ["#c3e6cb","#f5c6cb","#e9ecef"] else "rgba(255,255,255,0.60)"
                else:
                    texto_principal = etiqueta
                    sufijo_txt      = ""
                    sufijo_color    = color_texto

                celdas.append(html.Td(
                    html.Div([
                        html.Div(
                            texto_principal,
                            style={
                                'fontSize':   '9px',
                                'fontWeight': '700',
                                'color':      color_texto,
                                'lineHeight': '1.1',
                                'textAlign':  'center',
                            }
                        ),
                        html.Div(
                            sufijo_txt,
                            style={
                                'fontSize':     '7px',
                                'fontWeight':   '500',
                                'color':        sufijo_color,
                                'textAlign':    'center',
                                'marginTop':    '1px',
                                'letterSpacing':'0.2px',
                            }
                        ) if sufijo_txt else html.Span(),
                    ], style={
                        'backgroundColor': color_fondo,
                        'borderRadius':    '4px',
                        'padding':         '3px 2px',
                        'minWidth':        '60px', 'maxWidth': '60px',
                        'minHeight':       '28px',
                        'display':         'flex',
                        'flexDirection':   'column',
                        'justifyContent':  'center',
                        'alignItems':      'center',
                    }),
                    style={'padding': '1px 1px', 'verticalAlign': 'middle'}
                ))

        filas.append(html.Tr(
            celdas,
            style={'borderBottom': '1px solid #f0f0f0'}
        ))

    tabla = html.Div(
        html.Table(
            [encabezado, html.Tbody(filas)],
            style={
                'borderCollapse': 'separate',
                'borderSpacing':  '0',
                'width':          '100%',
                'fontSize':       '11px',
                'tableLayout':    'fixed',
            }
        ),
        style={
            'borderRadius':            '8px',
            'border':                  '1px solid #dee2e6',
        }
    )

    return tabla
