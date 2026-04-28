import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from dash import dash_table
from data_loader import load_data, get_available_months
import plotly.graph_objects as go
import logging

# Configurar logging robusto para evitar OSError en Windows
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ─── FUNCIONES AUXILIARES DE ESTILO ──────────────────────────────────────────

def legend_cell(text, is_range=False):
    """Genera una celda de estilo estándar para la leyenda"""
    base_style = {
        'fontSize': '11px',
        'padding': '4px',
        'border': '1px solid #dee2e6',
        'textAlign': 'center'
    }
    if is_range:
        base_style['fontWeight'] = 'bold'
        base_style['backgroundColor'] = '#f8f9fa'
        base_style['color'] = '#495057'
    return base_style

def get_row_styles(range_txt, class_txt, bg_color, text_color):
    """Genera las celdas HTML para una fila de la leyenda"""
    return [
        html.Td(range_txt, style={**legend_cell("", True), 'backgroundColor': bg_color, 'color': text_color}),
        html.Td(class_txt, style={**legend_cell(""), 'backgroundColor': bg_color, 'color': text_color})
    ]

def color_fondo(z):
    """Color de fondo de la celda según clasificación Hopkins/Z-Score."""
    if z is None or (isinstance(z, float) and np.isnan(z)):
        return '#f8f9fa'
    if z > 2.0:
        return '#1a6e1a'    # Verde Oscuro  — Excelente
    if z > 1.0:
        return '#4CAF50'    # Verde         — Muy Bueno
    if z > 0.5:
        return '#A8D08D'    # Verde Claro   — Bueno
    if z >= -0.5:
        return '#FFFFFF'    # Blanco        — Promedio (Estable)
    if z >= -1.0:
        return '#FFD600'    # Amarillo      — Debajo del Promedio
    if z >= -2.0:
        return '#FF9800'    # Naranja       — Pobre
    if z >= -3.0:
        return '#E53935'    # Rojo          — Muy Pobre
    return '#8B0000'        # Rojo Oscuro   — Extremadamente Pobre

def color_texto(z):
    """
    Color del número en la celda.
    Fondo oscuro → texto blanco.
    Fondo claro  → texto oscuro.
    """
    if z is None or (isinstance(z, float) and np.isnan(z)):
        return '#aaaaaa'
    if z > 2.0:
        return '#ffffff'    # Verde Oscuro  → texto blanco
    if z > 1.0:
        return '#ffffff'    # Verde         → texto blanco
    if z > 0.5:
        return '#1a1a2e'    # Verde Claro   → texto oscuro
    if z >= -0.5:
        return '#1a1a2e'    # Blanco        → texto oscuro
    if z >= -1.0:
        return '#1a1a2e'    # Amarillo      → texto oscuro
    if z >= -2.0:
        return '#ffffff'    # Naranja       → texto blanco
    if z >= -3.0:
        return '#ffffff'    # Rojo          → texto blanco
    return '#ffffff'        # Rojo Oscuro   → texto blanco

def color_barra(z):
    """Color de las barras del gráfico, misma escala que la tabla."""
    if z is None or (isinstance(z, float) and np.isnan(z)):
        return 'rgba(200,200,200,0.4)'
    if z > 2.0:   return '#1a6e1a'
    if z > 1.0:   return '#4CAF50'
    if z > 0.5:   return '#A8D08D'
    if z >= -0.5: return '#E0E0E0'
    if z >= -1.0: return '#FFD600'
    if z >= -2.0: return '#FF9800'
    if z >= -3.0: return '#E53935'
    return '#8B0000'


# ─── LAYOUT ───────────────────────────────────────────────────────────────────

