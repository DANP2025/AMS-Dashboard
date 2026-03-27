import pandas as pd
import numpy as np
import os
import re

# Ruta al archivo Excel (está en C:\Dany\AMS\AMS.xlsx)
EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'AMS.xlsx'
)

def normalize_categoria(cat):
    """Normaliza nombres de categoría a formato 'Sub 15', 'Sub 16', etc."""
    if pd.isna(cat) or cat is None:
        return None
    cat = str(cat).strip()
    cat = ' '.join(cat.split())  # elimina espacios dobles
    match = re.match(r'sub\s*(\d+)', cat, re.IGNORECASE)
    if match:
        return f"Sub {match.group(1)}"
    # Para Primera, Reserva, etc.
    return cat.capitalize()

def get_file_modified_time():
    """Devuelve la fecha de última modificación del Excel."""
    try:
        return os.path.getmtime(EXCEL_PATH)
    except Exception:
        return None

def load_data():
    """Carga y procesa todas las hojas necesarias del Excel AMS.xlsx."""
    try:
        xl = pd.ExcelFile(EXCEL_PATH)

        # — Base de datos (fuente principal de jugadores y categorías) —
        df_base = pd.read_excel(xl, 'Base de datos')
        df_base['Categoria'] = df_base['Categoria'].apply(normalize_categoria)
        df_base['NombreCompleto'] = (
            df_base['Nombre'].astype(str).str.strip() + ' ' +
            df_base['Apellido'].astype(str).str.strip()
        )

        # — Rendimiento —
        df_rend = pd.read_excel(xl, 'Rendimiento', parse_dates=['Fecha'])
        df_rend['Categoria'] = df_rend['Categoria'].apply(normalize_categoria)
        df_rend['Fecha'] = pd.to_datetime(df_rend['Fecha'], errors='coerce')

        # — Plat de fuerza —
        df_pfza = pd.read_excel(xl, 'Plat de fuerza', parse_dates=['Fecha'])
        df_pfza['Categoria'] = df_pfza['Categoria'].apply(normalize_categoria)
        df_pfza['Fecha'] = pd.to_datetime(df_pfza['Fecha'], errors='coerce')

        return {
            'base': df_base,
            'rendimiento': df_rend,
            'pfza': df_pfza
        }
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el Excel: {e}")
        return None

def get_categorias(data):
    """Lista de categorías únicas normalizadas (fuente: Base de datos)."""
    cats = data['base']['Categoria'].dropna().unique().tolist()
    return sorted(cats)

def get_jugadores_por_categoria(data, categoria):
    """Jugadores de una categoría. Devuelve lista de dicts {DNI, NombreCompleto}."""
    df = data['base'][data['base']['Categoria'] == categoria]
    return df[['DNI', 'NombreCompleto']].dropna().to_dict('records')

def get_vars_rendimiento(data):
    """
    Detecta AUTOMÁTICAMENTE las variables numéricas de la hoja Rendimiento.
    Excluye columnas de identificación. Si en el futuro se agregan columnas,
    se detectan solas.
    """
    excluir = {
        'DNI', 'Apellido', 'Fecha de nacimiento', 'Fecha',
        'Categoria', 'Edad decimal', 'Peso', '30-15 IFT'
    }
    df = data['rendimiento']
    return [
        c for c in df.columns
        if c not in excluir and pd.api.types.is_numeric_dtype(df[c])
    ]

def get_vars_pfza(data):
    """
    Detecta AUTOMÁTICAMENTE las variables numéricas de la hoja Plat de fuerza.
    Si en el futuro se agregan columnas, se detectan solas.
    """
    excluir = {
        'DNI', 'Apellido', 'Fecha', 'Categoria', 'Test', 'Subtipo',
        'Total', 'Pierna Izquierda', 'Pierna Derecha', 'Asimetria %'
    }
    df = data['pfza']
    return [
        c for c in df.columns
        if c not in excluir and pd.api.types.is_numeric_dtype(df[c])
    ]

def get_available_months(data):
    """Meses disponibles (unión de Rendimiento y Plat de fuerza), ordenados."""
    m1 = data['rendimiento']['Fecha'].dropna().dt.to_period('M').astype(str).unique().tolist()
    m2 = data['pfza']['Fecha'].dropna().dt.to_period('M').astype(str).unique().tolist()
    return sorted(list(set(m1 + m2)))

def filter_by_month(df, year_month_str):
    """Filtra un DataFrame por año-mes (formato 'YYYY-MM')."""
    df = df.copy()
    df['_ym'] = df['Fecha'].dt.to_period('M').astype(str)
    result = df[df['_ym'] == year_month_str].drop(columns=['_ym'])
    return result

def latest_per_player(df):
    """Para cada jugador (DNI) toma su medición más reciente."""
    if df.empty:
        return df
    return df.sort_values('Fecha').groupby('DNI').last().reset_index()
