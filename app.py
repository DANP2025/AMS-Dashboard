import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

# Importamos las páginas al inicio para registrar sus callbacks
import pages.zscore_page as zscore_page
import pages.mbd_page as mbd_page

# ─── INICIALIZACIÓN ────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap"
    ],
    suppress_callback_exceptions=True
)
server = app.server

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
def make_sidebar():
    return html.Div([
        # Cabecera
        html.Div([
            html.Div("⚽", style={'fontSize': '2rem'}),
            html.H4("AMS", style={
                'margin': '4px 0 0 0',
                'fontFamily': 'Rajdhani, sans-serif',
                'fontWeight': '700',
                'letterSpacing': '3px',
                'color': '#e0e0e0'
            }),
            html.P("Athlete Management", style={
                'fontSize': '10px',
                'color': '#666',
                'margin': '0',
                'letterSpacing': '1px',
                'textTransform': 'uppercase'
            }),
        ], style={
            'textAlign': 'center',
            'padding': '24px 12px 16px',
            'borderBottom': '1px solid #2a2a3e'
        }),

        # Navegación
        html.Div([
            html.P("📊 RENDIMIENTO", style={
                'color': '#555',
                'fontSize': '10px',
                'fontWeight': '700',
                'letterSpacing': '2px',
                'margin': '20px 12px 6px',
                'textTransform': 'uppercase'
            }),
            dbc.Nav([
                dbc.NavLink(
                    html.Span(["🔬 ", html.Span("Z-Score / Extrapolar")]),
                    href="/zscore",
                    id="nav-zscore",
                    style={'fontSize': '13px', 'padding': '8px 14px', 'borderRadius': '6px', 'marginBottom': '4px'}
                ),
                dbc.NavLink(
                    html.Span(["📈 ", html.Span("MBD Hopkins")]),
                    href="/mbd",
                    id="nav-mbd",
                    style={'fontSize': '13px', 'padding': '8px 14px', 'borderRadius': '6px', 'marginBottom': '4px'}
                ),
            ], vertical=True, pills=True),
        ], style={'padding': '0 8px'}),

        # Pie del sidebar
        html.Div([
            html.P("AMS v1.0", style={'color': '#333', 'fontSize': '10px', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'position': 'absolute', 'bottom': '12px', 'width': '100%'
        })

    ], style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '200px',
        'backgroundColor': '#0d0d1a',
        'borderRight': '1px solid #1a1a2e',
        'overflowY': 'auto',
        'zIndex': 1000
    })


# ─── LAYOUT PRINCIPAL ──────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Intervalo de auto-recarga: revisa el Excel cada 30 segundos
    dcc.Interval(id='auto-reload', interval=30_000, n_intervals=0),

    make_sidebar(),

    # Contenido de la página activa
    html.Div(
        id='page-content',
        style={
            'marginLeft': '200px',
            'padding': '24px',
            'minHeight': '100vh',
            'backgroundColor': '#0f0f1a'
        }
    )
], style={'fontFamily': 'IBM Plex Sans, sans-serif'})


# ─── ROUTING ───────────────────────────────────────────────────────────────────
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page(pathname):
    if pathname == '/mbd':
        return mbd_page.layout()
    return zscore_page.layout()


# ─── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("🚀 AMS Dashboard iniciando en http://localhost:8050")
    app.run(debug=True, host='127.0.0.1', port=8050)