def layout():
    try:
        data = load_data()
        if data is None:
            return dbc.Alert("❌ Error crítico: No se pudo cargar AMS.xlsx. Verificá la ruta del archivo.", color="danger")

        # Obtener categorías directamente
        categorias = sorted(data['base']['Categoria'].unique()) if data.get('base') is not None else []
        cat_options = [{'label': c, 'value': c} for c in categorias]
        
        meses = get_available_months(data)
        month_options = [{'label': m, 'value': m} for m in meses]
    except Exception as e:
         return dbc.Alert(f"❌ Error al inicializar datos: {str(e)}", color="danger")

    return html.Div([
        # Stores para datos
        dcc.Store(id='zs-data-store'),
        dcc.Store(id='zs-jugadores-store'),
        
        # Título
        html.Div([
            html.H3("🔬 Z-Score — Extrapolar Datos", style={
                'fontFamily': 'Rajdhani, sans-serif', 'fontWeight': '700',
                'color': '#007bff', 'marginBottom': '4px', 'letterSpacing': '1px'
            }),
            html.P("Compará el perfil de un jugador contra categorías como referencia.",
                   style={'color': '#6c757d', 'fontSize': '13px', 'marginBottom': '20px'}),
        ]),

        # ── Filtros ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Mes", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dcc.Dropdown(id='zs-mes', options=month_options, value=meses[-1] if meses else None, clearable=False)
            ], width=2),
            dbc.Col([
                html.Label("Categoría Jugador", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dcc.Dropdown(id='zs-cat-jugador', options=cat_options, value=categorias[0] if categorias else None, clearable=False)
            ], width=3),
            dbc.Col([
                html.Label("Jugadores", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dbc.Row([
                    dbc.Col(dcc.Dropdown(id='zs-jugadores', multi=True, placeholder="Seleccioná..."), width=9),
                    dbc.Col(dbc.Button("Todos", id='zs-btn-todos', color="outline-secondary", size="sm", style={'width': '100%'}), width=3),
                ], className="g-1"),
            ], width=4),
            dbc.Col([
                html.Label("Comparar vs", style={'fontSize': '11px', 'textTransform': 'uppercase', 'color': '#6c757d'}),
                dcc.Dropdown(id='zs-cat-comparar', options=cat_options, value=categorias[0] if categorias else None, clearable=False)
            ], width=3),
        ], className="mb-4"),

        # ── Cuadro de Clasificación Z-Score (CORREGIDO SEGÚN IMAGEN 4) ───────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H6("📊 Clasificación Z-Score (Niveles Visuales)", style={
                            'color': '#ffffff', 'fontSize': '14px', 'fontWeight': '600', 'margin': '0', 'textAlign': 'center'
                        })
                    ], style={'backgroundColor': '#007bff', 'borderBottom': 'none', 'borderRadius': '8px 8px 0 0'}),
                    dbc.CardBody([
                        html.Div([
                            # Tabla 4 columnas x 4 filas para ser compacta
                            html.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Z-Score", style={**legend_cell("", True), 'backgroundColor': '#f1f3f5'}),
                                        html.Th("Clasificación", style={**legend_cell(""), 'backgroundColor': '#f1f3f5'}),
                                        html.Th("Z-Score", style={**legend_cell("", True), 'backgroundColor': '#f1f3f5'}),
                                        html.Th("Clasificación", style={**legend_cell(""), 'backgroundColor': '#f1f3f5'})
                                    ])
                                ]),
                                html.Tbody([
                                    # Fila 1: Excelente vs Debajo Promedio
                                    html.Tr(
                                        get_row_styles("> 2.0", "Excelente", "#006400", "white") + # Verde Oscuro
                                        get_row_styles("-1.0 a -0.5", "Debajo del Promedio", "#FFFF99", "black") # Amarillo
                                    ),
                                    # Fila 2: Muy Bueno vs Pobre
                                    html.Tr(
                                        get_row_styles("1.0 a 2.0", "Muy Bueno", "#228B22", "white") + # Verde
                                        get_row_styles("-2.0 a -1.0", "Pobre", "#FF9933", "white") # Naranja (actualizado)
                                    ),
                                    # Fila 3: Bueno vs Muy Pobre
                                    html.Tr(
                                        get_row_styles("0.5 a 1.0", "Bueno", "#32CD32", "white") + # Verde Claro
                                        get_row_styles("-3.0 a -2.0", "Muy Pobre", "#CC0000", "white") # Rojo
                                    ),
                                    # Fila 4: Promedio vs Extremadamente Pobre
                                    html.Tr(
                                        get_row_styles("-0.5 a 0.5", "Promedio (Estable)", "#FFFFFF", "black") + # Blanco
                                        get_row_styles("< -3.0", "Extremadamente Pobre", "#8B0000", "white") # Rojo Oscuro (actualizado)
                                    )
                                ])
                            ], style={'width': '100%', 'maxWidth': '700px', 'margin': '0 auto', 'borderCollapse': 'collapse'})
                        ], style={'textAlign': 'center'})
                    ], style={'padding': '10px', 'backgroundColor': '#ffffff'})
                ], style={'border': 'none', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,123,255,0.1)', 'marginBottom': '10px'})
            ], width=12)
        ], className="mb-2"),

        # Tabla de ancho completo visible
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='zs-info-comparacion'),
                        html.Div(id='zs-tabla-container', children=[
                            dash_table.DataTable(
                                id='zs-tabla',
                                columns=[],
                                data=[],
                                style_table={
                                    'width': '100%',
                                    'overflowX': 'hidden',
                                    'borderRadius': '6px',
                                    'border': '1px solid #dee2e6',
                                },
                                style_header={
                                    'backgroundColor': '#f0f4f8',
                                    'color': '#1a3a5c',
                                    'fontWeight': '700',
                                    'fontSize': '10px',
                                    'textTransform': 'uppercase',
                                    'letterSpacing': '0.3px',
                                    'border': '1px solid #dee2e6',
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
                                        'if': {'column_id': 'Jugador'},
                                        'textAlign': 'left',
                                        'fontWeight': '700',
                                        'width': '14%',
                                        'minWidth': '120px',
                                        'maxWidth': '160px',
                                    }
                                ],
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '1.3',
                                },
                                style_data_conditional=[],
                                page_action='none',
                                sort_action='native',
                            )
                        ], style={'minHeight': '200px'})
                    ])
                ], style={'border': 'none', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.08)'})
            ], width=12)
        ], className="mb-4"),

        # ── Gráfico Radar ────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H6("🕸️ Perfil Radar Z-Score", style={
                            'color': '#ffffff',
                            'fontSize': '14px',
                            'fontWeight': '600',
                            'margin': '0',
                            'textAlign': 'center'
                        })
                    ], style={
                        'backgroundColor': '#1a3a5c',
                        'borderBottom': 'none',
                        'borderRadius': '8px 8px 0 0'
                    }),
                    dbc.CardBody([
                        dcc.Graph(
                            id='zs-radar',
                            config={'displayModeBar': False},
                            style={'height': '650px'}
                        )
                    ], style={'padding': '12px', 'backgroundColor': '#ffffff'})
                ], style={
                    'border': 'none',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'marginBottom': '16px'
                })
            ], width=12)
        ]),
    ])


