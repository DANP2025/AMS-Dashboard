import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto

def test_final_sub17_corregido():
    """Test final para verificar que 'Sub 17' funcione correctamente."""
    print("=== TEST FINAL - SUB 17 CORREGIDO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar categorías disponibles
    print("1. CATEGORÍAS DISPONIBLES:")
    categorias = get_categorias(data)
    print(f"   Lista: {categorias}")
    
    # Buscar 'Sub 17' o variaciones
    sub17_variations = [cat for cat in categorias if '17' in str(cat)]
    print(f"   Variaciones con '17': {sub17_variations}")
    
    # 2. Verificar datos en hoja pfza
    print("\n2. VERIFICACIÓN DE DATOS EN HOJA PFZA:")
    if 'pfza' in data:
        df_pfza = data['pfza']
        print(f"   Total registros: {len(df_pfza)}")
        
        # Verificar categorías en pfza
        cats_pfza = df_pfza['Categoria'].dropna().unique()
        print(f"   Categorías en pfza: {sorted(cats_pfza)}")
        
        # Buscar 'Sub 17' o variaciones
        sub17_pfza = [cat for cat in cats_pfza if '17' in str(cat)]
        print(f"   Variaciones con '17' en pfza: {sub17_pfza}")
        
        # Para cada variación, verificar datos
        for cat in sub17_pfza:
            print(f"\n   --- Categoría: '{cat}' ---")
            df_cat = df_pfza[df_pfza['Categoria'] == cat].copy()
            print(f"   Registros: {len(df_cat)}")
            
            if len(df_cat) > 0:
                # Verificar fechas
                if 'Fecha' in df_cat.columns:
                    fechas_unicas = df_cat['Fecha'].dropna().unique()
                    print(f"   Fechas: {sorted(fechas_unicas)}")
                    
                    # Verificar cada mes
                    for fecha in sorted(fechas_unicas):
                        fecha_dt = pd.to_datetime(fecha)
                        mes_str = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                        count = len(df_cat[df_cat['Fecha'] == fecha])
                        print(f"     {mes_str}: {count} registros")
                        
                        # Verificar específicamente 2025-12
                        if fecha_dt.year == 2025 and fecha_dt.month == 12:
                            print(f"     ¡DATOS ENCONTRADOS PARA 2025-12!")
                            df_dic = df_cat[df_cat['Fecha'] == fecha]
                            vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
                            print(f"     Variables de fuerza:")
                            for var in vars_fuerza:
                                if var in df_dic.columns:
                                    valores = df_dic[var].dropna()
                                    if len(valores) > 0:
                                        print(f"       {var}: {len(valores)} valores (rango: {valores.min():.2f} - {valores.max():.2f})")
                            
                            print(f"     Datos completos:")
                            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']
                            print(df_dic[cols_mostrar].to_string())
                    
                    # Probar filtrado estricto
                    print(f"\n   Prueba de filtrado estricto:")
                    for mes in ['2025-12', '2026-01']:
                        df_filtrado = _filtrar_mes_estricto(df_cat, mes)
                        print(f"     {mes}: {len(df_filtrado)} registros")
                        
                        if len(df_filtrado) > 0:
                            print(f"     ✓ FILTRADO EXITOSO para {mes}")
                        else:
                            print(f"     ✗ Sin datos para {mes}")
    
    # 3. Verificación final
    print("\n3. VERIFICACIÓN FINAL:")
    print("   El problema estaba en que el Excel tenía 'sub  17' (con espacios)")
    print("   pero el sistema lo convertía a 'Sub 17' y no encontraba los datos.")
    print("   Ahora el data_loader mantiene los nombres originales.")
    
    # 4. Verificar si hay datos en 2025-12
    print("\n4. CONCLUSIÓN SOBRE DATOS 2025-12:")
    
    # Verificar directamente si hay datos en 2025-12
    hay_datos_2025_12 = False
    if 'pfza' in data:
        df_pfza = data['pfza']
        for cat in sub17_pfza:
            df_cat = df_pfza[df_pfza['Categoria'] == cat].copy()
            
            if 'Fecha' in df_cat.columns:
                df_cat['Fecha'] = pd.to_datetime(df_cat['Fecha'], errors='coerce')
                df_2025_12 = df_cat[(df_cat['Fecha'].dt.year == 2025) & (df_cat['Fecha'].dt.month == 12)]
                
                if len(df_2025_12) > 0:
                    hay_datos_2025_12 = True
                    print(f"   ✓ HAY DATOS para '{cat}' en 2025-12: {len(df_2025_12)} registros")
    
    if hay_datos_2025_12:
        print("   ✓ El error 'Sin datos Pre (2025-12) para Sub 17' debería desaparecer")
    else:
        print("   ✗ Realmente no hay datos en 2025-12 para 'Sub 17'")
        print("   ✗ El mensaje de error es correcto")

def get_categorias(data):
    """Función copiada de data_loader."""
    cats = data['base']['Categoria'].dropna().unique().tolist()
    return sorted(cats)

if __name__ == "__main__":
    test_final_sub17_corregido()
