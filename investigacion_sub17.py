import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto

def investigacion_sub17():
    """Investigación profunda para 'Sub 17' en 2025-12."""
    print("=== INVESTIGACIÓN PROFUNDA - SUB 17 EN 2025-12 ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificación directa del Excel
    print("1. VERIFICACIÓN DIRECTA DEL EXCEL:")
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        # Cargar directamente la hoja 'Plat de fuerza'
        df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
        print(f"   Hoja 'Plat de fuerza': {df_fuerza.shape}")
        
        # Filtrar por 'Sub 17'
        df_sub17 = df_fuerza[df_fuerza['Categoria'] == 'Sub 17'].copy()
        print(f"   Registros 'Sub 17': {len(df_sub17)}")
        
        if len(df_sub17) > 0:
            print("\n   Datos completos de 'Sub 17':")
            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']
            print(df_sub17[cols_mostrar].to_string())
            
            # Verificar fechas específicas
            print(f"\n   Fechas en 'Sub 17':")
            fechas_unicas = df_sub17['Fecha'].dropna().unique()
            for fecha in sorted(fechas_unicas):
                count = len(df_sub17[df_sub17['Fecha'] == fecha])
                print(f"     {fecha}: {count} registros")
                
                # Verificar específicamente diciembre 2025
                if pd.to_datetime(fecha).year == 2025 and pd.to_datetime(fecha).month == 12:
                    print(f"     ¡DATOS ENCONTRADOS PARA 2025-12!")
                    df_dic_2025 = df_sub17[df_sub17['Fecha'] == fecha]
                    print(f"     Variables de fuerza:")
                    vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
                    for var in vars_fuerza:
                        if var in df_dic_2025.columns:
                            valores = df_dic_2025[var].dropna()
                            if len(valores) > 0:
                                print(f"       {var}: {len(valores)} valores")
        else:
            print("   No hay registros para 'Sub 17'")
            
    except Exception as e:
        print(f"   Error cargando Excel: {e}")
    
    # 2. Verificación a través del data_loader
    print("\n2. VERIFICACIÓN A TRAVÉS DE DATA_LOADER:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        print(f"   Hoja 'pfza' desde data_loader: {df_pfza.shape}")
        
        df_sub17_loader = df_pfza[df_pfza['Categoria'] == 'Sub 17'].copy()
        print(f"   Registros 'Sub 17' desde loader: {len(df_sub17_loader)}")
        
        if len(df_sub17_loader) > 0:
            print("\n   Datos desde loader:")
            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']
            print(df_sub17_loader[cols_mostrar].to_string())
    
    # 3. Verificación con _filtrar_mes_estricto
    print("\n3. VERIFICACIÓN CON _filtrar_mes_estricto:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_sub17 = df_pfza[df_pfza['Categoria'] == 'Sub 17'].copy()
        
        print(f"   DataFrame 'Sub 17': {len(df_sub17)} registros")
        
        # Aplicar filtro estricto
        df_filtrado = _filtrar_mes_estricto(df_sub17, '2025-12')
        print(f"   Resultado _filtrar_mes_estricto: {len(df_filtrado)} registros")
        
        if len(df_filtrado) > 0:
            print("   ¡FILTRADO EXITOSO!")
            print(df_filtrado[['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']].to_string())
        else:
            print("   FILTRADO FALLIDO - Investigando causa...")
            
            # Depuración detallada
            print("\n   Depuración del filtrado:")
            if 'Fecha' in df_sub17.columns:
                try:
                    df_sub17['Fecha'] = pd.to_datetime(df_sub17['Fecha'], errors='coerce')
                    periodos = df_sub17['Fecha'].dt.to_period('M').astype(str)
                    print(f"   Períodos en 'Sub 17': {periodos.dropna().unique()}")
                    
                    mask_2025_12 = periodos == '2025-12'
                    print(f"   Registros con período 2025-12: {mask_2025_12.sum()}")
                    
                    if mask_2025_12.sum() > 0:
                        print("   ¡Hay datos pero el filtro falló!")
                        df_manual = df_sub17[mask_2025_12]
                        print(df_manual[['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']].to_string())
                    else:
                        print("   Realmente no hay datos en 2025-12 según el filtrado")
                        
                        # Verificar fechas individuales
                        print("\n   Fechas individuales:")
                        for fecha in df_sub17['Fecha'].dropna().unique():
                            fecha_dt = pd.to_datetime(fecha)
                            periodo = fecha_dt.to_period('M').astype(str)
                            print(f"     {fecha_dt} -> {periodo}")
                            
                except Exception as e:
                    print(f"   Error en depuración: {e}")
    
    # 4. Verificar si hay problema con el callback o mensaje de error
    print("\n4. VERIFICACIÓN DE MENSAJE DE ERROR:")
    print("   El mensaje aparece en el callback 'actualizar_contenido'")
    print("   Necesito verificar si el error viene de 'crear_squad_swc' o 'crear_individual_swc'")

if __name__ == "__main__":
    investigacion_sub17()