# ─── CALLBACKS OPTIMIZADOS ────────────────────────────────────────────────────────────────

@callback(
    Output('zs-data-store', 'data'),
    Output('zs-jugadores-store', 'data'),
    Input('zs-cat-jugador', 'value'),
)
def cargar_datos_cacheados(cat_jugador):
    try:
        logger.debug(f"Cargando datos para categoría: {cat_jugador}")
        data = load_data()
        if data is None or data.get('base') is None: 
            logger.debug("No se pudieron cargar los datos")
            return {}, []
        
        logger.debug(f"Datos cargados - base: {len(data['base'])}, rendimiento: {len(data['rendimiento'])}, pfza: {len(data['pfza'])}")
        
        jugadores_data = []
        base_df = data['base']
        
        # Preparar datos de jugadores rápidamente
        for _, row in base_df.iterrows():
            jugadores_data.append({
                'dni': row['DNI'],
                'nombre': row['NombreCompleto'],
                'categoria': row['Categoria']
            })
        
        logger.debug(f"Jugadores procesados: {len(jugadores_data)}")
        
        return {
            'base': data['base'].to_dict('records'),
            'rendimiento': data['rendimiento'].to_dict('records'),
            'pfza': data['pfza'].to_dict('records')
        }, jugadores_data
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return {}, []

@callback(
    Output('zs-jugadores', 'options'),
    Output('zs-jugadores', 'value'),
    Input('zs-cat-jugador', 'value'),
    Input('zs-btn-todos', 'n_clicks'),
    State('zs-jugadores-store', 'data'),
    State('zs-jugadores', 'value'),
    prevent_initial_call=False  # CAMBIADO: Permitir ejecución inicial
)
def actualizar_jugadores(cat_jugador, n_clicks_todos, jugadores_data, current_values):
    logger.debug(f"ACTUALIZAR JUGADORES - categoría: {cat_jugador}, clicks: {n_clicks_todos}")
    logger.debug(f"ACTUALIZAR JUGADORES - data: {len(jugadores_data) if jugadores_data else 0}, values: {len(current_values) if current_values else 0}")
    logger.debug(f"ACTUALIZAR JUGADORES - jugadores_data type: {type(jugadores_data)}")
    
    if not jugadores_data or not cat_jugador: 
        logger.debug("No hay jugadores_data o categoría")
        return [], []
    
    # Filtrado jerárquico por categoría (NO por mes)
    jugadores_filtrados = [j for j in jugadores_data if j['categoria'] == cat_jugador]
    
    logger.debug(f"Jugadores filtrados por categoría: {len(jugadores_filtrados)}")
    
    options = [{'label': j['nombre'], 'value': j['dni']} for j in jugadores_filtrados]
    
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    logger.debug(f"Triggered ID: {triggered_id}")
    
    if triggered_id == 'zs-btn-todos':
        # Botón pulsado: seleccionar todos los filtrados
        values = [j['dni'] for j in jugadores_filtrados]
        logger.debug(f"Botón Todos pulsado - seleccionando {len(values)} jugadores")
        return options, values
    else:
        # Selección normal: mantener o limpiar según corresponda
        if current_values is None:
            current_values = []
        
        # Filtrar valores actuales para que solo incluyan jugadores de esta categoría
        valores_filtrados = [v for v in current_values if v in [j['dni'] for j in jugadores_filtrados]]
        
        logger.debug(f"Manteniendo selección: {len(valores_filtrados)} jugadores")
        return options, valores_filtrados

