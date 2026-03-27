import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data_loader import (
    load_data, get_categorias, get_jugadores_por_categoria,
    get_vars_rendimiento, get_vars_pfza, get_available_months,
    filter_by_month
)
from calculations import calc_mbd, get_etiqueta_inferencia, get_color_etiqueta


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
                'color': '#e8e8f0',
                'marginBottom': '4px',
                'letterSpacing': '1px'
            }),
            html.P(
                "Metodología Will Hopkins | SWC = 0.2 × SD baseline | TE estimado por ICC (0.90)",
                style={'color': '#666', 'fontSize': '12px', 'marginBottom': '20px'}
            ),
        ]),

        # ── Filtros ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Meses (seleccioná exactamente 2)", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dcc.Dropdown(
                    id='mbd-meses',
                    options=month_options,
                    value=default_meses,
                    multi=True,
                    placeholder="Seleccioná 2 meses...",
                )
            ], width=4),

            dbc.Col([
                html.Label("Categoría", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dcc.Dropdown(
                    id='mbd-categoria',
                    options=cat_options,
                    value=primera_cat,
                    clearable=False,
                )
            ], width=3),

            dbc.Col([
                html.Label("Jugador(es)", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dbc.Row([
                    dbc.Col(dcc.Dropdown(
                        id='mbd-jugadores',
                        options=[],
                        value=[],
                        multi=True,
                        placeholder="Todos o seleccioná...",
                    ), width=9),
                    dbc.Col(dbc.Button(
                        "Todos", id='mbd-btn-todos',
                        color="outline-secondary", size="sm",
                        style={'width': '100%', 'fontSize': '12px'}
                    ), width=3),
                ], className="g-1"),
            ], width=5),
        ], className="mb-3"),

        # Alertas de selección
        html.Div(id='mbd-alerta', className="mb-3"),

        # ── Tabla MBD ─────────────────────────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                html.H6("Tabla de Inferencias por Variable y Jugador",
                        style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px', 'marginBottom': '12px'}),
                html.Div(id='mbd-tabla', style={'overflowX': 'auto'}),
            ])
        ], style={'backgroundColor': '#13131f', 'border': '1px solid #2a2a3e', 'marginBottom': '16px'}),

        # ── Selector de jugador para el gráfico ───────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Jugador para el Forest Plot", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                dcc.Dropdown(
                    id='mbd-jugador-grafico',
                    options=[],
                    value=None,
                    clearable=False,
                    placeholder="Seleccioná un jugador..."
                )
            ], width=4),
        ], className="mb-2"),

        # ── Forest Plot ───────────────────────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='mbd-forest', config={'displayModeBar': False})
            ])
        ], style={'backgroundColor': '#13131f', 'border': '1px solid #2a2a3e'}),

    ])


# ─── CALLBACKS ────────────────────────────────────────────────────────────────

@callback(
    Output('mbd-jugadores', 'options'),
    Output('mbd-jugadores', 'value'),
    Input('mbd-categoria', 'value'),
    Input('mbd-btn-todos', 'n_clicks'),
)
def actualizar_jugadores_mbd(categoria, n_clicks):
    data = load_data()
    if data is None or not categoria:
        return [], []
    jugadores = get_jugadores_por_categoria(data, categoria)
    options = [{'label': j['NombreCompleto'], 'value': j['DNI']} for j in jugadores]
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else ''
    values = [j['DNI'] for j in jugadores] if 'mbd-btn-todos' in triggered else []
    return options, values


