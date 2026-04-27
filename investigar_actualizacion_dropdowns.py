import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto, _corregir_altura_salto

def investigar_actualizacion_dropdowns():
    """Investigar por qué los gráficos no se actualizan al cambiar fechas en dropdowns."""
    print("=== INVESTIGACIÓN - ACTUALIZACIÓN DE DROPDOWNS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar el callback de actualización
    print("1. VERIFICACIÓN DEL CALLBACK DE ACTUALIZACIÓN:")
    print("   El callback debería responder a:")
    print("   - Input('swc-mes-pre', 'value')")
    print("   - Input('swc-mes-post', 'value')")
    print("   - Input('swc-categoria', 'value')")
    print("   - Input('swc-variable', 'value')")
    
    # 2. Probar diferentes combinaciones de fechas para Primera y Pmax
    print(f"\n2. PRUEBA DE COMBINACIONES - Primera / Pmax:")
    
    categoria = 'Primera'
    variable = 'Pmax'  # Pmax es 'Pmax' en rendimiento, 'Potencia Pico' en pfza
    
    # Verificar qué hoja contiene la variable
    hoja = None
    if 'rendimiento' in data:
        df_rend = data['rendimiento']
        if variable in df_rend.columns:
            hoja = 'rendimiento'
            print(f"   Variable '{variable}' encontrada en hoja 'rendimiento'")
    
    if hoja is None and 'pfza' in data:
        df_pfza = data['pfza']
        # Pmax en rendimiento corresponde a 'Potencia Pico' en pfza
        if variable == 'Pmax':
            variable_pfza = 'Potencia Pico'
            if variable_pfza in df_pfza.columns:
                hoja = 'pfza'
                variable = variable_pfza
                print(f"   Variable '{variable}' (Pmax) encontrada en hoja 'pfza' como '{variable_pfza}'")
    
    if hoja is None:
        print(f"   ERROR: Variable 'Pmax' no encontrada en ninguna hoja")
        return
    
    df = data[hoja]
    
    # 3. Probar diferentes combinaciones de fechas
    combinaciones_fechas = [
        ('2025-12', '2026-01'),  # Combinación estándar
        ('2025-12', '2025-12'),  # Mismo mes
        ('2026-01', '2026-01'),  # Mismo mes
        ('2025-12', '2025-11'),  # Mes anterior (no debería tener datos)
        ('2026-02', '2026-01'),  # Mes futuro (no debería tener datos)
    ]
    
    for mes_pre, mes_post in combinaciones_fechas:
        print(f"\n   --- Combinación: {mes_pre} > {mes_post} ---")
        
        # Filtrar por categoría
        df_cat = df[df['Categoria'] == categoria].copy()
        print(f"   Registros categoría '{categoria}': {len(df_cat)}")
        
        # Aplicar filtros de mes
        pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
        post_cat = _filtrar_mes_estricto(df_cat, mes_post)
        
        print(f"   Registros Pre ({mes_pre}): {len(pre_cat)}")
        print(f"   Registros Post ({mes_post}): {len(post_cat)}")
        
        # Verificar datos de la variable
        if len(pre_cat) > 0:
            pre_vals = pre_cat[variable].dropna()
            print(f"   Valores Pre ({variable}): {len(pre_vals)}")
            if len(pre_vals) > 0:
                print(f"     Rango Pre: {pre_vals.min():.2f} - {pre_vals.max():.2f}")
        
        if len(post_cat) > 0:
            post_vals = post_cat[variable].dropna()
            print(f"   Valores Post ({variable}): {len(post_vals)}")
            if len(post_vals) > 0:
                print(f"     Rango Post: {post_vals.min():.2f} - {post_vals.max():.2f}")
        
        # Calcular cambios si hay datos en ambos meses
        if len(pre_cat) > 0 and len(post_cat) > 0:
            cambios = []
            for _, row_pre in pre_cat.iterrows():
                apellido = row_pre['Apellido']
                pre_val = row_pre[variable]
                
                if pd.notna(pre_val):
                    match_post = post_cat[post_cat['Apellido'].str.strip().str.lower() == apellido.strip().lower()]
                    if not match_post.empty:
                        post_val = match_post.iloc[0][variable]
                        if pd.notna(post_val):
                            cambio = post_val - pre_val
                            cambios.append(cambio)
            
            if cambios:
                print(f"   Cambios calculados: {len(cambios)}")
                print(f"   Rango cambios: {min(cambios):+.2f} a {max(cambios):+.2f}")
                print(f"   RESULTADO: Se puede generar gráfico")
            else:
                print(f"   RESULTADO: No hay cambios calculados")
        else:
            print(f"   RESULTADO: No hay datos suficientes")
    
    # 4. Verificar si hay problema con el callback
    print(f"\n3. VERIFICACIÓN DEL CALLBACK:")
    print("   Revisando el código del callback en swc_page.py...")
    
    # Leer el callback para verificar inputs
    try:
        with open('C:/Dany/AMS/Dash/pages/swc_page.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar el callback principal
        if '@callback(' in contenido and 'swc-mes-pre' in contenido:
            print("   Callback encontrado con inputs correctos")
            
            # Verificar que todos los inputs estén presentes
            inputs_requeridos = ['swc-mes-pre', 'swc-mes-post', 'swc-categoria', 'swc-variable']
            for input_req in inputs_requeridos:
                if input_req in contenido:
                    print(f"   Input '{input_req}': PRESENTE")
                else:
                    print(f"   Input '{input_req}': AUSENTE - PROBLEMA")
        else:
            print("   ERROR: Callback no encontrado o sin inputs correctos")
    
    except Exception as e:
        print(f"   Error leyendo el archivo: {e}")
    
    # 5. Verificar si hay cache o problemas de estado
    print(f"\n4. VERIFICACIÓN DE CACHE Y ESTADO:")
    print("   Posibles problemas:")
    print("   - Cache de datos no se actualiza")
    print("   - Callback no se dispara correctamente")
    print("   - Filtro de mes no funciona como esperado")
    print("   - Variable mapeada incorrectamente")
    
    # 6. Probar con otras variables para comparar
    print(f"\n5. COMPARACIÓN CON OTRAS VARIABLES:")
    
    otras_variables = ['Fuerza', 'Altura Salto']
    mes_pre, mes_post = '2025-12', '2026-01'
    
    for var in otras_variables:
        print(f"\n   --- Variable: {var} ---")
        
        if 'pfza' in data and var in data['pfza'].columns:
            df_pfza = data['pfza']
            df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
            
            pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
            post_cat = _filtrar_mes_estricto(df_cat, mes_post)
            
            if len(pre_cat) > 0 and len(post_cat) > 0:
                cambios = []
                for _, row_pre in pre_cat.iterrows():
                    apellido = row_pre['Apellido']
                    pre_val = row_pre[var]
                    
                    if pd.notna(pre_val):
                        match_post = post_cat[post_cat['Apellido'].str.strip().str.lower() == apellido.strip().lower()]
                        if not match_post.empty:
                            post_val = match_post.iloc[0][var]
                            if pd.notna(post_val):
                                cambio = post_val - pre_val
                                cambios.append(cambio)
                
                if cambios:
                    print(f"   Cambios: {len(cambios)} (rango: {min(cambios):+.2f} a {max(cambios):+.2f})")
                else:
                    print(f"   Sin cambios calculados")
            else:
                print(f"   Sin datos suficientes")
        else:
            print(f"   Variable no encontrada")

if __name__ == "__main__":
    investigar_actualizacion_dropdowns()