@callback(
    Output('zs-info-comparacion', 'children'),
    Output('zs-tabla', 'data'),
    Output('zs-tabla', 'columns'),
    Output('zs-tabla', 'style_data_conditional'),
    Input('zs-jugadores', 'value'),
    Input('zs-cat-comparar', 'value'),
    Input('zs-mes', 'value'),
    State('zs-data-store', 'data'),
)
def actualizar_zscore_optimizado(dni_list, cat_comparar, mes_seleccionado, data_cache):
    try:
        # Inicializar variables antes de cualquier logging
        modo_individual = len(dni_list) == 1
        es_todos = []
        
        # Validaciones rápidas primero
        if not dni_list or not cat_comparar or not data_cache or not mes_seleccionado:
            logger.debug("Validación fallida - faltan datos")
            return html.P("Seleccioná jugadores, categoría de referencia y mes", 
                          style={'color': '#6c757d', 'textAlign': 'center', 'marginTop': '50px'}), [], [], []

        logger.debug(f"Callback iniciado - jugadores: {len(dni_list)}, comparar: {cat_comparar}, mes: {mes_seleccionado}, modo_individual: {modo_individual}")
        
        # Reconstruir DataFrames
        base = pd.DataFrame(data_cache['base'])
        rend = pd.DataFrame(data_cache['rendimiento'])
        pfza = pd.DataFrame(data_cache['pfza'])
        
        logger.debug(f"DataFrames reconstruidos - base: {len(base)}, rendimiento: {len(rend)}, pfza: {len(pfza)}")
        
        # Convertir fechas y filtrar por mes
        rend['Fecha'] = pd.to_datetime(rend['Fecha'], errors='coerce')
        pfza['Fecha'] = pd.to_datetime(pfza['Fecha'], errors='coerce')
        rend = rend[rend['Fecha'].dt.strftime('%Y-%m') == mes_seleccionado]
        pfza = pfza[pfza['Fecha'].dt.strftime('%Y-%m') == mes_seleccionado]
        
        logger.debug(f"Datos filtrados por mes {mes_seleccionado} - rendimiento: {len(rend)}, pfza: {len(pfza)}")

        # Variables en orden solicitado
        vars_especificas = [
            'VO2 max', 'F0', 'Pmax', 'Vmax', 'RF', 'DRF', 'Fuerza',
            'Potencia Pico', 'Altura Salto', 'Fuerza IMTP', 'RFD Dec',
            'RFD 100', 'RFD 150', 'RFD 250'
        ]
        
        # Filtrar datos de referencia
        rend_comp = rend[rend['Categoria'] == cat_comparar]
        pfza_comp = pfza[pfza['Categoria'] == cat_comparar]
        
        logger.debug(f"Datos de referencia para {cat_comparar} - rendimiento: {len(rend_comp)}, pfza: {len(pfza_comp)}")
        
        if rend_comp.empty and pfza_comp.empty:
            logger.debug("No hay datos de referencia")
            return html.P(f"No hay datos de referencia para {cat_comparar} en {mes_seleccionado}.", 
                          style={'color': '#dc3545', 'textAlign': 'center', 'padding': '20px'}), [], [], []

        # Determinar variables disponibles
        vars_disponibles = [v for v in vars_especificas if v in rend_comp.columns or v in pfza_comp.columns]
        
        logger.debug(f"Variables disponibles: {vars_disponibles}")

        # Calcular estadísticas de referencia (vectorizado)
        ref_stats = {}
        for var in vars_disponibles:
            df_comp = rend_comp if var in rend_comp.columns else pfza_comp
            data_var = df_comp[var].replace(0, np.nan).dropna() # Evitar ceros en referencia
            if len(data_var) > 1 and data_var.std() > 0.001:
                ref_stats[var] = (data_var.mean(), data_var.std())

        # Filtrar datos de los jugadores seleccionados
        jugadores_sel = base[base['DNI'].isin(dni_list)]
        rend_jugadores = rend[rend['DNI'].isin(dni_list)]
        pfza_jugadores = pfza[pfza['DNI'].isin(dni_list)]
        
        logger.debug(f"Jugadores seleccionados: {len(jugadores_sel)}")
        logger.debug(f"Datos jugadores - rendimiento: {len(rend_jugadores)}, pfza: {len(pfza_jugadores)}")
        
        # Cálculo de Z-scores
        resultados = []
        for _, jugador in jugadores_sel.iterrows():
            dni = jugador['DNI']
            fila = {'Jugador': jugador['NombreCompleto']}
            tiene_datos = False
            
            for var, (media, std) in ref_stats.items():
                df_j = rend_jugadores if var in rend_comp.columns else pfza_jugadores
                val_j = df_j[df_j['DNI'] == dni][var]
                if not val_j.empty:
                    fila[var] = round((val_j.iloc[0] - media) / std, 2)
                    tiene_datos = True
                else:
                    fila[var] = np.nan
            
            if tiene_datos:
                resultados.append(fila)

        logger.debug(f"Resultados calculados: {len(resultados)}")
        logger.debug(f"Primer resultado: {resultados[0] if resultados else 'No hay resultados'}")

        if not resultados:
            logger.debug("No hay resultados - todos los jugadores sin datos")
            return html.P(f"No se encontraron mediciones para los jugadores seleccionados en {mes_seleccionado}.", 
                          style={'color': '#6c757d', 'textAlign': 'center', 'padding': '20px'}), [], [], []

        # ── PREPARAR DATOS (números como float, NaN como None) ───────────────
        df_res = pd.DataFrame(resultados)
        datos_tabla = []
        for r in df_res.to_dict('records'):
            row = {}
            for k, v in r.items():
                if k == 'Jugador':
                    row[k] = v
                elif v is None or (isinstance(v, float) and np.isnan(v)):
                    row[k] = None   # None = celda vacía en DataTable
                else:
                    row[k] = round(float(v), 2)
            datos_tabla.append(row)

        # ── COLUMNAS ─────────────────────────────────────────────────────────
        columnas_dt = [{'name': 'JUGADOR', 'id': 'Jugador', 'type': 'text'}]
        for var in vars_disponibles:
            if var in ref_stats:
                columnas_dt.append({
                    'name': var,
                    'id': var,
                    'type': 'numeric',
                    'format': {'specifier': '.2f'}
                })

        # ── COLORES CONDICIONALES ─────────────────────────────────────────────
        # Cada regla usa rangos exclusivos para que solo un color aplique por celda.
        # Fondo oscuro → texto blanco | Fondo claro → texto oscuro
        reglas_color = [
            # (filter_query_template, fondo, texto)
            ('{%s} > 2',                             '#1a6e1a', '#ffffff'),  # Excelente
            ('{%s} >= 1 && {%s} <= 2',               '#4CAF50', '#ffffff'),  # Muy Bueno
            ('{%s} >= 0.5 && {%s} < 1',              '#A8D08D', '#1a1a2e'),  # Bueno
            ('{%s} >= -0.5 && {%s} < 0.5',           '#FFFFFF', '#1a1a2e'),  # Promedio (Estable)
            ('{%s} >= -1 && {%s} < -0.5',            '#FFD600', '#1a1a2e'),  # Debajo del Promedio
            ('{%s} >= -2 && {%s} < -1',              '#FF9800', '#ffffff'),  # Pobre
            ('{%s} >= -3 && {%s} < -2',              '#E53935', '#ffffff'),  # Muy Pobre
            ('{%s} < -3',                             '#8B0000', '#ffffff'),  # Extremadamente Pobre
        ]

        style_conditional = [
            # Columna Jugador
            {
                'if': {'column_id': 'Jugador'},
                'textAlign': 'left', 'fontWeight': '700',
                'color': '#1a1a2e', 'backgroundColor': '#f8f9fa',
                'minWidth': '140px'
            }
        ]

        for var in vars_disponibles:
            if var not in ref_stats:
                continue
            # Estilo base (celdas sin datos)
            style_conditional.append({
                'if': {'column_id': var},
                'backgroundColor': '#f0f0f0', 'color': '#cccccc',
                'textAlign': 'center'
            })
            # Reglas de color con rangos exclusivos
            for plantilla, bg, txt in reglas_color:
                conteo_vars = plantilla.count('%s')
                if conteo_vars == 1:
                    query = plantilla % var
                else:
                    query = plantilla % tuple([var] * conteo_vars)
                style_conditional.append({
                    'if': {'column_id': var, 'filter_query': query},
                    'backgroundColor': bg, 'color': txt,
                    'textAlign': 'center', 'fontWeight': '700'
                })

        info = html.Div([
            html.H6([
                f"📊 {len(datos_tabla)} jugadores vs {cat_comparar}",
                html.Span(
                    f" • {len(vars_disponibles)} variables en {mes_seleccionado}",
                    style={'fontSize': '12px', 'color': '#6c757d', 'marginLeft': '5px'}
                )
            ], style={'color': '#495057', 'marginBottom': '15px', 'fontWeight': '600'})
        ])

        logger.debug(f"OK — {len(datos_tabla)} jugadores, {len(columnas_dt)} columnas")
        return info, datos_tabla, columnas_dt, style_conditional
        
    except Exception as e:
        logger.error(f"Error en callback zscore: {e}")
        return html.P(f"Error técnico: {str(e)}", style={'color': 'red', 'textAlign': 'center', 'marginTop': '50px'}), [], [], []

