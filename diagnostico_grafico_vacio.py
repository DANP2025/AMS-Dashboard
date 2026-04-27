import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto, _corregir_altura_salto

def diagnostico_grafico_vacio():
    """Diagnóstico rápido para identificar por qué no hay datos en el gráfico."""
    print("=== DIAGNÓSTICO - GRÁFICO VACÍO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar estado actual del sistema
    print("1. ESTADO ACTUAL DEL SISTEMA:")
    print("   Según la imagen, el gráfico no muestra datos")
    print("   Necesito verificar las posibles causas:")
    
    # 2. Verificar variables y categorías disponibles
    print(f"\n2. VARIABLES Y CATEGORÍAS DISPONIBLES:")
    
    categorias = get_categorias(data)
    print(f"   Categorías: {categorias}")
    
    # Variables disponibles por hoja
    if 'rendimiento' in data:
        vars_rend = [col for col in data['rendimiento'].columns 
                    if col not in ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Edad decimal', 'Peso', '30-15 IFT']]
        print(f"   Variables rendimiento: {vars_rend}")
    
    if 'pfza' in data:
        vars_pfza = [col for col in data['pfza'].columns 
                    if col not in ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Test', 'Subtipo', 'Total', 'Pierna Izquierda', 'Pierna Derecha', 'Asimetria %']]
        print(f"   Variables pfza: {vars_pfza}")
    
    # 3. Simular el proceso completo con valores típicos
    print(f"\n3. SIMULACIÓN DEL PROCESO COMPLETO:")
    
    # Valores típicos que podrían estar seleccionados
    categoria_test = 'Primera'
    variable_test = 'Pmax'  # o 'Fuerza'
    mes_pre_test = '2025-12'
    mes_post_test = '2026-01'
    
    print(f"   Probando con: {categoria_test} / {variable_test} / {mes_pre_test} > {mes_post_test}")
    
    # Mapeo inteligente de variables
    variable_mapping = {
        'Pmax': ('pfza', 'Potencia Pico'),
        'Fuerza': ('pfza', 'Fuerza'),
        'Altura Salto': ('pfza', 'Altura Salto'),
        'VO2 max': ('rendimiento', 'VO2 max'),
        'Vmax': ('rendimiento', 'Vmax'),
        'F0': ('rendimiento', 'F0'),
        'V0': ('rendimiento', 'V0'),
        'RF': ('rendimiento', 'RF'),
        'DRF': ('rendimiento', 'DRF'),
    }
    
    if variable_test in variable_mapping:
        sheet, variable_actual = variable_mapping[variable_test]
        print(f"   Variable mapeada: {variable_actual} en hoja '{sheet}'")
    else:
        print(f"   Variable no mapeada: {variable_test}")
        return
    
    df = data[sheet]
    
    # 4. Verificar datos por categoría y mes
    print(f"\n4. VERIFICACIÓN DE DATOS:")
    
    df_cat = df[df['Categoria'] == categoria_test].copy()
    print(f"   Registros totales '{categoria_test}': {len(df_cat)}")
    
    pre_cat = _filtrar_mes_estricto(df_cat, mes_pre_test)
    post_cat = _filtrar_mes_estricto(df_cat, mes_post_test)
    
    print(f"   Registros Pre ({mes_pre_test}): {len(pre_cat)}")
    print(f"   Registros Post ({mes_post_test}): {len(post_cat)}")
    
    if len(pre_cat) == 0:
        print(f"   ¡PROBLEMA! No hay datos Pre para {mes_pre_test}")
        print(f"   Posibles causas:")
        print(f"   - La fecha {mes_pre_test} no existe en los datos")
        print(f"   - La categoría '{categoria_test}' no tiene datos en esa fecha")
        print(f"   - Error en el filtrado de fechas")
        
        # Verificar qué fechas sí existen
        if 'Fecha' in df_cat.columns:
            fechas = df_cat['Fecha'].dropna().unique()
            periodos = []
            for fecha in fechas:
                fecha_dt = pd.to_datetime(fecha)
                periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                periodos.append(periodo)
            periodos_unicos = sorted(set(periodos))
            print(f"   Fechas disponibles para '{categoria_test}': {periodos_unicos}")
    
    if len(post_cat) == 0:
        print(f"   ¡PROBLEMA! No hay datos Post para {mes_post_test}")
        print(f"   Posibles causas:")
        print(f"   - La fecha {mes_post_test} no existe en los datos")
        print(f"   - La categoría '{categoria_test}' no tiene datos en esa fecha")
        print(f"   - Error en el filtrado de fechas")
    
    # 5. Verificar valores de la variable
    if len(pre_cat) > 0 and len(post_cat) > 0:
        print(f"\n5. VERIFICACIÓN DE VALORES:")
        
        pre_vals = pre_cat[variable_actual].dropna()
        post_vals = post_cat[variable_actual].dropna()
        
        print(f"   Valores Pre ({variable_actual}): {len(pre_vals)}")
        if len(pre_vals) > 0:
            print(f"     Rango: {pre_vals.min():.2f} - {pre_vals.max():.2f}")
        
        print(f"   Valores Post ({variable_actual}): {len(post_vals)}")
        if len(post_vals) > 0:
            print(f"     Rango: {post_vals.min():.2f} - {post_vals.max():.2f}")
        
        if len(pre_vals) < 2:
            print(f"   ¡PROBLEMA! Menos de 2 valores Pre (necesario para SD)")
        
        # 6. Simular cálculo de cambios
        if len(pre_vals) >= 2 and len(post_vals) >= 2:
            print(f"\n6. SIMULACIÓN DE CÁLCULO DE CAMBIOS:")
            
            sd_grupo = float(pre_vals.std(ddof=1))
            print(f"   SD grupo: {sd_grupo:.2f}")
            
            if sd_grupo == 0:
                print(f"   ¡PROBLEMA! SD = 0 (todos los valores son idénticos)")
            else:
                SWC = 0.2 * sd_grupo
                print(f"   SWC: {SWC:.2f}")
                
                # Calcular cambios
                cambios = []
                for _, row_pre in pre_cat.iterrows():
                    apellido = row_pre['Apellido']
                    pre_val = row_pre[variable_actual]
                    
                    if pd.notna(pre_val):
                        match_post = post_cat[post_cat['Apellido'].str.strip().str.lower() == apellido.strip().lower()]
                        if not match_post.empty:
                            post_val = match_post.iloc[0][variable_actual]
                            if pd.notna(post_val):
                                cambio = post_val - pre_val
                                cambios.append(cambio)
                                print(f"     {apellido}: {post_val:.2f} - {pre_val:.2f} = {cambio:+.2f}")
                
                if len(cambios) == 0:
                    print(f"   ¡PROBLEMA! No hay cambios calculados")
                    print(f"   Posibles causas:")
                    print(f"   - No hay jugadores comunes entre Pre y Post")
                    print(f"   - Problema en la coincidencia de apellidos")
                else:
                    print(f"   Cambios calculados: {len(cambios)}")
                    print(f"   Rango: {min(cambios):+.2f} a {max(cambios):+.2f}")
                    print(f"   RESULTADO: El gráfico debería mostrar {len(cambios)} puntos")
    
    # 7. Verificar problemas comunes
    print(f"\n7. PROBLEMAS COMUNES IDENTIFICADOS:")
    print("   a) Fechas incorrectas en dropdowns")
    print("   b) Categoría sin datos en las fechas seleccionadas")
    print("   c) Variable sin valores válidos")
    print("   d) SD = 0 (valores idénticos)")
    print("   e) No hay jugadores comunes entre meses")
    print("   f) Error en el mapeo de variables")

def get_categorias(data):
    cats = data['base']['Categoria'].dropna().unique().tolist()
    return sorted(cats)

if __name__ == "__main__":
    diagnostico_grafico_vacio()
