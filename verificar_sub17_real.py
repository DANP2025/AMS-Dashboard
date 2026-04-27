import pandas as pd
from data_loader import load_data

def verificar_sub17_real():
    """Verificar los datos reales de 'sub  17' (con dos espacios)."""
    print("=== VERIFICACIÓN REAL - 'sub  17' (CON DOS ESPACIOS) ===\n")
    
    # Cargar directamente el Excel
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
        print(f"Hoja 'Plat de fuerza': {df_fuerza.shape}")
        
        # Buscar la categoría con el nombre exacto del Excel
        categoria_excel = 'sub  17'  # con dos espacios
        df_sub17_excel = df_fuerza[df_fuerza['Categoria'] == categoria_excel].copy()
        print(f"\nRegistros '{categoria_excel}': {len(df_sub17_excel)}")
        
        if len(df_sub17_excel) > 0:
            print("\nDatos completos de 'sub  17':")
            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']
            print(df_sub17_excel[cols_mostrar].to_string())
            
            # Verificar fechas específicas
            print(f"\nFechas en '{categoria_excel}':")
            fechas_unicas = df_sub17_excel['Fecha'].dropna().unique()
            
            for fecha in sorted(fechas_unicas):
                fecha_dt = pd.to_datetime(fecha)
                periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                count = len(df_sub17_excel[df_sub17_excel['Fecha'] == fecha])
                print(f"  {fecha} -> {periodo}: {count} registros")
                
                # Verificar específicamente diciembre 2025
                if fecha_dt.year == 2025 and fecha_dt.month == 12:
                    print(f"  ¡DATOS ENCONTRADOS PARA 2025-12!")
                    df_dic_2025 = df_sub17_excel[df_sub17_excel['Fecha'] == fecha]
                    print(f"  Variables de fuerza:")
                    vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
                    for var in vars_fuerza:
                        if var in df_dic_2025.columns:
                            valores = df_dic_2025[var].dropna()
                            if len(valores) > 0:
                                print(f"    {var}: {len(valores)} valores (rango: {valores.min():.2f} - {valores.max():.2f})")
                    
                    print(f"\n  Datos completos para 2025-12:")
                    print(df_dic_2025[cols_mostrar].to_string())
        else:
            print(f"No hay registros para '{categoria_excel}'")
        
        # Verificar otras categorías que podrían ser 'Sub 17'
        print(f"\n=== OTRAS CATEGORÍAS SIMILARES ===")
        todas_categorias = df_fuerza['Categoria'].dropna().unique()
        for cat in sorted(todas_categorias):
            if '17' in str(cat):
                df_cat = df_fuerza[df_fuerza['Categoria'] == cat].copy()
                print(f"\nCategoría '{cat}': {len(df_cat)} registros")
                
                if len(df_cat) > 0:
                    fechas_unicas = df_cat['Fecha'].dropna().unique()
                    for fecha in sorted(fechas_unicas):
                        fecha_dt = pd.to_datetime(fecha)
                        if fecha_dt.year == 2025 and fecha_dt.month == 12:
                            print(f"  ¡Datos en 2025-12 para '{cat}'!")
                            df_dic = df_cat[df_cat['Fecha'] == fecha]
                            print(df_dic[cols_mostrar].to_string())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_sub17_real()
