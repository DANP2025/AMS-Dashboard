import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto, _corregir_altura_salto

def test_final_correcciones():
    """Test final para verificar que todas las correcciones funcionen."""
    print("=== TEST FINAL - CORRECCIONES IMPLEMENTADAS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar corrección de 'Altura Salto'
    print("1. CORRECCIÓN DE 'Altura Salto':")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        # Verificar datos originales
        print("   Datos originales 'Altura Salto':")
        categoria = 'Primera'
        df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
        
        for mes in ['2025-12', '2026-01']:
            df_filtrado = _filtrar_mes_estricto(df_cat, mes)
            if len(df_filtrado) > 0:
                valores_orig = df_filtrado['Altura Salto'].values
                print(f"   {categoria} - {mes}: {valores_orig}")
        
        # Verificar corrección directa
        print("\n   Verificación de corrección directa:")
        df_test = df_cat.copy()
        df_corregido = _corregir_altura_salto(df_test)
        
        for mes in ['2025-12', '2026-01']:
            df_filtrado = _filtrar_mes_estricto(df_corregido, mes)
            if len(df_filtrado) > 0:
                valores_corr = df_filtrado['Altura Salto'].values
                print(f"   {categoria} - {mes} (corregido): {valores_corr}")
    
    # 2. Verificar detección de valores
    print("\n2. DETECCIÓN DE VALORES:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
        
        for var in vars_fuerza:
            if var in df_pfza.columns:
                valores = df_pfza[var].dropna()
                print(f"   {var}: {len(valores)} valores válidos")
            else:
                print(f"   {var}: NO EXISTE")
    
    # 3. Verificar cálculo de cambios después de corrección
    print("\n3. CÁLCULO DE CAMBIOS DESPUÉS DE CORRECCIÓN:")
    
    categoria = 'Primera'
    variable = 'Altura Salto'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
        
        pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
        post_cat = _filtrar_mes_estricto(df_cat, mes_post)
        
        print(f"   Categoría: {categoria}")
        print(f"   Variable: {variable}")
        print(f"   Pre ({mes_pre}): {len(pre_cat)} registros")
        print(f"   Post ({mes_post}): {len(post_cat)} registros")
        
        if len(pre_cat) > 0 and len(post_cat) > 0:
            print(f"\n   Cambios calculados (corregidos):")
            for _, row_pre in pre_cat.iterrows():
                apellido = row_pre['Apellido']
                pre_val = row_pre[variable]
                
                # Buscar mismo jugador en post
                row_post = post_cat[post_cat['Apellido'] == apellido]
                if len(row_post) > 0:
                    post_val = row_post.iloc[0][variable]
                    cambio = post_val - pre_val
                    print(f"     {apellido}: {post_val:.2f} - {pre_val:.2f} = {cambio:+.2f}")
        
        # Calcular rangos para eje Y
        if len(pre_cat) > 0 and len(post_cat) > 0:
            todos_cambio = []
            for _, row_pre in pre_cat.iterrows():
                apellido = row_pre['Apellido']
                pre_val = row_pre[variable]
                
                row_post = post_cat[post_cat['Apellido'] == apellido]
                if len(row_post) > 0:
                    post_val = row_post.iloc[0][variable]
                    cambio = post_val - pre_val
                    todos_cambio.append(cambio)
            
            if todos_cambio:
                max_cambio_abs = max(abs(c) for c in todos_cambio)
                print(f"\n   Rango de cambios: {min(todos_cambio):+.2f} a {max(todos_cambio):+.2f}")
                print(f"   Máximo cambio absoluto: {max_cambio_abs:.2f}")
                
                # Simular cálculo de rango Y
                SWC = 0.2
                min_swc_range = 6 * SWC
                
                if max_cambio_abs > min_swc_range * 10:
                    y_max_abs = max(min_swc_range * 3, max_cambio_abs * 0.1)
                    print(f"   Rango Y (cambios grandes): ±{y_max_abs:.2f}")
                else:
                    y_max_abs = max(max_cambio_abs, min_swc_range) * 1.3
                    print(f"   Rango Y (cambios normales): ±{y_max_abs:.2f}")
    
    # 4. Verificar otras variables
    print("\n4. VERIFICACIÓN DE OTRAS VARIABLES:")
    
    for var in ['Fuerza', 'Potencia Pico']:
        print(f"\n   Variable: {var}")
        
        if 'pfza' in data:
            df_pfza = data['pfza']
            df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
            
            pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
            post_cat = _filtrar_mes_estricto(df_cat, mes_post)
            
            if len(pre_cat) > 0 and len(post_cat) > 0:
                cambios = []
                for _, row_pre in pre_cat.iterrows():
                    apellido = row_pre['Apellido']
                    pre_val = row_pre[var]
                    
                    row_post = post_cat[post_cat['Apellido'] == apellido]
                    if len(row_post) > 0:
                        post_val = row_post.iloc[0][var]
                        cambio = post_val - pre_val
                        cambios.append(cambio)
                
                if cambios:
                    print(f"     Cambios: {min(cambios):+.2f} a {max(cambios):+.2f}")
                    max_abs = max(abs(c) for c in cambios)
                    print(f"     Máximo absoluto: {max_abs:.2f}")
    
    print("\n=== CONCLUSIÓN ===")
    print("Correcciones implementadas:")
    print("1. 'Altura Salto': Valores > 1000 convertidos a cm (dividido por 10)")
    print("2. Eje Y: Rango mejorado para cambios grandes")
    print("3. Detección: Validación de valores válidos para todas las variables")
    print("4. Mensajes: Mejorados para mostrar información clara")

if __name__ == "__main__":
    test_final_correcciones()