@callback(
    Output('zs-radar', 'figure'),
    Input('zs-jugadores', 'value'),
    Input('zs-cat-comparar', 'value'),
    Input('zs-mes', 'value'),
    Input('zs-btn-todos', 'n_clicks'),
    State('zs-data-store', 'data'),
    State('zs-jugadores-store', 'data'),
)
def actualizar_radar(dni_list, cat_comparar, mes_seleccionado, n_clicks_todos, data_cache, jugadores_data):
    import sys
    # Inicializar variables antes de cualquier logging
    modo_individual = len(dni_list) == 1

    print(f"[ZSCORE RADAR] Iniciando callback - jugadores: {len(dni_list) if dni_list else 0}, comparar: {cat_comparar}, mes: {mes_seleccionado}", file=sys.stderr)
    logger.debug(f"RADAR - jugadores: {len(dni_list) if dni_list else 0}, comparar: {cat_comparar}, mes: {mes_seleccionado}, clicks_todos: {n_clicks_todos}")
    logger.debug(f"RADAR - data_cache: {'recibido' if data_cache else 'no recibido'}")
    logger.debug(f"RADAR - jugadores_data: {len(jugadores_data) if jugadores_data else 0}")

    # Figura vacía por defecto
    fig_vacia = go.Figure()
    fig_vacia.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,0)',
        annotations=[{
            'text': 'Seleccioná jugadores para ver el radar',
            'showarrow': False,
            'font': {'color': '#aaa', 'size': 14}
        }],
        height=650
    )

    logger.debug(f"RADAR INICIO - jugadores: {len(dni_list) if dni_list else 0}, modo_individual: {modo_individual}")
    logger.debug(f"RADAR - Variables: dni_list={bool(dni_list)}, cat_comparar={bool(cat_comparar)}, data_cache={bool(data_cache)}, mes_seleccionado={bool(mes_seleccionado)}")

    # Validaciones rápidas primero
    if not dni_list or not cat_comparar or not data_cache or not mes_seleccionado:
        print(f"[ZSCORE RADAR] Validación fallida - dni_list: {bool(dni_list)}, cat_comparar: {bool(cat_comparar)}, data_cache: {bool(data_cache)}, mes: {bool(mes_seleccionado)}", file=sys.stderr)
        logger.debug(f"RADAR - Validación fallida. dni_list: {bool(dni_list)}, cat_comparar: {bool(cat_comparar)}, data_cache: {bool(data_cache)}, mes: {bool(mes_seleccionado)}")
        return fig_vacia

    # Detectar si se presionó el botón "Todos" (SOLO cuando se presiona recientemente)
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Es modo promedio SOLO si se seleccionaron TODOS los jugadores de la categoría
    # Obtener total de jugadores en la categoría actual
    total_jugadores_categoria = len([j for j in jugadores_data if j['categoria'] == cat_comparar]) if jugadores_data else 0
    
    # Modo promedio: si se seleccionaron todos los jugadores de la categoría
    es_todos = (len(dni_list) == total_jugadores_categoria and total_jugadores_categoria > 0)
    
    # Modo individual: cuando NO se seleccionaron todos los jugadores
    modo_individual = not es_todos and dni_list and len(dni_list) > 0
    
    logger.debug(f"RADAR - n_clicks_todos: {n_clicks_todos}, es_todos: {es_todos}")
    logger.debug(f"RADAR - jugadores: {len(dni_list) if dni_list else 0}, comparar: {cat_comparar}, mes: {mes_seleccionado}")
    logger.debug(f"RADAR - data_cache: {'recibido' if data_cache else 'no recibido'}")

    try:
        base  = pd.DataFrame(data_cache['base'])
        rend  = pd.DataFrame(data_cache['rendimiento'])
        pfza  = pd.DataFrame(data_cache['pfza'])

        rend['Fecha'] = pd.to_datetime(rend['Fecha'], errors='coerce')
        pfza['Fecha'] = pd.to_datetime(pfza['Fecha'], errors='coerce')
        rend = rend[rend['Fecha'].dt.strftime('%Y-%m') == mes_seleccionado]
        pfza = pfza[pfza['Fecha'].dt.strftime('%Y-%m') == mes_seleccionado]

        vars_especificas = [
            'VO2 max', 'F0', 'Pmax', 'Vmax', 'RF', 'DRF', 'Fuerza',
            'Potencia Pico', 'Altura Salto', 'Fuerza IMTP', 'RFD Dec',
            'RFD 100', 'RFD 150', 'RFD 250'
        ]

        rend_comp = rend[rend['Categoria'] == cat_comparar]
        pfza_comp = pfza[pfza['Categoria'] == cat_comparar]

        # Estadísticas de referencia
        ref_stats = {}
        for var in vars_especificas:
            if var in rend_comp.columns:
                serie = rend_comp[var].replace(0, np.nan).dropna()
            elif var in pfza_comp.columns:
                serie = pfza_comp[var].replace(0, np.nan).dropna()
            else:
                continue
            if len(serie) > 1 and serie.std() > 0.001:
                ref_stats[var] = (serie.mean(), serie.std())

        vars_disponibles = [v for v in vars_especificas if v in ref_stats]

        if not vars_disponibles:
            return fig_vacia

        # Paleta de colores para las líneas (uno por jugador)
        paleta = [
            '#1a3a5c', '#e74c3c', '#2ecc71', '#f39c12',
            '#9b59b6', '#1abc9c', '#e67e22', '#3498db'
        ]

        # Función para convertir hex a rgba con transparencia
        def hex_to_rgba(hex_color, alpha):
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f'rgba({r}, {g}, {b}, {alpha})'

        fig = go.Figure()

        # Zonas de referencia de fondo (solo Z=0 como media del grupo)
        categorias_radar = vars_disponibles + [vars_disponibles[0]]  # cerrar el polígono

        # Zona neutra: Z = 0 (media del grupo) - línea roja destacada
        fig.add_trace(go.Scatterpolar(
            r=[0] * len(categorias_radar),
            theta=categorias_radar,
            mode='lines',
            line=dict(color='rgba(220, 53, 69, 0.9)', width=3, dash='dash'),
            name='Media (Z=0)',
            hoverinfo='skip',
            showlegend=True,
            fill=None
        ))

        # Determinar nombre para la leyenda según modo
        if es_todos:
            nombre_legend = "Promedio del Grupo"
        elif len(dni_list) == 1:
            # Si hay un solo jugador, mostrar su nombre
            nombre_row = base[base['DNI'] == dni_list[0]]['NombreCompleto'].values
            nombre_legend = nombre_row[0] if len(nombre_row) > 0 else f"DNI {dni_list[0]}"
        else:
            nombre_legend = f"{len(dni_list)} jugadores"
        
        logger.debug(f"RADAR - Modo: {'Individual' if modo_individual else 'Promedio'}, Leyenda: {nombre_legend}")
        
        # Una línea por cada jugador seleccionado (solo en modo individual)
        if modo_individual:
            for i, dni in enumerate(dni_list):
                nombre_row = base[base['DNI'] == dni]['NombreCompleto'].values
                nombre = nombre_row[0] if len(nombre_row) > 0 else f"DNI {dni}"

                rend_j = rend[rend['DNI'] == dni]
                pfza_j = pfza[pfza['DNI'] == dni]

                zscores = []
                for var in vars_disponibles:
                    media, std = ref_stats[var]
                    if var in rend_j.columns and not rend_j.empty:
                        val = rend_j[var].values[0]
                    elif var in pfza_j.columns and not pfza_j.empty:
                        val = pfza_j[var].values[0]
                    else:
                        val = np.nan

                    if pd.isna(val) or std == 0:
                        zscores.append(None)
                    else:
                        zscores.append(round((val - media) / std, 2))

                # Cerrar el polígono repitiendo el primer valor
                r_vals = zscores + [zscores[0]]
                color = paleta[i % len(paleta)]

                # Texto hover con clasificación
                def clasificar(z):
                    if z is None: return '—'
                    if z > 2.0:   return f'{z:.2f} ✦ Excelente'
                    if z > 1.0:   return f'{z:.2f} ↑ Muy Bueno'
                    if z > 0.5:   return f'{z:.2f} ↑ Bueno'
                    if z >= -0.5: return f'{z:.2f} → Promedio'
                    if z >= -1.0: return f'{z:.2f} ↓ Debajo Prom.'
                    if z >= -2.0: return f'{z:.2f} ↓ Pobre'
                    if z >= -3.0: return f'{z:.2f} ↓ Muy Pobre'
                    return f'{z:.2f} ✗ Ext. Pobre'

                hover_texts = [clasificar(z) for z in zscores] + [clasificar(zscores[0])]

                color = paleta[i % len(paleta)]
                
                # Determinar si mostrar nombre en hover (evitar duplicación con 1 jugador)
                mostrar_nombre_hover = len(dni_list) > 1
                logger.debug(f"RADAR - len(dni_list): {len(dni_list)}, mostrar_nombre_hover: {mostrar_nombre_hover}, nombre: {nombre}")
                
                fig.add_trace(go.Scatterpolar(
                    r=r_vals,
                    theta=categorias_radar,
                    fill='toself',
                    fillcolor=hex_to_rgba(color, 0.1),  # 10% transparencia
                    line=dict(color=color, width=2.5),
                    name=nombre,
                    text=hover_texts,
                    hovertemplate='<b>%{theta}</b><br>%{text}<extra>' + (nombre if mostrar_nombre_hover else '') + '</extra>',
                    marker=dict(size=6, color=color, line=dict(color='white', width=1))
                ))
        # Calcular promedio de Z-Score para cada variable (solo en modo promedio)
        promedios_z = []  # Inicializar siempre
        
        if not modo_individual:
            logger.debug(f"PROMEDIO - Calculando para {len(vars_disponibles)} variables")
            
            for var in vars_disponibles:
                media, std = ref_stats[var]
                logger.debug(f"PROMEDIO - Variable: {var}, media: {media}, std: {std}")
                
                # Obtener todos los valores de los jugadores seleccionados
                valores_z = []
                for dni in dni_list:
                    rend_j = rend[rend['DNI'] == dni]
                    pfza_j = pfza[pfza['DNI'] == dni]
                    
                    if var in rend_j.columns and not rend_j.empty:
                        val = rend_j[var].values[0]
                        logger.debug(f"PROMEDIO - DNI {dni}: {var} = {val} (rendimiento)")
                    elif var in pfza_j.columns and not pfza_j.empty:
                        val = pfza_j[var].values[0]
                        logger.debug(f"PROMEDIO - DNI {dni}: {var} = {val} (pfza)")
                    else:
                        logger.debug(f"PROMEDIO - DNI {dni}: {var} = NO ENCONTRADO")
                        continue
                    
                    if not pd.isna(val) and std != 0:
                        z = (val - media) / std
                        valores_z.append(z)
                        logger.debug(f"PROMEDIO - DNI {dni}: {var} Z = {z}")
                    else:
                        logger.debug(f"PROMEDIO - DNI {dni}: {var} = NaN o std=0")
                
                logger.debug(f"PROMEDIO - {var}: {len(valores_z)} valores Z = {valores_z}")
                
                # Calcular promedio
                if valores_z:
                    promedio_z = round(np.mean(valores_z), 2)
                    promedios_z.append(promedio_z)
                    logger.debug(f"PROMEDIO - {var}: promedio = {promedio_z}")
                else:
                    promedios_z.append(None)
                    logger.debug(f"PROMEDIO - {var}: sin datos")
            
            logger.debug(f"PROMEDIO - Resultado final: {promedios_z}")
        
        # Cerrar el polígono (mostrar solo si hay al menos algunos valores válidos)
        if promedios_z and any(z is not None for z in promedios_z):
            # Filtrar solo los valores válidos para el radar
            valores_validos = [(var, z) for var, z in zip(vars_disponibles, promedios_z) if z is not None]
            
            if valores_validos:
                vars_validas = [var for var, z in valores_validos]
                z_validos = [z for var, z in valores_validos]
                
                # Cerrar el polígono
                r_vals = z_validos + [z_validos[0]]
                theta_vals = vars_validas + [vars_validas[0]]
                
                # Texto hover para promedio
                def clasificar_promedio(z):
                    if z is None: return '—'
                    if z > 2.0:   return f'{z:.2f} ✦ Excelente'
                    if z > 1.0:   return f'{z:.2f} ↑ Muy Bueno'
                    if z > 0.5:   return f'{z:.2f} ↑ Bueno'
                    if z >= -0.5: return f'{z:.2f} → Promedio'
                    if z >= -1.0: return f'{z:.2f} ↓ Debajo Prom.'
                    if z >= -2.0: return f'{z:.2f} ↓ Pobre'
                    if z >= -3.0: return f'{z:.2f} ↓ Muy Pobre'
                    return f'{z:.2f} ✗ Ext. Pobre'
                
                hover_texts = [clasificar_promedio(z) for z in z_validos] + [clasificar_promedio(z_validos[0])]
                
                # Línea azul para el promedio
                fig.add_trace(go.Scatterpolar(
                    r=r_vals,
                    theta=theta_vals,
                    fill='toself',
                    fillcolor='rgba(26, 58, 92, 0.15)',  # Azul con transparencia
                    line=dict(color='#1a3a5c', width=3),
                    name=nombre_legend,
                    text=hover_texts,
                    hovertemplate='<b>%{theta}</b><br>%{text}<extra>' + nombre_legend + '</extra>',
                    marker=dict(size=8, color='#1a3a5c', line=dict(color='white', width=2))
                ))

        # Mostrar mensaje de debug en la interfaz para Windsurf
        mostrar_nombre_hover = len(dni_list) > 1  # Definir aquí para que esté disponible siempre
        debug_text = f"DEBUG: {len(dni_list)} jugadores - Modo: {'Individual' if modo_individual else 'Promedio'} - Hover: {'Con nombre' if mostrar_nombre_hover else 'Sin nombre'}"
        print(debug_text)
        
        fig.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(255,255,255,1)',
            polar=dict(
                bgcolor='rgba(248,250,252,0.3)',
                radialaxis=dict(
                    visible=True,
                    range=[-3, 3],
                    tickvals=[-3, -2, -1, 0, 1, 2, 3],
                    ticktext=['-3', '-2', '-1', '0', '+1', '+2', '+3'],
                    tickfont=dict(size=10, color='#6c757d', family='IBM Plex Sans'),
                    gridcolor='rgba(0,0,0,0.05)',
                    linecolor='rgba(0,0,0,0.1)',
                    showline=True,
                    linewidth=1,
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color='#1a3a5c', family='IBM Plex Sans'),
                    gridcolor='rgba(0,0,0,0.05)',
                    linecolor='rgba(0,0,0,0.1)',
                    showline=True,
                    linewidth=1,
                    direction='clockwise',
                    rotation=90,
                )
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.15,
                xanchor='center',
                x=0.5,
                font=dict(size=12, family='IBM Plex Sans', color='#495057'),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='#dee2e6',
                borderwidth=1,
                tracegroupgap=5,
                itemwidth=30,
            ),
            title=dict(
                text=f'Perfil Z-Score vs {cat_comparar}  |  {mes_seleccionado}',
                font=dict(
                    family='Rajdhani, sans-serif',
                    size=16,
                    color='#1a3a5c'
                ),
                x=0.5,
                xanchor='center',
                y=0.95,
                yanchor='top',
                pad=dict(t=10, b=10)
            ),
            margin=dict(t=100, b=120, l=100, r=100),
            height=650,
            showlegend=True,
        )

        return fig

    except Exception as e:
        import sys
        print(f"[ZSCORE RADAR ERROR] {str(e)}", file=sys.stderr)
        logger.error(f"Error en callback radar: {e}")
        # Devolver figura con mensaje de error
        fig_error = go.Figure()
        fig_error.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(255,255,255,1)',
            plot_bgcolor='rgba(255,255,255,0)',
            annotations=[{
                'text': f'Error: {str(e)}',
                'showarrow': False,
                'font': {'color': '#dc3545', 'size': 14}
            }],
            height=650
        )
        return fig_error