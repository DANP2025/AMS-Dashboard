import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def debug_potencia_pico():
    """Debug específico para Potencia Pico en categoría Primera."""
    print("=== DEBUG POTENCIA PICO - CATEGORÍA PRIMERA ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    variable = 'Potencia Pico'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"Parámetros: {categoria} / {variable} / {mes_pre} > {mes_post}")
    
    # 1. Verificar datos crudos
    print(f"\n1. DATOS CRUDOS:")
    
    vars_pfza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250']
    print(f"   Variables fuerza detectadas: {vars_pfza}")
    print(f"   'Potencia Pico' en variables: {'Potencia Pico' in vars_pfza}")
    
    # 2. Verificar datos en pfza
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        # Filtrar por categoría
        from pages.swc_page import _norm_cat
        cat_norm = _norm_cat(categoria)
        df_cat = df_pfza[df_pfza['Categoria'].apply(_norm_cat) == cat_norm]
        
        print(f"   Registros en categoría: {len(df_cat)}")
        
        if 'Potencia Pico' in df_cat.columns:
            vals_potencia = df_cat['Potencia Pico'].dropna()
            print(f"   Valores 'Potencia Pico': {len(vals_potencia)}")
            print(f"   Rango: {vals_potencia.min():.2f} a {vals_potencia.max():.2f}")
            print(f"   Valores únicos: {sorted(vals_potencia.unique())}")
        else:
            print(f"   ERROR: 'Potencia Pico' no encontrada en columnas")
            print(f"   Columnas disponibles: {df_cat.columns.tolist()}")
    
    # 3. Verificar filtrado por mes
    print(f"\n2. FILTRADO POR MES:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        cat_norm = _norm_cat(categoria)
        df_cat = df_pfza[df_pfza['Categoria'].apply(_norm_cat) == cat_norm]
        
        from pages.swc_page import _filtrar_mes_estricto
        
        pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
        post_cat = _filtrar_mes_estricto(df_cat, mes_post)
        
        print(f"   Registros Pre ({mes_pre}): {len(pre_cat)}")
        print(f"   Registros Post ({mes_post}): {len(post_cat)}")
        
        if len(pre_cat) > 0 and 'Potencia Pico' in pre_cat.columns:
            vals_pre = pre_cat['Potencia Pico'].dropna()
            print(f"   Valores Pre: {len(vals_pre)}")
            print(f"   Rango Pre: {vals_pre.min():.2f} a {vals_pre.max():.2f}")
            print(f"   SD Pre: {vals_pre.std(ddof=1):.4f}")
            
        if len(post_cat) > 0 and 'Potencia Pico' in post_cat.columns:
            vals_post = post_cat['Potencia Pico'].dropna()
            print(f"   Valores Post: {len(vals_post)}")
            print(f"   Rango Post: {vals_post.min():.2f} a {vals_post.max():.2f}")
    
    # 4. Probar el gráfico
    print(f"\n3. PRUEBA DEL GRÁFICO:")
    
    try:
        grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        
        if hasattr(grafico, 'figure'):
            fig = grafico.figure
            
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'y') and trace.y is not None:
                    valores_y = trace.y
                    puntos = len(valores_y)
                    
                    print(f"   Puntos generados: {puntos}")
                    print(f"   Valores Y: {[f'{y:.1f}' for y in valores_y]}")
                    
                    # Analizar el rango del eje Y
                    if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                        rango_grafico = fig.layout.yaxis.range
                        print(f"   Rango del gráfico: [{rango_grafico[0]:.1f}, {rango_grafico[1]:.1f}]")
                        
                        # Verificar si es simétrico
                        if abs(rango_grafico[0]) == abs(rango_grafico[1]):
                            print(f"   PROBLEMA: RANGO SIMÉTRICO detectado")
                        else:
                            print(f"   CORRECTO: Rango asimétrico")
                        
                        # Verificar si es demasiado grande
                        rango_total = abs(rango_grafico[1] - rango_grafico[0])
                        datos_max = max(abs(y) for y in valores_y) if valores_y else 0
                        
                        if rango_total > datos_max * 3:
                            print(f"   PROBLEMA: Rango demasiado grande ({rango_total:.1f} vs datos max {datos_max:.1f})")
                        else:
                            print(f"   CORRECTO: Rango proporcional a los datos")
                        
                        # Verificar si incluye -1400
                        if rango_grafico[0] <= -1400:
                            print(f"   PROBLEMA: El rango incluye -1400 (muy bajo)")
                            print(f"   Esto indica que el cálculo de rangos es incorrecto")
                    else:
                        print(f"   ERROR: No se encontró rango del eje Y")
                else:
                    print(f"   ERROR: Sin datos Y")
            else:
                print(f"   ERROR: Sin traces")
        else:
            if hasattr(grafico, 'children'):
                mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                print(f"   ERROR: {mensaje[:100]}...")
            else:
                print(f"   ERROR: Tipo inesperado")
                
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Si el rango del gráfico muestra -1400, el problema está en:")
    print("1. El cálculo de cambio_min/cambio_max")
    print("2. El cálculo del margen (25% del rango)")
    print("3. El ajuste final con SWC * 2.0")
    print("Revisar estos cálculos paso a paso")

if __name__ == "__main__":
    debug_potencia_pico()
