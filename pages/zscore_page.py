import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data_loader import (
    load_data, get_categorias, get_jugadores_por_categoria,
    get_vars_rendimiento, get_vars_pfza, latest_per_player
)
from calculations import calc_zscore


# ─── LAYOUT ───────────────────────────────────────────────────────────────────

def layout():
    data = load_data()
    if data is None:
        return dbc.Alert("❌ No se pudo cargar AMS.xlsx. Verificá la ruta del archivo.", color="danger")

    categorias = get_categorias(data)
    cat_options = [{'label': c, 'value': c} for c in categorias]
    primera_cat = categorias[0] if categorias else None

    return html.Div([
        # Título
        html.Div([
            html.H3("🔬 Z-Score — Extrapolar Datos", style={
                'fontFamily': 'Rajdhani, sans-serif',
                'fontWeight': '700',
                'color': '#e8e8f0',
                'marginBottom': '4px',
                'letterSpacing': '1px'
            }),
            html.P(
                "Compará el perfil de un jugador contra cualquier categoría como referencia.",
                style={'color': '#666', 'fontSize': '13px', 'marginBottom': '20px'}
            ),
        ]),

        # ── Filtros ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Categoría del jugador", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dcc.Dropdown(
                    id='zs-cat-jugador',
                    options=cat_options,
                    value=primera_cat,
                    clearable=False,
                    style={'backgroundColor': '#1a1a2e', 'color': 'white'}
                )
            ], width=3),

            dbc.Col([
                html.Label("Jugador(es)", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dbc.Row([
                    dbc.Col(dcc.Dropdown(
                        id='zs-jugadores',
                        options=[],
                        value=[],
                        multi=True,
                        placeholder="Seleccioná jugadores...",
                    ), width=9),
                    dbc.Col(dbc.Button(
                        "Todos", id='zs-btn-todos',
                        color="outline-secondary", size="sm",
                        style={'width': '100%', 'fontSize': '12px'}
                    ), width=3),
                ], className="g-1"),
            ], width=5),

            dbc.Col([
                html.Label("Categoría a comparar", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dcc.Dropdown(
                    id='zs-cat-comparar',
                    options=cat_options,
                    value=primera_cat,
                    clearable=False,
                    style={'backgroundColor': '#1a1a2e', 'color': 'white'}
                )
            ], width=4),
        ], className="mb-4"),

        # ── Indicador de comparación ──────────────────────────────────────────
        html.Div(id='zs-info-comparacion', className="mb-3"),

        # ── Gráfico de barras ─────────────────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='zs-grafico', config={'displayModeBar': False}, style={'height': '420px'})
            ])
        ], style={'backgroundColor': '#13131f', 'border': '1px solid #2a2a3e', 'marginBottom': '16px'}),

        # ── Tabla de Z-scores ─────────────────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                html.H6("Tabla de Z-Scores", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px', 'marginBottom': '12px'}),
                html.Div(id='zs-tabla', style={'overflowX': 'auto'})
            ])
        ], style={'backgroundColor': '#13131f', 'border': '1px solid #2a2a3e'}),

    ])


# ─── CALLBACKS ────────────────────────────────────────────────────────────────

@callback(
    Output('zs-jugadores', 'options'),
    Output('zs-jugadores', 'value'),
    Input('zs-cat-jugador', 'value'),
    Input('zs-btn-todos', 'n_clicks'),
    prevent_initial_call=False
)
def actualizar_jugadores(categoria, n_clicks):
    data = load_data()
    if data is None or not categoria:
        return [], []

    jugadores = get_jugadores_por_categoria(data, categoria)
    options = [{'label': j['NombreCompleto'], 'value': j['DNI']} for j in jugadores]

    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else ''
    if 'zs-btn-todos' in triggered:
        values = [j['DNI'] for j in jugadores]
    else:
        values = []

    return options, values


