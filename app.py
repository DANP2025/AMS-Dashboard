import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

import pages.zscore_page as zscore_page
import pages.mbd_page as mbd_page
import pages.swc_page as swc_page

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap"
    ],
    suppress_callback_exceptions=True
)
server = app.server

def make_sidebar():
    return html.Div([
        html.Div([
            html.Div("⚽", style={'fontSize': '2rem'}),
            html.H4("AMS", style={
                'margin': '4px 0 0',
                'fontFamily': 'Rajdhani, sans-serif',
                'fontWeight': '700',
                'letterSpacing': '3px',
                'color': '#ffffff'
            }),
            html.P("Athlete Management", style={
                'fontSize': '10px',
                'color': 'rgba(255,255,255,0.45)',
                'margin': '0',
                'letterSpacing': '1px',
                'textTransform': 'uppercase'
            }),
        ], style={
            'textAlign': 'center',
            'padding': '24px 12px 16px',
            'borderBottom': '1px solid rgba(255,255,255,0.1)'
        }),

        html.Div([
            html.P("📊 RENDIMIENTO", style={
                'color': 'rgba(255,255,255,0.3)',
                'fontSize': '10px',
                'fontWeight': '700',
                'letterSpacing': '2px',
                'margin': '20px 12px 6px',
                'textTransform': 'uppercase'
            }),
            dbc.Nav([
                dbc.NavLink(
                    html.Span(["", html.Span("Z-Score / Extrapolar")]),
                    href="/zscore",
                    id="nav-zscore",
                    style={'fontSize': '13px', 'padding': '8px 14px', 'borderRadius': '6px', 'marginBottom': '4px', 'color': 'rgba(255,255,255,0.75)'}
                ),
                dbc.NavLink(
                    html.Span(["", html.Span("MBD Hopkins")]),
                    href="/mbd",
                    id="nav-mbd",
                    style={'fontSize': '13px', 'padding': '8px 14px', 'borderRadius': '6px', 'marginBottom': '4px', 'color': 'rgba(255,255,255,0.75)'}
                ),
                dbc.NavLink(
                    html.Span(["", html.Span("SWC")]),
                    href="/swc",
                    id="nav-swc",
                    style={'fontSize': '13px', 'padding': '8px 14px', 'borderRadius': '6px', 'marginBottom': '4px', 'color': 'rgba(255,255,255,0.75)'}
                ),
            ], vertical=True, pills=True),
        ], style={'padding': '0 8px'}),

        html.Div([
            html.P("AMS v1.0", style={'color': 'rgba(255,255,255,0.2)', 'fontSize': '10px', 'textAlign': 'center', 'margin': '0'})
        ], style={'position': 'absolute', 'bottom': '12px', 'width': '100%'})

    ], style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '200px',
        'backgroundColor': '#1a3a5c',
        'borderRight': '1px solid #163252',
        'overflowY': 'auto',
        'zIndex': 1000
    })


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='auto-reload', interval=30_000, n_intervals=0),
    make_sidebar(),
    html.Div(
        id='page-content',
        style={
            'marginLeft': '200px',
            'padding': '28px',
            'minHeight': '100vh',
            'backgroundColor': '#ffffff'
        }
    )
], style={'fontFamily': 'IBM Plex Sans, sans-serif', 'backgroundColor': '#ffffff'})


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page(pathname):
    if pathname == '/' or pathname is None:
        # Página de inicio - redirigir a SWC
        return swc_page.layout()
    elif pathname == '/mbd':
        return mbd_page.layout()
    elif pathname == '/swc':
        return swc_page.layout()
    elif pathname == '/zscore':
        return zscore_page.layout()
    else:
        return html.Div([
            html.H1("Página no encontrada", style={'textAlign': 'center', 'marginTop': '50px'}),
            html.P(f"La página '{pathname}' no existe.", style={'textAlign': 'center'}),
            html.P("Páginas disponibles: /swc, /mbd, /zscore", style={'textAlign': 'center', 'marginTop': '20px'})
        ], style={'padding': '50px'})



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    print(f"AMS Dashboard iniciando en http://0.0.0.0:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
