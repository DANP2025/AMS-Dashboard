import pandas as pd
from data_loader import load_data

def debug_sd_plat_fuerza():
    """Debug para identificar el problema del SD en variables de Plat de fuerza."""
    print("=== DEBUG SD - PLAT DE FUERZA VS RENDIMIENTO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print("1. VARIABLES DE PLAT DE FUERZA:")
    
    if 'pfza' in data:
        pfza = data['pfza']
        
        # Filtrar por categoría
        pfza_cat = pfza[pfza['Categoria'] == categoria]
        
        # Filtrar por mes
        from data_loader import filter_by_month_smart
        
        pre_cat = filter_by_month_smart(pfza_cat, mes_pre)
        post_cat = filter_by_month_smart(pfza_cat, mes_post)
        
        vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
        
        for var in vars_fuerza:
            if var in pre_cat.columns and var in post_cat.columns:
                vals_pre = pre_cat[var].dropna()
                vals_post = post_cat[var].dropna()
                
                if len(vals_pre) > 1 and len(vals_post) > 1:
                    sd_pre = vals_pre.std(ddof=1)
                    sd_post = vals_post.std(ddof=1)
                    
                    print(f"\n   {var}:")
                    print(f"     Pre ({len(vals_pre)}): {vals_pre.min():.1f}-{vals_pre.max():.1f} | SD={sd_pre:.2f}")
                    print(f"     Post ({len(vals_post)}): {vals_post.min():.1f}-{vals_post.max():.1f} | SD={sd_post:.2f}")
                    
                    # Calcular SWC con SD del Pre (como en el código actual)
                    SWC = 0.2 * sd_pre
                    
                    # Calcular cambios para algunos jugadores
                    if len(pre_cat) > 0 and len(post_cat) > 0:
                        dni_comun = None
                        for dni in pre_cat['DNI'].unique():
                            if dni in post_cat['DNI'].values:
                                dni_comun = dni
                                break
                        
                        if dni_comun:
                            pre_val = pre_cat[pre_cat['DNI'] == dni_comun][var].iloc[0]
                            post_val = post_cat[post_cat['DNI'] == dni_comun][var].iloc[0]
                            cambio = post_val - pre_val
                            es = cambio / sd_pre if sd_pre != 0 else 0
                            
                            print(f"     Ejemplo: pre={pre_val:.1f} post={post_val:.1f} cambio={cambio:+.1f} ES={es:+.2f}")
                            print(f"     SWC: {SWC:.2f}")
                else:
                    print(f"\n   {var}: No encontrada o sin datos suficientes")
    
    print(f"\n2. VARIABLES DE RENDIMIENTO:")
    
    if 'rendimiento' in data:
        rend = data['rendimiento']
        
        # Filtrar por categoría
        rend_cat = rend[rend['Categoria'] == categoria]
        
        # Filtrar por mes
        pre_cat = filter_by_month_smart(rend_cat, mes_pre)
        post_cat = filter_by_month_smart(rend_cat, mes_post)
        
        vars_rend = ['VO2 max', 'F0', 'V0', 'Pmax', 'Vmax', 'RF', 'DRF']
        
        for var in vars_rend:
            if var in pre_cat.columns and var in post_cat.columns:
                vals_pre = pre_cat[var].dropna()
                vals_post = post_cat[var].dropna()
                
                if len(vals_pre) > 1 and len(vals_post) > 1:
                    sd_pre = vals_pre.std(ddof=1)
                    sd_post = vals_post.std(ddof=1)
                    
                    print(f"\n   {var}:")
                    print(f"     Pre ({len(vals_pre)}): {vals_pre.min():.2f}-{vals_pre.max():.2f} | SD={sd_pre:.2f}")
                    print(f"     Post ({len(vals_post)}): {vals_post.min():.2f}-{vals_post.max():.2f} | SD={sd_post:.2f}")
                else:
                    print(f"\n   {var}: No encontrada o sin datos suficientes")
    
    print(f"\n=== ANÁLISIS DEL PROBLEMA ===")
    print("Si las variables de Plat de fuerza tienen valores correctos (1000-5000)")
    print("pero el eje Y muestra valores incorrectos (-1500, etc.), el problema es:")
    print("1. SD demasiado alta para variables de fuerza")
    print("2. ES (cambio/SD) demasiado pequeño")
    print("3. El cálculo de SD está usando datos incorrectos")
    print("4. La agregación de pfza está afectando el cálculo de SD")

if __name__ == "__main__":
    debug_sd_plat_fuerza()
