import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto, _corregir_altura_salto

def analisis_escala_will_hopkins():
    """Análisis exhaustivo de la escala del eje Y según concepto de Will Hopkins."""
    print("=== ANÁLISIS ESCALA WILL HOPKINS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar el concepto de Will Hopkins
    print("1. CONCEPTO DE WILL HOPKINS:")
    print("   - SWC (Smallest Worthwhile Change) = 0.2 x SD del grupo")
    print("   - Las zonas del gráfico deberían basarse en múltiplos de SWC")
    print("   - Eje Y debería mostrar cambios en unidades de SD")
    
    # 2. Analizar variables problemáticas
    print(f"\n2. ANÁLISIS DE VARIABLES PROBLEMÁTICAS:")
    
    variables_analizar = [
        ('VO2 max', 'rendimiento'),
        ('Pmax', 'rendimiento'), 
        ('Potencia Pico', 'pfza'),
        ('Fuerza IMTP', 'pfza'),
        ('Altura Salto', 'pfza')
    ]
    
    categoria = 'Primera'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    for variable, hoja_nombre in variables_analizar:
        print(f"\n   --- Variable: {variable} (hoja: {hoja_nombre}) ---")
        
        if hoja_nombre not in data:
            print(f"   ERROR: Hoja '{hoja_nombre}' no encontrada")
            continue
        
        df = data[hoja_nombre]
        
        # Verificar si la variable existe
        if variable not in df.columns:
            print(f"   ERROR: Variable '{variable}' no encontrada en hoja '{hoja_nombre}'")
            print(f"   Columnas disponibles: {[col for col in df.columns if col not in ['DNI', 'Apellido', 'Fecha', 'Categoria']]}")
            continue
        
        # Filtrar por categoría y mes
        df_cat = df[df['Categoria'] == categoria].copy()
        pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
        post_cat = _filtrar_mes_estricto(df_cat, mes_post)
        
        print(f"   Registros Pre: {len(pre_cat)}")
        print(f"   Registros Post: {len(post_cat)}")
        
        if len(pre_cat) < 2:
            print(f"   PROBLEMA: Menos de 2 datos Pre para calcular SD")
            continue
        
        if len(post_cat) < 2:
            print(f"   PROBLEMA: Menos de 2 datos Post")
            continue
        
        # Calcular valores según Will Hopkins
        pre_vals = pre_cat[variable].dropna()
        
        if len(pre_vals) < 2:
            print(f"   PROBLEMA: Menos de 2 valores válidos Pre")
            continue
        
        sd_grupo = float(pre_vals.std(ddof=1))
        swc = 0.2 * sd_grupo
        
        print(f"   SD grupo: {sd_grupo:.4f}")
        print(f"   SWC (0.2 x SD): {swc:.4f}")
        print(f"   Rango Pre: {pre_vals.min():.4f} - {pre_vals.max():.4f}")
        
        # Calcular cambios
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
            cambio_sd = [c / sd_grupo for c in cambios]
            print(f"   Cambios absolutos: {cambios}")
            print(f"   Cambios en SD: {[f'{c:.2f}' for c in cambio_sd]}")
            print(f"   Rango cambios: {min(cambios):.4f} a {max(cambios):.4f}")
            
            # Verificar si los cambios son extremos
            max_cambio_abs = max(abs(min(cambios)), abs(max(cambios)))
            print(f"   Máximo cambio absoluto: {max_cambio_abs:.4f}")
            
            if max_cambio_abs > 1000:
                print(f"   ¡PROBLEMA! Cambios extremadamente grandes (>1000)")
                print(f"   Esto indica que la variable necesita normalización")
            
            # Zonas según Will Hopkins
            print(f"   Zonas SWC:")
            print(f"     Trivial: < {swc:.4f} ({swc/sd_grupo:.2f} SD)")
            print(f"     Small: {swc:.4f} a {3*swc:.4f} ({0.2:.2f} a {0.6:.2f} SD)")
            print(f"     Medium: {3*swc:.4f} a {6*swc:.4f} ({0.6:.2f} a {1.2:.2f} SD)")
            print(f"     Large: > {6*swc:.4f} ({1.2:.2f}+ SD)")
        else:
            print(f"   PROBLEMA: No se pudieron calcular cambios")
    
    # 3. Verificar problema específico con Altura Salto
    print(f"\n3. PROBLEMA ESPECÍFICO - ALTURA SALTO:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        
        if 'Altura Salto' in df_pfza.columns:
            print(f"   Variable 'Altura Salto' encontrada en pfza")
            
            # Verificar datos por categoría
            for cat in ['Primera', 'Sub 15', 'Sub 16']:
                df_cat = df_pfza[df_pfza['Categoria'] == cat].copy()
                pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
                post_cat = _filtrar_mes_estricto(df_cat, mes_post)
                
                print(f"\n   --- Categoría: {cat} ---")
                print(f"   Registros Pre: {len(pre_cat)}")
                print(f"   Registros Post: {len(post_cat)}")
                
                if len(pre_cat) > 0:
                    pre_vals = pre_cat['Altura Salto'].dropna()
                    print(f"   Valores Pre: {len(pre_vals)}")
                    if len(pre_vals) > 0:
                        print(f"     Rango: {pre_vals.min():.2f} - {pre_vals.max():.2f}")
                        print(f"     Valores: {sorted(pre_vals.values)}")
                
                if len(post_cat) > 0:
                    post_vals = post_cat['Altura Salto'].dropna()
                    print(f"   Valores Post: {len(post_vals)}")
                    if len(post_vals) > 0:
                        print(f"     Rango: {post_vals.min():.2f} - {post_vals.max():.2f}")
                        print(f"     Valores: {sorted(post_vals.values)}")
                
                # Verificar coincidencias de jugadores
                if len(pre_cat) > 0 and len(post_cat) > 0:
                    jugadores_pre = set(pre_cat['Apellido'].str.strip().str.lower())
                    jugadores_post = set(post_cat['Apellido'].str.strip().str.lower())
                    jugadores_comunes = jugadores_pre & jugadores_post
                    
                    print(f"   Jugadores comunes: {jugadores_comunes}")
                    
                    if len(jugadores_comunes) == 0:
                        print(f"   ¡PROBLEMA! No hay jugadores comunes entre Pre y Post")
                    else:
                        print(f"   Jugadores con datos en ambos meses: {len(jugadores_comunes)}")
                        
                        # Verificar valores específicos por jugador
                        print(f"   Valores por jugador:")
                        for apellido in jugadores_comunes:
                            pre_row = pre_cat[pre_cat['Apellido'].str.strip().str.lower() == apellido]
                            post_row = post_cat[post_cat['Apellido'].str.strip().str.lower() == apellido]
                            
                            if not pre_row.empty and not post_row.empty:
                                pre_val = pre_row.iloc[0]['Altura Salto']
                                post_val = post_row.iloc[0]['Altura Salto']
                                print(f"     {apellido}: {pre_val:.2f} -> {post_val:.2f}")
        else:
            print(f"   ERROR: 'Altura Salto' no encontrada en pfza")
    
    # 4. Identificar problemas de nombres
    print(f"\n4. VERIFICACIÓN DE NOMBRES:")
    
    # Variables en rendimiento
    if 'rendimiento' in data:
        vars_rend = [col for col in data['rendimiento'].columns 
                    if col not in ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Edad decimal', 'Peso', '30-15 IFT']]
        print(f"   Variables en rendimiento: {vars_rend}")
    
    # Variables en pfza
    if 'pfza' in data:
        vars_pfza = [col for col in data['pfza'].columns 
                    if col not in ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Test', 'Subtipo', 'Total', 'Pierna Izquierda', 'Pierna Derecha', 'Asimetria %']]
        print(f"   Variables en pfza: {vars_pfza}")
    
    # 5. Recomendaciones
    print(f"\n5. RECOMENDACIONES PARA CORRECCIÓN:")
    print("   a) Normalizar variables con valores extremos (-1500 a 1500)")
    print("   b) Usar escala Y basada en SD (unidades de cambio estandarizado)")
    print("   c) Implementar corrección de datos inconsistentes")
    print("   d) Mejorar detección de nombres de variables")
    print("   e) Verificar mapeo de variables entre hojas")

if __name__ == "__main__":
    analisis_escala_will_hopkins()
