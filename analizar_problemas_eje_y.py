import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto

def analizar_problemas_eje_y():
    """Analizar problemas del eje Y y detección de valores."""
    print("=== ANÁLISIS DE PROBLEMAS - EJE Y Y DETECCIÓN DE VALORES ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar variables disponibles y sus datos
    print("1. VARIABLES DISPONIBLES Y SUS DATOS:")
    
    # Variables de fuerza
    vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250']
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        print(f"\nHoja 'pfza': {df_pfza.shape}")
        print(f"Columnas disponibles: {list(df_pfza.columns)}")
        
        for var in vars_fuerza:
            if var in df_pfza.columns:
                valores = df_pfza[var].dropna()
                print(f"\n--- Variable: '{var}' ---")
                print(f"  Total valores: {len(valores)}")
                print(f"  Rango: {valores.min():.2f} - {valores.max():.2f}")
                print(f"  Media: {valores.mean():.2f}")
                print(f"  Desvío estándar: {valores.std():.2f}")
                
                # Verificar valores por categoría
                if 'Categoria' in df_pfza.columns:
                    for cat in ['Primera', 'Sub 15', 'Sub 16']:
                        df_cat = df_pfza[df_pfza['Categoria'] == cat]
                        valores_cat = df_cat[var].dropna()
                        if len(valores_cat) > 0:
                            print(f"  {cat}: {len(valores_cat)} valores (rango: {valores_cat.min():.2f} - {valores_cat.max():.2f})")
            else:
                print(f"\n--- Variable: '{var}' ---")
                print(f"  NO EXISTE en la hoja 'pfza'")
    
    # 2. Verificar problema específico con 'Altura Salto'
    print("\n2. ANÁLISIS ESPECÍFICO - 'Altura Salto':")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        if 'Altura Salto' in df_pfza.columns:
            valores_altura = df_pfza['Altura Salto'].dropna()
            print(f"  Valores 'Altura Salto': {len(valores_altura)}")
            print(f"  Valores únicos: {sorted(valores_altura.unique())}")
            
            # Verificar por categoría y mes
            if 'Categoria' in df_pfza.columns and 'Fecha' in df_pfza.columns:
                for cat in ['Primera', 'Sub 15', 'Sub 16']:
                    df_cat = df_pfza[df_pfza['Categoria'] == cat].copy()
                    
                    # Filtrar por mes
                    for mes in ['2025-12', '2026-01']:
                        df_filtrado = _filtrar_mes_estricto(df_cat, mes)
                        if len(df_filtrado) > 0:
                            valores_mes = df_filtrado['Altura Salto'].dropna()
                            print(f"  {cat} - {mes}: {len(valores_mes)} valores")
                            if len(valores_mes) > 0:
                                print(f"    Valores: {sorted(valores_mes.unique())}")
                        else:
                            print(f"  {cat} - {mes}: Sin datos")
    
    # 3. Analizar problema del eje Y
    print("\n3. ANÁLISIS DEL PROBLEMA DEL EJE Y:")
    print("  Posibles causas:")
    print("  a) El eje Y muestra 'Cambio vs Pre-test' pero los valores pueden estar mal calculados")
    print("  b) Los rangos del eje Y pueden ser demasiado grandes o pequeños")
    print("  c) Los valores de cambio pueden ser cero o muy pequeños")
    
    # Simular cálculo de cambios para una variable
    print("\n4. SIMULACIÓN DE CÁLCULO DE CAMBIOS:")
    
    categoria = 'Primera'
    variable = 'Altura Salto'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
        
        pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
        post_cat = _filtrar_mes_estricto(df_cat, mes_post)
        
        print(f"  Categoría: {categoria}")
        print(f"  Variable: {variable}")
        print(f"  Pre ({mes_pre}): {len(pre_cat)} registros")
        print(f"  Post ({mes_post}): {len(post_cat)} registros")
        
        if len(pre_cat) > 0 and len(post_cat) > 0:
            print(f"\n  Valores Pre:")
            for _, row in pre_cat.iterrows():
                print(f"    {row['Apellido']}: {row[variable]:.2f}")
            
            print(f"\n  Valores Post:")
            for _, row in post_cat.iterrows():
                print(f"    {row['Apellido']}: {row[variable]:.2f}")
            
            # Calcular cambios
            print(f"\n  Cambios calculados:")
            for _, row_pre in pre_cat.iterrows():
                apellido = row_pre['Apellido']
                pre_val = row_pre[variable]
                
                # Buscar mismo jugador en post
                row_post = post_cat[post_cat['Apellido'] == apellido]
                if len(row_post) > 0:
                    post_val = row_post.iloc[0][variable]
                    cambio = post_val - pre_val
                    print(f"    {apellido}: {post_val:.2f} - {pre_val:.2f} = {cambio:+.2f}")
                else:
                    print(f"    {apellido}: No hay datos post")
    
    # 5. Verificar configuración del eje Y en el código
    print("\n5. VERIFICACIÓN DE CONFIGURACIÓN DEL EJE Y:")
    print("  El código actual usa:")
    print("  - yaxis=dict(title='Cambio vs Pre-test', range=y_range)")
    print("  - y_range se calcula como: [-y_max_abs, y_max_abs]")
    print("  - y_max_abs = max(abs(min(todos_cambio)), abs(max(todos_cambio)), 6 * SWC) * 1.3")
    print("  - Si los cambios son muy pequeños, el eje Y puede verse mal")

if __name__ == "__main__":
    analizar_problemas_eje_y()
