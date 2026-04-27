import pandas as pd
from data_loader import load_data, get_vars_pfza
from pages.swc_page import crear_squad_swc, _norm_cat

def debug_altura_salto_especifico():
    """Debug específico para el problema con 'Altura Salto'"""
    print("=== DEBUG ALTURA SALTO ESPECÍFICO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    variable = 'Altura Salto'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"Parámetros: {categoria} / {variable} / {mes_pre} > {mes_post}")
    
    # 1. Verificar que la variable existe en pfza
    print("1. VERIFICACIÓN DE VARIABLE EN PFZA:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        print(f"   Columnas en pfza: {df_pfza.columns.tolist()}")
        print(f"   'Altura Salto' en columnas: {'Altura Salto' in df_pfza.columns}")
        
        if 'Altura Salto' in df_pfza.columns:
            vals_altura = df_pfza['Altura Salto'].dropna()
            print(f"   Valores 'Altura Salto': {len(vals_altura)}")
            print(f"   Rango: {vals_altura.min():.2f} - {vals_altura.max():.2f}")
            print(f"   Valores únicos: {sorted(vals_altura.unique())}")
        else:
            print("   ERROR: 'Altura Salto' no encontrada en pfza")
            return
    
    # 2. Verificar variables detectadas por get_vars_pfza
    print(f"\n2. VARIABLES DETECTADAS POR get_vars_pfza:")
    
    vars_pfza = get_vars_pfza(data)
    print(f"   Variables detectadas: {vars_pfza}")
    print(f"   'Altura Salto' detectada: {'Altura Salto' in vars_pfza}")
    
    # 3. Verificar filtrado por categoría
    print(f"\n3. VERIFICACIÓN DE FILTRADO POR CATEGORÍA:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        cat_norm = _norm_cat(categoria)
        print(f"   Categoría normalizada: '{categoria}' -> '{cat_norm}'")
        
        df_cat = df_pfza[df_pfza['Categoria'].apply(_norm_cat) == cat_norm]
        print(f"   Registros filtrados: {len(df_cat)}")
        
        if len(df_cat) > 0:
            vals_altura_cat = df_cat['Altura Salto'].dropna()
            print(f"   Valores 'Altura Salto' en '{categoria}': {len(vals_altura_cat)}")
            print(f"   Rango: {vals_altura_cat.min():.2f} - {vals_altura_cat.max():.2f}")
            print(f"   Valores únicos: {sorted(vals_altura_cat.unique())}")
        else:
            print(f"   ERROR: No hay registros para categoría '{categoria}'")
    
    # 4. Verificar filtrado por mes
    print(f"\n4. VERIFICACIÓN DE FILTRADO POR MES:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        # Filtrar por categoría primero
        cat_norm = _norm_cat(categoria)
        df_cat = df_pfza[df_pfza['Categoria'].apply(_norm_cat) == cat_norm]
        
        print(f"   Registros por categoría: {len(df_cat)}")
        
        if len(df_cat) > 0:
            # Filtrar por mes
            from pages.swc_page import _filtrar_mes_estricto
            
            pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
            post_cat = _filtrar_mes_estricto(df_cat, mes_post)
            
            print(f"   Registros Pre ({mes_pre}): {len(pre_cat)}")
            print(f"   Registros Post ({mes_post}): {len(post_cat)}")
            
            if len(pre_cat) > 0:
                vals_pre = pre_cat['Altura Salto'].dropna()
                print(f"   Valores Pre: {len(vals_pre)}")
                print(f"   Rango Pre: {vals_pre.min():.2f} - {vals_pre.max():.2f}")
                print(f"   Valores únicos Pre: {sorted(vals_pre.unique())}")
            
            if len(post_cat) > 0:
                vals_post = post_cat['Altura Salto'].dropna()
                print(f"   Valores Post: {len(vals_post)}")
                print(f"   Rango Post: {vals_post.min():.2f} - {vals_post.max():.2f}")
                print(f"   Valores únicos Post: {sorted(vals_post.unique())}")
        else:
            print(f"   ERROR: No hay registros para categoría '{categoria}'")
    
    # 5. Probar crear_squad_swc
    print(f"\n5. PRUEBA DE crear_squad_swc:")
    
    try:
        grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        
        if hasattr(grafico, 'figure'):
            fig = grafico.figure
            
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'y') and trace.y is not None:
                    puntos = len(trace.y)
                    print(f"   RESULTADO: CORRECTO - {puntos} puntos generados")
                    print(f"   Valores Y: {[f'{y:.1f}' for y in trace.y]}")
                else:
                    print(f"   RESULTADO: PROBLEMA - Sin datos Y")
            else:
                print(f"   RESULTADO: PROBLEMA - Sin traces")
        else:
            # Verificar si es un mensaje de error
            if hasattr(grafico, 'children'):
                mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                print(f"   MENSAJE: {mensaje}")
                
                if 'no tiene valores válidos' in mensaje:
                    print(f"   CAUSA: Variable sin valores válidos")
                elif 'no encontrada' in mensaje:
                    print(f"   CAUSA: Variable no encontrada")
                elif 'Sin datos' in mensaje:
                    print(f"   CAUSA: Sin datos para los meses")
                else:
                    print(f"   CAUSA: Mensaje inesperado")
            else:
                print(f"   RESULTADO: TIPO INESPERADO")
                
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Análisis completado. Revisar los resultados para identificar el problema.")

if __name__ == "__main__":
    debug_altura_salto_especifico()