@callback(
    Output('mbd-alerta', 'children'),
    Output('mbd-tabla', 'children'),
    Output('mbd-jugador-grafico', 'options'),
    Output('mbd-jugador-grafico', 'value'),
    Input('mbd-meses', 'value'),
    Input('mbd-categoria', 'value'),
    Input('mbd-jugadores', 'value'),
    Input('auto-reload', 'n_intervals'),
)
def actualizar_tabla_mbd(meses, categoria, dni_list, n_intervals):
    sin_datos = html.P("Sin datos para mostrar.", style={'color': '#555'})

    if not meses or len(meses) != 2:
        alerta = dbc.Alert("⚠️ Seleccioná exactamente 2 meses para definir Pre-test y Post-test.", color="warning", className="py-1")
        return alerta, sin_datos, [], None

    if not dni_list:
        alerta = dbc.Alert("ℹ️ Seleccioná al menos un jugador.", color="info", className="py-1")
        return alerta, sin_datos, [], None

    data = load_data()
    if data is None:
        return dbc.Alert("❌ Error al cargar datos.", color="danger"), sin_datos, [], None

    meses_sorted = sorted(meses)
    mes_pre, mes_post = meses_sorted[0], meses_sorted[1]
    alerta = dbc.Alert([
        html.Strong("Pre-test: "), html.Span(mes_pre, style={'color': '#4da6ff'}),
        html.Span("  →  ", style={'color': '#666'}),
        html.Strong("Post-test: "), html.Span(mes_post, style={'color': '#5cb85c'}),
        html.Span(f"  |  SWC = 0.2 × SD baseline", style={'color': '#888', 'fontSize': '11px', 'marginLeft': '8px'})
    ], color="dark", className="py-1 px-3",
       style={'backgroundColor': '#1a1a2e', 'border': '1px solid #2a2a3e'})

    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    todas_vars = vars_rend + vars_pfza

    # SD del grupo en pre-test (toda la categoría seleccionada)
    rend_cat_pre = filter_by_month(data['rendimiento'][data['rendimiento']['Categoria'] == categoria], mes_pre)
    pfza_cat_pre = filter_by_month(data['pfza'][data['pfza']['Categoria'] == categoria], mes_pre)

    # Calcular MBD por jugador
    datos_tabla = []
    nombres_map = {}

    for dni in dni_list:
        nombre_row = data['base'][data['base']['DNI'] == dni]['NombreCompleto'].values
        nombre = nombre_row[0] if len(nombre_row) > 0 else f"DNI {dni}"
        nombres_map[dni] = nombre
        row = {'Jugador': nombre, 'DNI': dni}

        # Rendimiento
        rend_pre = filter_by_month(data['rendimiento'][data['rendimiento']['DNI'] == dni], mes_pre)
        rend_post = filter_by_month(data['rendimiento'][data['rendimiento']['DNI'] == dni], mes_post)
        for var in vars_rend:
            pre_v = rend_pre[var].values[0] if (not rend_pre.empty and var in rend_pre.columns and len(rend_pre) > 0) else np.nan
            post_v = rend_post[var].values[0] if (not rend_post.empty and var in rend_post.columns and len(rend_post) > 0) else np.nan
            sd_grp = rend_cat_pre[var] if var in rend_cat_pre.columns else pd.Series(dtype=float)
            row[var] = calc_mbd(pre_v, post_v, sd_grp)

        # Plat de fuerza
        pfza_pre = filter_by_month(data['pfza'][data['pfza']['DNI'] == dni], mes_pre)
        pfza_post = filter_by_month(data['pfza'][data['pfza']['DNI'] == dni], mes_post)
        for var in vars_pfza:
            pre_v = pfza_pre[var].values[0] if (not pfza_pre.empty and var in pfza_pre.columns and len(pfza_pre) > 0) else np.nan
            post_v = pfza_post[var].values[0] if (not pfza_post.empty and var in pfza_post.columns and len(pfza_post) > 0) else np.nan
            sd_grp = pfza_cat_pre[var] if var in pfza_cat_pre.columns else pd.Series(dtype=float)
            row[var] = calc_mbd(pre_v, post_v, sd_grp)

        datos_tabla.append(row)

    # Variables con al menos un dato disponible
    vars_disp = [v for v in todas_vars if any(r.get(v) is not None for r in datos_tabla)]

    # ── CONSTRUCCIÓN DE LA TABLA ─────────────────────────────────────────────
    encabezado = html.Thead(html.Tr([
        html.Th("Jugador", style={'color': '#4da6ff', 'fontSize': '11px', 'position': 'sticky', 'left': 0, 'backgroundColor': '#0d0d1a', 'minWidth': '130px'}),
        *[html.Th(v, style={'color': '#4da6ff', 'fontSize': '10px', 'textAlign': 'center', 'minWidth': '100px'})
          for v in vars_disp]
    ]))

    filas = []
    for row in datos_tabla:
        celdas = [html.Td(row['Jugador'], style={
            'fontWeight': '600', 'fontSize': '12px', 'color': '#ddd',
            'position': 'sticky', 'left': 0, 'backgroundColor': '#13131f'
        })]
        for var in vars_disp:
            mbd_res = row.get(var)
            if mbd_res is None:
                celdas.append(html.Td("—", style={'textAlign': 'center', 'color': '#333'}))
            else:
                etiqueta = get_etiqueta_inferencia(mbd_res['prob_ben'], mbd_res['prob_per'])
                color_bg = get_color_etiqueta(etiqueta)
                cambio_txt = f"{mbd_res['cambio']:+.2f}"
                celdas.append(html.Td([
                    html.Div(cambio_txt, style={'fontSize': '11px', 'fontWeight': '700', 'color': 'white'}),
                    html.Div(etiqueta, style={'fontSize': '9px', 'color': 'rgba(255,255,255,0.85)', 'lineHeight': '1.2'})
                ], style={
                    'backgroundColor': color_bg,
                    'textAlign': 'center',
                    'padding': '5px 4px',
                    'borderRadius': '4px',
                    'margin': '1px'
                }))
        filas.append(html.Tr(celdas))

    tabla = dbc.Table(
        [encabezado, html.Tbody(filas)],
        bordered=False, dark=True, hover=True, responsive=True, size="sm"
    )

    # Opciones para el selector de jugador del gráfico
    opciones_graf = [{'label': nombres_map[d], 'value': d} for d in dni_list]
    valor_graf = dni_list[0] if dni_list else None

    return alerta, tabla, opciones_graf, valor_graf


