import numpy as np
import pandas as pd
from scipy.stats import norm

ICC = 0.90

def calc_mbd(pre, post, sd_grupo_serie):
    """
    Calcula MBD completo según Will Hopkins (Magnitude-Based Decisions).
    pre, post: float — valores individuales del jugador
    sd_grupo_serie: pd.Series — valores de la variable para toda la categoría en el pre-test
    Retorna dict con todos los resultados o None si faltan datos.
    """
    if pd.isna(pre) or pd.isna(post):
        return None

    sd_vals = sd_grupo_serie.dropna()
    if len(sd_vals) < 2:
        return None

    sd_pre = float(sd_vals.std(ddof=1))
    if sd_pre == 0:
        return None

    SWC       = 0.2 * sd_pre
    TE        = sd_pre * np.sqrt(1 - ICC)   # TE desde ICC = 0.90
    SE_cambio = TE * np.sqrt(2)             # error del cambio (2 mediciones)
    cambio    = post - pre
    effect_size   = cambio / sd_pre
    incertidumbre = 1.96 * SE_cambio        # IC 95%

    prob_ben  = float(1 - norm.cdf((SWC  - cambio) / SE_cambio))
    prob_per  = float(norm.cdf(    (-SWC - cambio) / SE_cambio))
    prob_triv = max(0.0, 1.0 - prob_ben - prob_per)

    # ── UN SOLO return ─────────────────────────────────────────────────
    return {
        'pre':          pre,
        'post':         post,
        'cambio':       cambio,
        'effect_size':  effect_size,
        'sd_pre':       sd_pre,
        'SWC':          SWC,
        'TE':           TE,
        'SE_cambio':    SE_cambio,
        'incertidumbre':incertidumbre,
        'prob_ben':     prob_ben,
        'prob_per':     prob_per,
        'prob_triv':    prob_triv,
        'limite_inf':   cambio - incertidumbre,
        'limite_sup':   cambio + incertidumbre,
    }


def get_etiqueta_inferencia(p_ben, p_per):
    """
    Etiquetas de inferencia según Will Hopkins — MBI/MBD framework.
    
    Umbrales de probabilidad (Hopkins 2006, 2016):
      >99.5% → Casi Seguro
      95–99.5% → Muy Probable
      75–95%   → Probable
      25–75%   → Posible
      5–25%    → Improbable
      0.5–5%   → Muy Improbable
      <0.5%    → Casi Seguro que No
    
    Claridad: resultado es NO CLARO si P_Ben > 0.05 Y P_Per > 0.05
    simultáneamente (incertidumbre clínica real).
    """
    no_claro = (p_ben > 0.05) and (p_per > 0.05)
    sufijo   = " (NO CLARO)" if no_claro else " (CLARO)"

    # ── PERJUDICIAL — evaluar de mayor a menor certeza ──────────────────
    if p_per > 0.995:
        return "Casi Seguro Perjudicial"   + sufijo
    if p_per > 0.95:
        return "Muy Probable Perjudicial"  + sufijo
    if p_per > 0.75:
        return "Probable Perjudicial"      + sufijo
    if p_per > 0.25:
        return "Posible Perjudicial"       + sufijo

    # ── BENEFICIOSO — evaluar de mayor a menor certeza ─────────────────
    if p_ben > 0.995:
        return "Casi Seguro Beneficioso"   + sufijo
    if p_ben > 0.95:
        return "Muy Probable Beneficioso"  + sufijo
    if p_ben > 0.75:
        return "Probable Beneficioso"      + sufijo
    if p_ben > 0.25:
        return "Posible Beneficioso"       + sufijo

    # ── TRIVIAL ─────────────────────────────────────────────────────────
    return "Trivial" + sufijo


# ── PALETA DE COLORES (coincide exactamente con zonas del Forest Plot) ──────

# Fondo de celda según etiqueta
COLORES_FONDO = {
    "Casi Seguro Beneficioso":  "#155724",   # verde muy oscuro
    "Muy Probable Beneficioso": "#1e7e34",   # verde oscuro
    "Probable Beneficioso":     "#28a745",   # verde medio
    "Posible Beneficioso":      "#c3e6cb",   # verde muy claro
    "Casi Seguro Perjudicial":  "#721c24",   # rojo muy oscuro
    "Muy Probable Perjudicial": "#c82333",   # rojo oscuro
    "Probable Perjudicial":     "#dc3545",   # rojo medio
    "Posible Perjudicial":      "#f5c6cb",   # rojo muy claro
    "Trivial":                  "#e9ecef",   # gris claro
}

# Color de texto: blanco sobre fondos oscuros, oscuro sobre fondos claros
COLORES_TEXTO = {
    "Casi Seguro Beneficioso":  "#ffffff",
    "Muy Probable Beneficioso": "#ffffff",
    "Probable Beneficioso":     "#ffffff",
    "Posible Beneficioso":      "#155724",   # texto verde oscuro sobre fondo verde claro
    "Casi Seguro Perjudicial":  "#ffffff",
    "Muy Probable Perjudicial": "#ffffff",
    "Probable Perjudicial":     "#ffffff",
    "Posible Perjudicial":      "#721c24",   # texto rojo oscuro sobre fondo rojo claro
    "Trivial":                  "#495057",   # texto gris oscuro
}

def get_color_etiqueta(etiqueta):
    """Devuelve (color_fondo, color_texto) para una etiqueta dada."""
    # Extraer la parte sin el sufijo CLARO/NO CLARO
    clave = etiqueta.replace(" (CLARO)", "").replace(" (NO CLARO)", "").strip()
    fondo = COLORES_FONDO.get(clave, "#e9ecef")
    texto = COLORES_TEXTO.get(clave, "#495057")
    return fondo, texto
