import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def debug_simetria_eje_y():
    """Debug para analizar problema de simetría del eje Y."""
    print("=== DEBUG SIMETRÍA EJE Y ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    variable = 'Potencia Pico'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"Parámetros: {categoria} / {variable} / {mes_pre} > {mes_post}")
    
    try:
        grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        
        if hasattr(grafico, 'figure'):
            fig = grafico.figure
            
            print("1. ANÁLISIS DEL GRÁFICO ACTUAL:")
            
            # Verificar datos del gráfico
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'x') and hasattr(trace, 'y'):
                    x_vals = trace.x
                    y_vals = trace.y
                    
                    print(f"   Puntos generados: {len(x_vals)}")
                    print(f"   Valores X (Post): {[f'{x:.1f}' for x in x_vals]}")
                    print(f"   Valores Y (Cambio): {[f'{y:.1f}' for y in y_vals]}")
                    
                    # Verificar rangos del eje Y
                    if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                        rango_y = fig.layout.yaxis.range
                        print(f"   Rango del eje Y: [{rango_y[0]:.1f}, {rango_y[1]:.1f}]")
                        
                        # Verificar si es simétrico
                        if abs(rango_y[0]) == abs(rango_y[1]):
                            print("   CORRECTO: Rango simetrico")
                        else:
                            print("   PROBLEMA: Rango no simetrico")
                        
                        # Verificar si los valores son demasiado grandes
                        if abs(rango_y[0]) > 100 or abs(rango_y[1]) > 100:
                            print("   PROBLEMA: Valores del eje Y demasiado grandes (>100)")
                            print("   Esto indica que se estan usando cambios absolutos en lugar de ES")
                        
                        # Verificar si los valores son pequeños (como deberian ser para ES)
                        if abs(rango_y[0]) <= 10 and abs(rango_y[1]) <= 10:
                            print("   CORRECTO: Valores del eje Y pequenos (como ES)")
                    
                    # Analizar los datos para determinar si son cambios absolutos o ES
                    print(f"\n2. ANÁLISIS DE DATOS:")
                    
                    # Calcular estadísticas de los valores Y
                    y_series = pd.Series(y_vals)
                    y_mean = y_series.mean()
                    y_std = y_series.std(ddof=1)
                    y_min = y_series.min()
                    y_max = y_series.max()
                    
                    print(f"   Media de Y: {y_mean:.2f}")
                    print(f"   SD de Y: {y_std:.2f}")
                    print(f"   Rango de Y: [{y_min:.1f}, {y_max:.1f}]")
                    
                    # Determinar si son cambios absolutos o ES
                    if abs(y_mean) > 100 or abs(y_std) > 100:
                        print("   PROBLEMA: Los valores Y son cambios absolutos (grandes)")
                        print("   Deberian ser ES (Effect Size) para tener valores pequenos")
                    else:
                        print("   CORRECTO: Los valores Y parecen ser ES (pequenos)")
                    
                    # Verificar si hay valores negativos y positivos
                    negativos = sum(1 for y in y_vals if y < 0)
                    positivos = sum(1 for y in y_vals if y > 0)
                    
                    print(f"   Valores negativos: {negativos}/{len(y_vals)}")
                    print(f"   Valores positivos: {positivos}/{len(y_vals)}")
                    
                    if negativos > 0 and positivos > 0:
                        print("   CORRECTO: Hay valores negativos y positivos (buena distribucion)")
                    elif negativos > 0 and positivos == 0:
                        print("   ADVERTENCIA: Todos los valores son negativos")
                    elif negativos == 0 and positivos > 0:
                        print("   ADVERTENCIA: Todos los valores son positivos")
                    
                    # Calcular como deberian ser los ES
                    print(f"\n3. CÁLCULO DE ES CORRECTO:")
                    
                    # Obtener datos originales para calcular ES correctamente
                    if 'pfza' in data:
                        pfza = data['pfza']
                        pfza_cat = pfza[pfza['Categoria'] == categoria]
                        
                        from data_loader import filter_by_month_smart
                        pre_cat = filter_by_month_smart(pfza_cat, mes_pre)
                        post_cat = filter_by_month_smart(pfza_cat, mes_post)
                        
                        if variable in pre_cat.columns and variable in post_cat.columns:
                            vals_pre = pre_cat[variable].dropna()
                            vals_post = post_cat[variable].dropna()
                            
                            if len(vals_pre) > 1:
                                sd_grupo = float(vals_pre.std(ddof=1))
                                print(f"   SD del grupo: {sd_grupo:.2f}")
                                
                                # Calcular ES para cada jugador
                                es_correctos = []
                                for i, row in pre_cat.iterrows():
                                    dni = row['DNI']
                                    pre_val = row[variable]
                                    
                                    post_row = post_cat[post_cat['DNI'] == dni]
                                    if not post_row.empty:
                                        post_val = post_row[variable].iloc[0]
                                        cambio = post_val - pre_val
                                        es = cambio / sd_grupo
                                        es_correctos.append(es)
                                
                                if es_correctos:
                                    es_mean = pd.Series(es_correctos).mean()
                                    es_std = pd.Series(es_correctos).std(ddof=1)
                                    es_min = min(es_correctos)
                                    es_max = max(es_correctos)
                                    
                                    print(f"   ES correctos:")
                                    print(f"     Media: {es_mean:.2f}")
                                    print(f"     SD: {es_std:.2f}")
                                    print(f"     Rango: [{es_min:.2f}, {es_max:.2f}]")
                                    
                                    # Rango simetrico sugerido para ES
                                    max_es = max(abs(es_min), abs(es_max))
                                    rango_sugerido = [-max_es * 1.2, max_es * 1.2]
                                    print(f"   Rango simetrico sugerido: [{rango_sugerido[0]:.2f}, {rango_sugerido[1]:.2f}]")
                                    
                                    # Comparar con valores actuales
                                    if abs(y_min) > 100:
                                        print(f"\n   PROBLEMA CONFIRMADO:")
                                        print(f"   Valores actuales: [{y_min:.1f}, {y_max:.1f}]")
                                        print(f"   ES correctos: [{es_min:.2f}, {es_max:.2f}]")
                                        print(f"   El grafico esta usando cambios absolutos en lugar de ES")
                
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Si el eje Y muestra valores de 0 a 3000 en lugar de -5 a 5:")
    print("1. El grafico esta usando cambios absolutos (Post - Pre)")
    print("2. Deberia usar ES (Effect Size) = (Post - Pre) / SD")
    print("3. Los valores de ES son pequenos (-5 a 5) y simetricos")
    print("4. Necesito corregir el grafico para usar ES en el eje Y")

if __name__ == "__main__":
    debug_simetria_eje_y()
