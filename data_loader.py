import os
import pandas as pd
import numpy as np

_cache = {'data': None, 'mtime': 0.0}
# Ruta del archivo Excel: usar variable de entorno o ruta relativa al script
XLSX_PATH = os.environ.get('AMS_XLSX_PATH', os.path.join(os.path.dirname(__file__), '..', 'AMS.xlsx'))

VARS_RENDIMIENTO = ['VO2 max', 'F0', 'V0', 'Pmax', 'Vmax', 'RF', 'DRF']
VARS_PFZA = [
    'Fuerza', 'Potencia Pico', 'Altura Salto',
    'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250'
]


def _normalizar_categoria(cat):
    """Normaliza categoría: elimina espacios múltiples, Title Case."""
    if cat is None or (isinstance(cat, float) and pd.isna(cat)):
        return ''
    return ' '.join(str(cat).strip().split()).title()


def load_data():
    global _cache
    try:
        mtime = os.path.getmtime(XLSX_PATH)
        if _cache['data'] is not None and mtime == _cache['mtime']:
            return _cache['data']

        xl = pd.ExcelFile(XLSX_PATH)
        base = xl.parse('Base de datos')
        rend = xl.parse('Rendimiento')
        pfza_raw = xl.parse('Plat de fuerza')

        # ── Crear NombreCompleto en base ──────────────────────────────────
        base['NombreCompleto'] = (
            base.get('Nombre', pd.Series([''] * len(base)))
            .fillna('').astype(str).str.strip()
            + ' '
            + base.get('Apellido', pd.Series([''] * len(base)))
            .fillna('').astype(str).str.strip()
        ).str.strip()

        # ── Normalizar DNI ────────────────────────────────────────────────
        for df in [base, rend, pfza_raw]:
            if 'DNI' in df.columns:
                df['DNI'] = pd.to_numeric(df['DNI'], errors='coerce')

        # ── Normalizar categorías ─────────────────────────────────────────
        for df in [base, rend, pfza_raw]:
            if 'Categoria' in df.columns:
                df['Categoria'] = df['Categoria'].apply(_normalizar_categoria)

        # ── Limpiar filas sin DNI ─────────────────────────────────────────
        rend = rend[rend['DNI'].notna()].copy()
        pfza_raw = pfza_raw[pfza_raw['DNI'].notna()].copy()

        # ── AGREGAR pfza: 1 fila por (DNI, Fecha, Categoria) ─────────────
        # La hoja tiene miles de filas por repetición/test.
        # Necesitamos la MEDIA por jugador+fecha para el SWC correcto (Hopkins).
        vars_a_agregar = [v for v in VARS_PFZA if v in pfza_raw.columns]

        if vars_a_agregar and 'Fecha' in pfza_raw.columns:
            group_cols = ['DNI', 'Fecha', 'Categoria']
            # También preservar Apellido si existe
            if 'Apellido' in pfza_raw.columns:
                group_cols_ext = ['DNI', 'Fecha', 'Categoria', 'Apellido']
                # Tomar primer Apellido por grupo
                apellidos = (pfza_raw.groupby(['DNI', 'Fecha', 'Categoria'])['Apellido']
                             .first().reset_index())
                pfza_agg = (pfza_raw.groupby(group_cols)[vars_a_agregar]
                            .mean()
                            .reset_index())
                pfza = pfza_agg.merge(apellidos, on=['DNI', 'Fecha', 'Categoria'], how='left')
            else:
                pfza = (pfza_raw.groupby(group_cols)[vars_a_agregar]
                        .mean()
                        .reset_index())
        else:
            pfza = pfza_raw.copy()

        data = {
            'base':        base,
            'rendimiento': rend,
            'pfza':        pfza,
        }
        _cache = {'data': data, 'mtime': mtime}
        return data

    except Exception as e:
        import sys
        print(f"[ERROR load_data] {e}", file=sys.stderr)
        return _cache.get('data', None)


def get_categorias(data):
    cats = set()
    for hoja in ['base', 'rendimiento', 'pfza']:
        if hoja in data and 'Categoria' in data[hoja].columns:
            vals = data[hoja]['Categoria'].dropna().unique()
            cats.update([v for v in vals if v and v.strip()])
    return sorted(cats)


def get_jugadores_por_categoria(data, categoria):
    if data is None or 'base' not in data:
        return []
    base = data['base']
    cat_norm = _normalizar_categoria(categoria)
    mask = base['Categoria'].apply(_normalizar_categoria) == cat_norm
    df_cat = base[mask]
    jugadores = []
    for _, row in df_cat.iterrows():
        dni = row.get('DNI')
        if pd.isna(dni):
            continue
        nombre = str(row.get('NombreCompleto', '')).strip()
        if not nombre:
            nombre = (f"{row.get('Nombre','')} {row.get('Apellido','')}".strip())
        if not nombre:
            nombre = f"DNI {int(dni)}"
        jugadores.append({'DNI': int(dni), 'NombreCompleto': nombre})
    return jugadores


def get_vars_rendimiento(data):
    if data is None or 'rendimiento' not in data:
        return []
    cols = data['rendimiento'].columns.tolist()
    return [v for v in VARS_RENDIMIENTO if v in cols]


def get_vars_pfza(data):
    if data is None or 'pfza' not in data:
        return []
    cols = data['pfza'].columns.tolist()
    return [v for v in VARS_PFZA if v in cols]


def get_available_months(data):
    meses = set()
    for hoja in ['rendimiento', 'pfza']:
        if hoja not in data:
            continue
        df = data[hoja]
        if 'Fecha' not in df.columns:
            continue
        try:
            periodos = (
                pd.to_datetime(df['Fecha'], errors='coerce')
                .dt.to_period('M').astype(str).dropna()
            )
            meses.update([m for m in periodos if m and m != 'NaT'])
        except Exception:
            pass
    return sorted(meses)


def filter_by_month_smart(df, mes_str, categoria=None):
    """Filtra por mes YYYY-MM usando columna 'Fecha' (nunca 'Fecha de nacimiento')."""
    if df is None or df.empty or not mes_str:
        return df.iloc[0:0] if df is not None else pd.DataFrame()

    fecha_col = 'Fecha' if 'Fecha' in df.columns else None
    if fecha_col is None:
        for col in df.columns:
            col_l = col.lower()
            if 'nacimiento' in col_l or 'nac' in col_l:
                continue
            if any(kw in col_l for kw in ['fecha', 'date', 'mes', 'period']):
                fecha_col = col
                break

    if fecha_col is None:
        return df.iloc[0:0]

    try:
        periodos = (
            pd.to_datetime(df[fecha_col], errors='coerce')
            .dt.to_period('M').astype(str)
        )
        resultado = df[periodos == mes_str].copy()
        if categoria and 'Categoria' in resultado.columns:
            cat_norm = _normalizar_categoria(categoria)
            resultado = resultado[
                resultado['Categoria'].apply(_normalizar_categoria) == cat_norm
            ]
        return resultado
    except Exception:
        return df.iloc[0:0]