@callback(
    Output('zs-info-comparacion', 'children'),
    Output('zs-grafico', 'figure'),
    Output('zs-tabla', 'children'),
    Input('zs-jugadores', 'value'),
    Input('zs-cat-comparar', 'value'),
    Input('zs-cat-jugador', 'value'),
    Input('auto-reload', 'n_intervals'),
)
def actualizar_zscore(dni_list, cat_comparar, cat_jugador, n_intervals):

    # Figura vacía por defecto
    fig_vacia = go.Figure()
    fig_vacia.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(13,13,26,1)',
        plot_bgcolor='rgba(13,13,26,0)',
        annotations=[{
            'text': 'Seleccioná jugadores y categoría a comparar',
            'showarrow': False,
            'font': {'color': '#444', 'size': 14}
        }]
    )

    if not dni_list or not cat_comparar:
        return None, fig_vacia, html.P("Sin datos para mostrar.", style={'color': '#555'})

    data = load_data()
    if data is None:
        return None, fig_vacia, html.P("Error al cargar datos.", style={'color': 'red'})

    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    todas_vars = vars_rend + vars_pfza

    # Grupo de comparación: última medición de cada jugador de la categoría seleccionada
    comp_rend = latest_per_player(
        data['rendimiento'][data['rendimiento']['Categoria'] == cat_comparar]
    )
    comp_pfza = latest_per_player(
        data['pfza'][data['pfza']['Categoria'] == cat_comparar]
    )

    n_comp_rend = len(comp_rend)
    n_comp_pfza = len(comp_pfza)

    # Info de comparación
    info = dbc.Alert([
        html.Span(f"📌 Comparando contra ", style={'color': '#aaa'}),
        html.Strong(cat_comparar, style={'color': '#4da6ff'}),
        html.Span(f" — {n_comp_rend} jugadores (Rendimiento) | {n_comp_pfza} jugadores (Fuerza)", style={'color': '#aaa', 'fontSize': '12px'})
    ], color="dark", className="py-1 px-3", style={'backgroundColor': '#1a1a2e', 'border': '1px solid #2a2a3e'})

    # Calcular Z-scores para cada jugador seleccionado
    resultados = []

    for dni in dni_list:
        nombre_row = data['base'][data['base']['DNI'] == dni]['NombreCompleto'].values
        nombre = nombre_row[0] if len(nombre_row) > 0 else f"DNI {dni}"
        row = {'Jugador': nombre}

        # Variables de Rendimiento
        player_rend = data['rendimiento'][data['rendimiento']['DNI'] == dni]
        if not player_rend.empty:
            ultima_rend = player_rend.sort_values('Fecha').iloc[-1]
            for var in vars_rend:
                if var in comp_rend.columns and not comp_rend.empty:
                    row[var] = round(calc_zscore(ultima_rend.get(var, np.nan), comp_rend[var]), 2)
                else:
                    row[var] = np.nan

        # Variables de Plat de fuerza
        player_pfza = data['pfza'][data['pfza']['DNI'] == dni]
        if not player_pfza.empty:
            ultima_pfza = player_pfza.sort_values('Fecha').iloc[-1]
            for var in vars_pfza:
                if var in comp_pfza.columns and not comp_pfza.empty:
                    row[var] = round(calc_zscore(ultima_pfza.get(var, np.nan), comp_pfza[var]), 2)
                else:
                    row[var] = np.nan

        resultados.append(row)

    if not resultados:
        return info, fig_vacia, html.P("Sin datos para mostrar.", style={'color': '#555'})

    df_res = pd.DataFrame(resultados)
    vars_disponibles = [v for v in todas_vars if v in df_res.columns]

    # ── GRÁFICO ──────────────────────────────────────────────────────────────
    def color_barra(z):
        if z is None or (isinstance(z, float) and np.isnan(z)):
            return 'rgba(100,100,100,0.4)'
        if z >= 1.5:   return '#0d6e33'
        if z >= 0.5:   return '#28a745'
        if z >= 0:     return '#5cb85c'
        if z >= -0.5:  return '#e67e22'
        if z >= -1.5:  return '#e74c3c'
        return '#7b241c'

    fig = go.Figure()
    for _, fila in df_res.iterrows():
        z_vals = [fila.get(v, None) for v in vars_disponibles]
        colores = [color_barra(z) for z in z_vals]
        z_vals_clean = [v if (v is not None and not (isinstance(v, float) and np.isnan(v))) else None for v in z_vals]

        fig.add_trace(go.Bar(
            name=fila['Jugador'],
            x=vars_disponibles,
            y=z_vals_clean,
            marker_color=colores,
            text=[f"{v:.2f}" if v is not None else "—" for v in z_vals_clean],
            textposition='outside',
            textfont=dict(size=10, color='#aaa'),
        ))

    fig.add_hline(y=0, line_color='rgba(255,255,255,0.3)', line_width=1)
    fig.add_hline(y=1, line_dash='dot', line_color='rgba(40,167,69,0.4)', line_width=1,
                  annotation_text='Z=1', annotation_font_color='#28a745', annotation_position='right')
    fig.add_hline(y=-1, line_dash='dot', line_color='rgba(231,76,60,0.4)', line_width=1,
                  annotation_text='Z=-1', annotation_font_color='#e74c3c', annotation_position='right')

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(13,13,26,1)',
        plot_bgcolor='rgba(13,13,26,0)',
        title=dict(
            text=f"Z-Score vs {cat_comparar}",
            font=dict(family='Rajdhani, sans-serif', size=16, color='#e0e0e0')
        ),
        barmode='group',
        yaxis_title="Z-Score",
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        xaxis=dict(tickfont=dict(size=11), gridcolor='rgba(255,255,255,0.03)'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        margin=dict(t=60, b=20, l=40, r=60),
    )

    # ── TABLA ────────────────────────────────────────────────────────────────
    encabezado = html.Thead(html.Tr([
        html.Th("Jugador", style={'color': '#4da6ff', 'fontSize': '11px', 'minWidth': '130px'}),
        *[html.Th(v, style={'color': '#4da6ff', 'fontSize': '10px', 'minWidth': '80px', 'textAlign': 'center'})
          for v in vars_disponibles]
    ]))

    filas = []
    for _, fila in df_res.iterrows():
        celdas = [html.Td(fila['Jugador'], style={'fontWeight': '600', 'fontSize': '12px', 'color': '#ddd'})]
        for v in vars_disponibles:
            val = fila.get(v)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                celdas.append(html.Td("—", style={'textAlign': 'center', 'color': '#444'}))
            else:
                col = color_barra(val)
                celdas.append(html.Td(
                    f"{val:.2f}",
                    style={
                        'textAlign': 'center',
                        'fontWeight': '700',
                        'fontSize': '12px',
                        'color': col,
                    }
                ))
        filas.append(html.Tr(celdas))

    tabla = dbc.Table(
        [encabezado, html.Tbody(filas)],
        bordered=False, dark=True, hover=True, responsive=True, size="sm"
    )

    return info, fig, tabla