@callback(
    Output('mbd-forest', 'figure'),
    Input('mbd-jugador-grafico', 'value'),
    Input('mbd-meses', 'value'),
    Input('mbd-categoria', 'value'),
    Input('auto-reload', 'n_intervals'),
)
def actualizar_forest_plot(dni_sel, meses, categoria, n_intervals):
    fig_vacia = go.Figure()
    fig_vacia.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(13,13,26,1)',
        plot_bgcolor='rgba(13,13,26,0)',
        height=200,
        annotations=[{'text': 'Seleccioná un jugador para ver el Forest Plot',
                      'showarrow': False, 'font': {'color': '#444', 'size': 13}}]
    )

    if not dni_sel or not meses or len(meses) != 2:
        return fig_vacia

    data = load_data()
    if data is None:
        return fig_vacia

    meses_sorted = sorted(meses)
    mes_pre, mes_post = meses_sorted[0], meses_sorted[1]

    vars_rend = get_vars_rendimiento(data)
    vars_pfza = get_vars_pfza(data)
    todas_vars = vars_rend + vars_pfza

    rend_cat_pre = filter_by_month(data['rendimiento'][data['rendimiento']['Categoria'] == categoria], mes_pre)
    pfza_cat_pre = filter_by_month(data['pfza'][data['pfza']['Categoria'] == categoria], mes_pre)

    # Obtener nombre del jugador
    nombre_row = data['base'][data['base']['DNI'] == dni_sel]['NombreCompleto'].values
    nombre = nombre_row[0] if len(nombre_row) > 0 else f"DNI {dni_sel}"

    # Calcular MBD para el jugador seleccionado
    vars_plot = []
    effects = []
    incerts = []
    colores_pt = []

    def get_mbd_var(var, sheet='rendimiento'):
        if sheet == 'rendimiento':
            pre_df = filter_by_month(data['rendimiento'][data['rendimiento']['DNI'] == dni_sel], mes_pre)
            post_df = filter_by_month(data['rendimiento'][data['rendimiento']['DNI'] == dni_sel], mes_post)
            sd_df = rend_cat_pre
        else:
            pre_df = filter_by_month(data['pfza'][data['pfza']['DNI'] == dni_sel], mes_pre)
            post_df = filter_by_month(data['pfza'][data['pfza']['DNI'] == dni_sel], mes_post)
            sd_df = pfza_cat_pre

        pre_v = pre_df[var].values[0] if (not pre_df.empty and var in pre_df.columns and len(pre_df) > 0) else np.nan
        post_v = post_df[var].values[0] if (not post_df.empty and var in post_df.columns and len(post_df) > 0) else np.nan
        sd_s = sd_df[var] if var in sd_df.columns else pd.Series(dtype=float)
        return calc_mbd(pre_v, post_v, sd_s)

    for var in vars_rend:
        mbd_res = get_mbd_var(var, 'rendimiento')
        if mbd_res is not None:
            etq = get_etiqueta_inferencia(mbd_res['prob_ben'], mbd_res['prob_per'])
            vars_plot.append(var)
            effects.append(mbd_res['effect_size'])
            incerts.append(mbd_res['incertidumbre'] / mbd_res['sd_pre'] if mbd_res['sd_pre'] != 0 else 0)
            colores_pt.append(get_color_etiqueta(etq))

    for var in vars_pfza:
        mbd_res = get_mbd_var(var, 'pfza')
        if mbd_res is not None:
            etq = get_etiqueta_inferencia(mbd_res['prob_ben'], mbd_res['prob_per'])
            vars_plot.append(var)
            effects.append(mbd_res['effect_size'])
            incerts.append(mbd_res['incertidumbre'] / mbd_res['sd_pre'] if mbd_res['sd_pre'] != 0 else 0)
            colores_pt.append(get_color_etiqueta(etq))

    if not vars_plot:
        return fig_vacia

    # ── FOREST PLOT ────────────────────────────────────────────────────────────
    SWC = 0.2  # En unidades estandarizadas, SWC siempre = 0.2
    max_range = max(2.5, max(abs(e) + u + 0.3 for e, u in zip(effects, incerts)))

    fig = go.Figure()

    # Zonas de color de fondo
    n_vars = len(vars_plot)
    fig.add_shape(type="rect",
                  x0=-max_range, x1=-SWC, y0=-0.5, y1=n_vars - 0.5,
                  fillcolor="rgba(180,30,30,0.12)", line_width=0, layer='below')
    fig.add_shape(type="rect",
                  x0=-SWC, x1=SWC, y0=-0.5, y1=n_vars - 0.5,
                  fillcolor="rgba(100,100,100,0.10)", line_width=0, layer='below')
    fig.add_shape(type="rect",
                  x0=SWC, x1=max_range, y0=-0.5, y1=n_vars - 0.5,
                  fillcolor="rgba(30,180,60,0.12)", line_width=0, layer='below')

    # Líneas de referencia
    fig.add_vline(x=0, line_color='rgba(255,255,255,0.2)', line_width=1)
    fig.add_vline(x=-SWC, line_dash='dash', line_color='rgba(220,53,69,0.7)', line_width=1.5,
                  annotation_text='-SWC', annotation_font_color='#dc3545',
                  annotation_position='top left', annotation_font_size=10)
    fig.add_vline(x=SWC, line_dash='dash', line_color='rgba(40,167,69,0.7)', line_width=1.5,
                  annotation_text='+SWC', annotation_font_color='#28a745',
                  annotation_position='top right', annotation_font_size=10)

    # Barras de error + puntos
    fig.add_trace(go.Scatter(
        x=effects,
        y=vars_plot,
        mode='markers',
        marker=dict(
            size=11,
            color=colores_pt,
            line=dict(color='white', width=1.5),
            symbol='circle'
        ),
        error_x=dict(
            type='data',
            array=incerts,
            visible=True,
            color='rgba(200,200,200,0.5)',
            thickness=2,
            width=6
        ),
        name=nombre,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Effect Size: %{x:.2f} SD<br>"
            "<extra></extra>"
        )
    ))

    # Etiquetas de zona
    fig.add_annotation(x=-max_range * 0.65, y=n_vars - 0.2,
                       text="🔴 Perjudicial", font=dict(color='#e74c3c', size=10), showarrow=False)
    fig.add_annotation(x=0, y=n_vars - 0.2,
                       text="⬜ Trivial", font=dict(color='#888', size=10), showarrow=False)
    fig.add_annotation(x=max_range * 0.65, y=n_vars - 0.2,
                       text="🟢 Beneficioso", font=dict(color='#28a745', size=10), showarrow=False)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(13,13,26,1)',
        plot_bgcolor='rgba(13,13,26,0)',
        title=dict(
            text=f"Forest Plot MBD — {nombre}  |  {mes_pre} → {mes_post}",
            font=dict(family='Rajdhani, sans-serif', size=15, color='#e0e0e0')
        ),
        xaxis=dict(
            title="Effect Size (unidades SD)  |  SWC = ±0.2",
            range=[-max_range, max_range],
            zeroline=False,
            gridcolor='rgba(255,255,255,0.04)',
            titlefont=dict(size=11, color='#888')
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.04)',
            tickfont=dict(size=11)
        ),
        height=max(280, n_vars * 38 + 120),
        showlegend=False,
        margin=dict(l=130, r=40, t=60, b=50),
    )

    return fig
