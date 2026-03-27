import pandas as pd
import numpy as np
from scipy import stats


# ─── Z-SCORE ──────────────────────────────────────────────────────────────────

def calc_zscore(valor_jugador, serie_comparacion):
    """
    Calcula el Z-score de un jugador respecto a un grupo de comparación.
    Z = (valor - media_grupo) / std_grupo
    Retorna np.nan si no hay datos suficientes o el valor es nulo.
    """
    if pd.isna(valor_jugador):
        return np.nan
    validos = serie_comparacion.dropna()
    if len(validos) < 2:
        return np.nan
    media = validos.mean()
    desvio = validos.std()
    if desvio == 0 or pd.isna(desvio):
        return 0.0
    return float((valor_jugador - media) / desvio)


# ─── MBD — MAGNITUD BASADA EN DECISIONES (Will Hopkins) ─────────────────────

def calc_mbd(pre_val, post_val, serie_pre_grupo, icc_estimado=0.90):
    """
    Calcula la Magnitud Basada en Decisiones según Will Hopkins.

    Parámetros:
    - pre_val          : valor del jugador en pre-test
    - post_val         : valor del jugador en post-test
    - serie_pre_grupo  : Serie con valores de TODO el grupo en pre-test (para SD)
    - icc_estimado     : ICC estimado del test (default 0.90, típico para tests físicos)

    Fórmulas (Hopkins, 2022):
    - SWC  = 0.2 × SD_pre          (Smallest Worthwhile Change)
    - TE   = SD_pre × √(1 - ICC)   (Error Típico estimado)
    - Prob_beneficiosa = P(efecto_real > SWC)
    - Prob_perjudicial = P(efecto_real < -SWC)
    - Prob_trivial     = 1 - Prob_ben - Prob_per
    - Effect Size      = cambio / SD_pre   (estandarizado)
    """
    if pd.isna(pre_val) or pd.isna(post_val):
        return None

    validos_grupo = serie_pre_grupo.dropna()
    if len(validos_grupo) < 2:
        return None

    sd_pre = validos_grupo.std()
    if sd_pre == 0 or pd.isna(sd_pre):
        return None

    cambio = float(post_val) - float(pre_val)
    swc = 0.2 * sd_pre                          # Cambio Mínimo Apreciable
    te = sd_pre * np.sqrt(1 - icc_estimado)     # Error Típico
    incertidumbre = te * np.sqrt(2)             # Incertidumbre del cambio

    if incertidumbre == 0:
        prob_ben = 1.0 if cambio > swc else 0.0
        prob_per = 1.0 if cambio < -swc else 0.0
    else:
        prob_ben = float(1 - stats.norm.cdf(swc, loc=cambio, scale=incertidumbre))
        prob_per = float(stats.norm.cdf(-swc, loc=cambio, scale=incertidumbre))

    prob_trivial = max(0.0, 1.0 - prob_ben - prob_per)
    effect_size = cambio / sd_pre

    return {
        'cambio': cambio,
        'effect_size': effect_size,       # en unidades de SD
        'swc': swc,
        'te': te,
        'incertidumbre': incertidumbre,
        'prob_ben': prob_ben,
        'prob_per': prob_per,
        'prob_trivial': prob_trivial,
        'sd_pre': sd_pre,
    }


def get_etiqueta_inferencia(prob_ben, prob_per):
    """
    Etiqueta de inferencia según Hopkins.
    Traducción exacta del DAX original del archivo Power BI.

    Lógica:
    - Primero evalúa riesgos (rojos)
    - Luego evalúa beneficios (verdes)
    - Por último lo incierto/trivial
    - Calificador CLARO/NO CLARO: NO CLARO si ambas prob > 5%
    """
    p_ben = prob_ben
    p_per = prob_per

    # Claridad
    es_claro = not (p_ben > 0.05 and p_per > 0.05)
    claridad = "CLARO" if es_claro else "NO CLARO"

    # Evaluación (orden del DAX original)
    if p_per > 0.95:
        etiqueta = "Muy Improbable"
    elif p_per > 0.75:
        etiqueta = "Improbable"
    elif p_ben > 0.995:
        etiqueta = "Casi Seguro"
    elif p_ben > 0.95:
        etiqueta = "Muy Probable"
    elif p_ben > 0.75:
        etiqueta = "Probable"
    elif p_ben > 0.25:
        etiqueta = "Posible"
    else:
        etiqueta = "Trivial"

    return f"{etiqueta} ({claridad})"


def get_color_etiqueta(etiqueta):
    """Color de fondo para cada etiqueta de inferencia."""
    if "Casi Seguro" in etiqueta:
        return "#0d6e33"
    elif "Muy Probable" in etiqueta:
        return "#1a7c3e"
    elif "Probable" in etiqueta:
        return "#28a745"
    elif "Posible" in etiqueta:
        return "#5cb85c"
    elif "Trivial" in etiqueta:
        return "#495057"
    elif "Improbable" in etiqueta and "Muy" not in etiqueta:
        return "#c0392b"
    elif "Muy Improbable" in etiqueta:
        return "#7b241c"
    return "#495057"
